import importlib.util
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('controlla', Path(__file__).resolve().parents[1]/'controlla.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

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
        # Il candidato cancellato è oltre il limite ma resta nell'indice dei rinomini.
        self.assertEqual(out['items'][0]['possible_rename_from']['path'],'old.md')
        self.assertEqual(m.pending(self.config,prefix='z.md')['matched'],1)

    def test_exclusion_patterns_ignore_case(self):
        self.config['exclude_paths']=['Out/*']; self.config['exclude_dirs'].append('Cache'); self.scan()
        self.put('out/x.md','x'); self.put('sub/cache/y.md','y'); self.put('outside.md','o'); self.scan()
        self.assertEqual({r['path'] for r in self.items()},{'out','sub','outside.md'})

    def test_links_and_junctions_are_not_followed(self):
        target=self.base/'target'; target.mkdir(); (target/'inside.md').write_text('x',encoding='utf-8')
        self.scan()
        try:
            if os.name=='nt':
                import _winapi; _winapi.CreateJunction(str(target),str(self.root/'link'))
            else:
                os.symlink(target,self.root/'link')
        except OSError as exc:
            self.skipTest(f'link non creabile: {exc}')
        result=self.scan(); self.assertEqual(result[0]['errors'],[]); self.assertEqual(self.items(),[])

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
        self.put('AGENTS.md','[Mappa](MAPPA.md)'); self.put('CLAUDE.md','@AGENTS.md')
        self.put('MAPPA.md','[Nota](<note con spazi.md#perché>)')
        self.put('MANUTENZIONE.md','# Manutenzione'); self.put('note con spazi.md','# Perché')
        self.assertEqual(m.links(self.config)['issues'],[])
        self.put('note con spazi.md','# Altro')
        self.assertEqual(m.links(self.config)['issues'][0]['error'],'anchor')

if __name__=='__main__': unittest.main()
