import importlib.util
from contextlib import closing, contextmanager
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import types
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('controlla', Path(__file__).resolve().parents[1]/'controlla.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def offline(path):
    # Simula un file solo nel cloud con l'attributo Windows offline.
    if os.name!='nt': raise unittest.SkipTest('attributi Windows')
    import ctypes; k=ctypes.windll.kernel32
    if not k.SetFileAttributesW(str(path),k.GetFileAttributesW(str(path))|0x1000):
        raise unittest.SkipTest('attributo offline non impostabile')

def never(*args, **kwargs): raise AssertionError('file letto: lo avrebbe scaricato dal cloud')

def junction(target, link):
    try:
        if os.name=='nt':
            import _winapi; _winapi.CreateJunction(str(target),str(link))
        else:
            os.symlink(target,link)
    except OSError as exc:
        raise unittest.SkipTest(f'link non creabile: {exc}')

class DetectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base/'files'; self.root.mkdir()
        self.config = {'database': str(self.base/'state.sqlite'), 'desktop': str(self.root),
                       'roots': [{'id': 'test', 'path': str(self.root)}],
                       'exclude_dirs': ['node_modules'], 'exclude_files': ['.env']}
    def scan(self, full=False): return m.scan(self.config, full=full)
    def items(self): return m.pending(self.config)['items']
    def put(self, name, body):
        p=self.root/name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(body,encoding='utf-8'); return p

    def test_baseline_is_not_review(self):
        self.put('a.md','initial'); self.assertTrue(self.scan()[0]['baseline'])
        self.assertEqual(self.items(),[])
        with closing(sqlite3.connect(self.config['database'])) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM observed').fetchone()[0],1)
            self.assertEqual(db.execute('SELECT count(*) FROM events').fetchone()[0],0)

    def test_pending_survives_unchanged_scan(self):
        self.scan(); self.put('a.md','new'); self.scan(); first=self.items()
        self.scan(); self.assertEqual(self.items(),first)

    def test_modified_and_deleted(self):
        p=self.put('a.md','old'); self.scan(); self.put('a.md','longer'); self.scan()
        first=self.items()[0]['id']; p.unlink(); self.scan()
        items=self.items(); self.assertEqual(len(items),1); self.assertEqual(items[0]['kind'],'deleted')
        self.assertEqual(items[0]['superseded_events'],1)
        with self.assertRaises(ValueError): m.review(self.config,[first],'old review')

    def test_review_checks_actual_content(self):
        self.scan(); p=self.put('a.md','one'); self.scan(); event=self.items()[0]['id']
        p.write_text('two',encoding='utf-8')
        with self.assertRaises(ValueError): m.review(self.config,[event],'read earlier')
        self.assertEqual(len(self.items()),1)
        self.scan(full=True); event=self.items()[0]['id']; m.review(self.config,[event],'read current content')
        self.assertEqual(self.items(),[])

    def test_batch_review_is_atomic(self):
        self.scan(); self.put('a.md','a'); b=self.put('b.md','b'); self.scan()
        ids=[r['id'] for r in self.items()]; b.write_text('changed')
        with self.assertRaises(ValueError): m.review(self.config,ids,'test')
        self.assertEqual(len(self.items()),2)

    def test_full_scan_detects_same_size_and_timestamp(self):
        p=self.put('a.md','abc'); self.scan(); old=p.stat()
        p.write_text('xyz'); os.utime(p,ns=(old.st_atime_ns,old.st_mtime_ns))
        self.scan(); self.assertEqual(self.items(),[])
        self.scan(full=True); self.assertEqual(self.items()[0]['kind'],'modified')

    def test_metadata_only_touch_is_not_content_change(self):
        p=self.put('a.md','same'); self.scan(); info=p.stat()
        os.utime(p,ns=(info.st_atime_ns,info.st_mtime_ns+1000000000)); self.scan()
        self.assertEqual(self.items(),[])

    def test_missing_root_does_not_delete(self):
        self.put('a.md','a'); self.scan(); self.root.rename(self.base/'unavailable')
        result=self.scan(); self.assertTrue(result[0]['errors']); self.assertEqual(self.items(),[])
        with closing(sqlite3.connect(self.config['database'])) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM observed').fetchone()[0],1)

    def test_inaccessible_subtree_is_preserved(self):
        self.put('locked/a.md','a'); self.put('ok.md','ok'); self.scan()
        real=m.os.scandir
        def denied(path):
            if Path(path).name=='locked': raise PermissionError('test access denied')
            return real(path)
        with patch.object(m.os,'scandir',side_effect=denied): result=self.scan()
        self.assertTrue(result[0]['errors']); self.assertEqual(self.items(),[])

    def test_rename_is_candidate_only(self):
        p=self.put('old.md','unique'); self.scan(); p.rename(self.root/'new.md'); self.scan()
        added=next(r for r in self.items() if r['kind']=='added')
        self.assertEqual(added['possible_rename_from']['path'],'old.md')
        self.assertTrue((self.root/'new.md').exists())
        self.assertEqual(len(self.items()),2)

    def test_ambiguous_rename_is_not_suggested(self):
        p=self.put('old.md','same'); self.scan(); p.unlink()
        self.put('new1.md','same'); self.put('new2.md','same'); self.scan()
        self.assertTrue(all('possible_rename_from' not in r for r in self.items()))

    def test_limit_truncates_output_only(self):
        p=self.put('old.md','unique'); self.scan(); p.rename(self.root/'new.md'); self.put('z.md','z'); self.scan()
        out=m.pending(self.config,limit=1)
        self.assertEqual((out['total_pending'],out['matched'],len(out['items'])),(3,3,1))
        # Il candidato cancellato è fuori dal filtro ma resta nell'indice dei rinomini.
        out=m.pending(self.config,prefix='new.md')
        self.assertEqual(out['items'][0]['possible_rename_from']['path'],'old.md')
        self.assertEqual(m.pending(self.config,prefix='z.md')['matched'],1)
        with self.assertRaises(ValueError): m.pending(self.config,limit=-1)

    def test_pending_summarizes_folders_and_renames(self):
        self.put('Vecchia/a.txt','a'); self.put('Vecchia/sub/b.txt','b'); self.put('x.md','x'); self.scan()
        (self.root/'Vecchia').rename(self.root/'Nuova'); self.put('x.md','y'); self.scan()
        summary=m.pending(self.config,limit=1)['summary']
        self.assertEqual(summary['folder_renames'],[{'root':'test','from':'Vecchia','to':'Nuova','identical':2,
                                                     'changed':0,'only_from':0,'only_to':0}])
        self.assertIn({'root':'test','folder':'Vecchia/sub','deleted':2},summary['folders'])
        self.assertIn({'root':'test','folder':'','modified':1},summary['folders'])
        self.assertEqual(m.pending(self.config,prefix='x.md')['summary']['folder_renames'],[])

    def test_pending_items_carry_only_useful_fields(self):
        self.scan(); self.put('a.md','a'); self.scan()
        self.assertEqual(set(self.items()[0]),{'id','root','path','kind','created','before','after','superseded_events'})

    def test_pending_shows_newest_first(self):
        self.scan(); self.put('a.md','a'); self.scan(); self.put('b.md','b'); self.scan()
        self.assertEqual([r['path'] for r in self.items()],['b.md','a.md'])
        self.assertEqual([r['path'] for r in m.pending(self.config,limit=1)['items']],['b.md'])

    def test_depth_filter_keeps_root_level(self):
        self.scan(); self.put('top.md','t'); self.put('sub/deep.md','d'); self.scan()
        self.assertEqual({r['path'] for r in m.pending(self.config,depth=1)['items']},{'top.md','sub'})
        with self.assertRaises(ValueError): m.pending(self.config,depth=0)

    def test_review_by_prefix(self):
        self.scan(); self.put('Foto/1.jpg','1'); self.put('Foto/2.jpg','2'); self.put('x.md','x'); self.scan()
        out=m.review(self.config,[],'foto censite',prefix='Foto')
        self.assertEqual(out['reviewed'],3); self.assertEqual([r['path'] for r in self.items()],['x.md'])

    def test_prefix_accepts_windows_separators(self):
        self.scan(); self.put('Foto/Mare/1.jpg','1'); self.put('Fotografie.md','x'); self.scan()
        self.assertEqual(m.pending(self.config,prefix='Foto/')['matched'],3)
        self.assertEqual(m.pending(self.config,prefix='Foto\\Mare')['matched'],2)
        self.assertEqual(m.pending(self.config,prefix='/Foto')['matched'],3)
        if os.name=='nt': self.assertEqual(m.pending(self.config,prefix='foto/mare')['matched'],2)
        self.assertEqual(m.review(self.config,[],'foto censite',prefix='Foto\\')['reviewed'],3)
        self.assertEqual([r['path'] for r in self.items()],['Fotografie.md'])

    def test_repeated_id_is_reviewed_once(self):
        self.scan(); self.put('a.md','a'); self.scan(); event=self.items()[0]['id']
        self.assertEqual(m.review(self.config,[event,event],'letto')['reviewed'],[event])
        self.assertEqual(self.items(),[])

    def test_case_only_rename_can_be_reviewed(self):
        # Su Windows il vecchio nome trova ancora la cartella rinominata: per la cancellazione conta il nome sul disco.
        self.put('foto/a.jpg','a'); self.scan(); (self.root/'foto').rename(self.root/'Foto'); self.scan()
        ids=[r['id'] for r in self.items()]; self.assertEqual(len(ids),4)
        m.review(self.config,ids,'rinomina di sole maiuscole'); self.assertEqual(self.items(),[])

    def test_unknown_root_is_named(self):
        with self.assertRaisesRegex(ValueError,'Altra'): m.scan(self.config,['test','Altra'])
        with self.assertRaisesRegex(ValueError,'Altra'): m.pending(self.config,root='Altra')
        with self.assertRaisesRegex(ValueError,'Altra'): m.review(self.config,[],'nota',root='Altra')

    def test_events_out_of_coverage_can_be_reviewed(self):
        # Dopo un'esclusione o con una profondità minore il percorso non si osserva più: si chiude senza ricontrollo.
        self.scan(); lock=self.put('~$Relazione.docx','lock'); self.put('a/b/c.md','deep'); self.scan()
        ids=[r['id'] for r in self.items()]
        self.config['exclude_files'].append('~$*'); self.config['roots'][0]['depth']=2
        lock.unlink(); self.put('a/b/c.md','cambiato'); self.scan()
        self.assertEqual(m.review(self.config,ids,'fuori copertura')['reviewed'],ids); self.assertEqual(self.items(),[])

    def test_status_lists_root_errors(self):
        self.put('a.md','a'); self.scan(); self.root.rename(self.base/'altrove'); self.scan()
        self.assertTrue(m.status(self.config)['roots'][0]['errors'][0]['error'])

    def test_works_without_windows_stat_constants(self):
        # Fuori da Windows il modulo stat non ha le costanti IO_REPARSE_TAG_*.
        fake=types.SimpleNamespace(**{k:getattr(m.stat,k) for k in dir(m.stat) if not k.startswith('IO_REPARSE_TAG')})
        self.put('a/b.md','b')
        with patch.object(m,'stat',fake): self.assertEqual(self.scan()[0]['errors'],[])

    def test_review_needs_ids_or_filter(self):
        self.scan(); self.put('a.md','a'); self.scan(); event=self.items()[0]['id']
        for ids,prefix in (([],None),([event],'a.md')):
            with self.assertRaises(ValueError): m.review(self.config,ids,'nota',prefix=prefix)

    def test_review_by_filter_is_atomic(self):
        self.scan(); self.put('Foto/1.jpg','1'); p=self.put('Foto/2.jpg','2'); self.scan(); p.write_text('changed')
        with self.assertRaises(ValueError): m.review(self.config,[],'test',prefix='Foto')
        self.assertEqual(len(self.items()),3)

    def test_cloud_only_files_are_not_read(self):
        p=self.put('video.mp4','contenuto'); offline(p)
        with patch.object(m,'digest',side_effect=never): self.scan(); self.scan(full=True)
        self.assertEqual(self.items(),[])

    def test_dehydrated_file_is_not_a_change(self):
        p=self.put('doc.pdf','contenuto'); self.scan(); offline(p)
        with patch.object(m,'digest',side_effect=never): self.scan(full=True)
        self.assertEqual(self.items(),[])

    def test_review_does_not_download_cloud_files(self):
        self.scan(); p=self.put('nuovo.pdf','x'); offline(p)
        with patch.object(m,'digest',side_effect=never):
            self.scan(); m.review(self.config,[self.items()[0]['id']],'censito')
        self.assertEqual(self.items(),[])

    def test_cloud_files_get_no_rename_suggestion(self):
        # Senza impronta una cancellazione e un'aggiunta qualsiasi non sono un rinomino.
        a=self.put('a.pdf','uno'); offline(a); self.scan(); a.unlink()
        e=self.put('e.pdf','tutto diverso'); offline(e); self.scan()
        self.assertTrue(all('possible_rename_from' not in r for r in self.items()))

    def test_exclusion_patterns_ignore_case(self):
        self.config['exclude_paths']=['Out/*']; self.config['exclude_dirs'].append('Cache'); self.scan()
        self.put('out/x.md','x'); self.put('sub/cache/y.md','y'); self.put('outside.md','o'); self.scan()
        self.assertEqual({r['path'] for r in self.items()},{'out','sub','outside.md'})

    def test_links_and_junctions_are_not_followed(self):
        target=self.base/'target'; target.mkdir(); (target/'inside.md').write_text('x',encoding='utf-8')
        self.scan(); junction(target,self.root/'link')
        result=self.scan(); self.assertEqual(result[0]['errors'],[]); self.assertEqual(self.items(),[])

    def test_junctions_without_direntry_support(self):
        # Python 3.10 e 3.11: DirEntry non ha is_junction, eppure la junction resta fuori senza errori.
        target=self.base/'target'; target.mkdir(); self.scan(); junction(target,self.root/'link')
        real=m.os.scandir
        class Old:
            def __init__(self,e): self.name,self.path,self.is_symlink=e.name,e.path,e.is_symlink
        @contextmanager
        def old(path):
            with real(path) as listing: yield [Old(e) for e in listing]
        with patch.object(m.os,'scandir',side_effect=old): result=self.scan()
        self.assertEqual((result[0]['errors'],self.items()),([],[]))

    def test_example_config_skips_office_lock_files(self):
        example=json.loads((Path(m.__file__).parent/'config.example.json').read_text(encoding='utf-8'))
        self.config['exclude_files']=example['exclude_files']; self.scan()
        self.put('~$Relazione.docx','lock'); self.put('.~lock.Bilancio.ods#','lock'); self.put('Relazione.docx','testo')
        self.scan(); self.assertEqual([r['path'] for r in self.items()],['Relazione.docx'])

    def test_exclusions_and_hidden_instructions(self):
        self.scan(); self.put('node_modules/ignored.js','code'); self.put('.env','test')
        self.put('.claude/rules.md','instructions'); self.scan()
        names=[r['path'] for r in self.items()]
        self.assertIn('.claude/rules.md',names); self.assertNotIn('.env',names)
        self.assertFalse(any('node_modules' in s for s in names))

    def test_empty_directory_is_detected(self):
        self.scan(); (self.root/'empty').mkdir(); self.scan()
        self.assertEqual(self.items()[0]['after']['kind'],'directory')

    def test_shallow_root(self):
        self.config['roots'][0]['recursive']=False; self.scan()
        self.put('sub/deep.md','deep'); self.put('top.md','top'); self.scan()
        self.assertEqual({r['path'] for r in self.items()},{'sub','top.md'})

    def test_depth_limit(self):
        self.config['roots'][0]['depth']=2; self.scan()
        self.put('a/b/c.md','deep'); self.put('a/top.md','top'); self.put('x.md','x'); self.scan()
        self.assertEqual({r['path'] for r in self.items()},{'a','a/b','a/top.md','x.md'})

    def test_reduced_depth_is_not_deletion(self):
        self.put('a/b/c.md','deep'); self.scan(); self.config['roots'][0]['depth']=2; self.scan()
        self.assertEqual(self.items(),[])
        (self.root/'a/b/c.md').unlink(); self.scan(); self.assertEqual(self.items(),[])
        (self.root/'a/b').rmdir(); self.scan(); self.assertEqual([r['path'] for r in self.items()],['a/b'])

    def test_transaction_rolls_back_on_failure(self):
        self.put('a.md','a'); self.scan(); self.put('a.md','changed')
        self.config['roots'].append({'id':'another','path':str(self.root)})
        real=m.walk
        def fail(root,*a,**kw):
            if root['id']=='another': raise RuntimeError('test crash')
            return real(root,*a,**kw)
        with patch.object(m,'walk',side_effect=fail):
            with self.assertRaises(RuntimeError): self.scan()
        self.assertEqual(self.items(),[])
        self.scan(); self.assertEqual(len(self.items()),1)

    def test_changed_root_path_is_rejected(self):
        self.scan(); self.config['roots'][0]['path']=str(self.base)
        with self.assertRaises(ValueError): self.scan()

    def test_new_exclusion_is_not_deletion(self):
        self.put('a.md','a'); self.scan(); self.config['exclude_files'].append('a.md'); self.scan()
        self.assertEqual(self.items(),[])

    def test_links_spaces_unicode_and_anchor(self):
        self.put('AGENTS.md','[Mappa](MAPPA.md)')
        self.put('MAPPA.md','[Nota](<note con spazi.md#perché>)')
        self.put('MANUTENZIONE.md','# Manutenzione'); self.put('note con spazi.md','# Perché')
        self.assertEqual(m.links(self.config)['issues'],[])
        self.put('note con spazi.md','# Altro')
        self.assertEqual(m.links(self.config)['issues'][0]['error'],'anchor')

    def test_links_skip_archive_and_excluded(self):
        self.config['exclude_dirs'].append('Bozze')
        self.put('AGENTS.md','[Vecchio](Archivio/vecchio.md) [Bozza](Bozze/b.md)')
        self.put('MAPPA.md','# Mappa'); self.put('MANUTENZIONE.md','# Manutenzione')
        self.put('Archivio/vecchio.md','[rotto](manca.md)'); self.put('Bozze/b.md','[rotto](manca.md)')
        self.assertEqual(m.links(self.config)['issues'],[])

    def test_links_report_missing_start_pages(self):
        self.put('AGENTS.md','[Mappa](MAPPA.md)'); self.put('MAPPA.md','# Mappa')
        self.assertEqual(m.links(self.config)['issues'],
                         [{'file':str(self.root.resolve()),'target':'MANUTENZIONE.md','error':'missing'}])

    def test_links_survive_unreadable_pages_and_ignore_code(self):
        self.put('AGENTS.md','[Mappa](MAPPA.md) [Esempio](MANUTENZIONE.md#esempio)')
        (self.root/'MAPPA.md').write_bytes(b'\x81\x82 non UTF-8')
        self.put('MANUTENZIONE.md','# Manutenzione\n```powershell\n# esempio\n```\n')
        found={(Path(i['file']).name,i['error']) for i in m.links(self.config)['issues']}
        self.assertEqual(found,{('MAPPA.md','unreadable'),('AGENTS.md','anchor')})

    def test_config_paths_are_relative_to_the_file(self):
        folder=self.base/'istanza'; folder.mkdir(); path=folder/'config.json'
        path.write_text(json.dumps({'desktop':'../files','roots':[{'id':'test','path':'../files'}]}),encoding='utf-8')
        config=m.load_config(path)
        self.assertEqual((config['desktop'],config['roots'][0]['path']),(str(self.root.resolve()),)*2)
        self.assertEqual(config['database'],str(folder/'.stato/registro.sqlite'))
        # Registro in una cartella locale fuori dallo strumento, come quando Documenti è su OneDrive.
        local=self.base/'Locale'/'Scrivano'/'registro.sqlite'
        path.write_text(json.dumps({'database':str(local),'roots':[{'id':'test','path':str(self.root)}]}),encoding='utf-8')
        config=m.load_config(path); self.assertEqual(config['database'],str(local))
        m.scan(config); self.assertTrue(local.is_file())

    def test_invalid_config_is_rejected(self):
        path=self.base/'config.json'; roots=[{'id':'x','path':'.'}]
        for config in ({},[],{'roots':[{'id':'x'}]},{'roots':[{'id':'x','path':None}]},
                       {'roots':roots,'desktop':None},{'roots':roots,'database':''}):
            path.write_text(json.dumps(config),encoding='utf-8')
            with self.assertRaises(ValueError,msg=config): m.load_config(path)

if __name__=='__main__': unittest.main()
