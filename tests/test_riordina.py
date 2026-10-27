import importlib.util
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('riordina', Path(__file__).resolve().parents[1]/'src'/'riordina.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def offline(path):
    # Simula un file solo nel cloud con l'attributo Windows offline.
    if os.name!='nt': raise unittest.SkipTest('attributi Windows')
    import ctypes; k=ctypes.windll.kernel32
    if not k.SetFileAttributesW(str(path),k.GetFileAttributesW(str(path))|0x1000):
        raise unittest.SkipTest('attributo offline non impostabile')

def junction(target, link):
    try:
        if os.name=='nt':
            import _winapi; _winapi.CreateJunction(str(target),str(link))
        else:
            os.symlink(target,link)
    except OSError as exc:
        raise unittest.SkipTest(f'link non creabile: {exc}')

class Base(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name); self.root=self.base/'Desktop'; self.root.mkdir()
        self.state=self.base/'stato'; self.state.mkdir()
    def put(self, name, body='x'):
        p=self.root/name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(body,encoding='utf-8'); return p
    def plan(self, *moves, vuote=()):
        p=self.state/'piano.json'
        p.write_text(json.dumps({'radice':str(self.root),'mosse':[{'da':a,'a':b} for a,b in moves],'vuote':list(vuote)}),encoding='utf-8')
        return p
    def exists(self, name): return os.path.lexists(self.root/name)

class InventoryTests(Base):
    def test_summary(self):
        self.put('a.pdf','same'); self.put('copia di a.pdf','same'); self.put('Progetto/.git/HEAD','ref')
        self.put('Progetto/main.py','print()'); self.put('Foto/IMG_1.jpg','img'); self.put('password.txt','segreto')
        out=m.inventory(self.root); voci={v['nome']:v for v in out['voci']}
        self.assertEqual((out['totale']['file'],out['totale']['cartelle']),(5,3))
        self.assertTrue(voci['Progetto']['progetto']); self.assertEqual(voci['Progetto']['pesanti'],['.git'])
        self.assertEqual(out['esclusioni_suggerite'],['.git'])
        self.assertEqual(out['segreti'],['password.txt']); self.assertTrue(voci['password.txt']['segreto'])
        self.assertEqual(out['duplicati'],[{'byte':4,'percorsi':['a.pdf','copia di a.pdf']}])

    def test_cloud_files_are_not_read(self):
        a=self.put('a.bin','same'); b=self.put('b.bin','same'); offline(a); offline(b)
        with patch.object(m,'digest',side_effect=AssertionError('file letto')): out=m.inventory(self.root)
        self.assertEqual(out['totale']['solo_cloud'],2); self.assertEqual(out['duplicati'],[])

    def test_dataless_files_are_not_read(self):
        # macOS: i file "dataless" di iCloud si scaricherebbero leggendoli; il flag sta in st_flags.
        self.put('a.bin','same'); self.put('b.bin','same'); real=os.stat
        def dataless(path,**kw):
            info=real(path,**kw)
            return types.SimpleNamespace(st_mode=info.st_mode,st_size=info.st_size,st_mtime_ns=info.st_mtime_ns,
                                         st_flags=0x40000000)
        with patch.object(m,'DATALESS',0x40000000),patch.object(m.os,'stat',dataless),\
                patch.object(m,'digest',side_effect=AssertionError('file letto')):
            out=m.inventory(self.root)
        self.assertEqual((out['totale']['solo_cloud'],out['duplicati']),(2,[]))

    def test_keynote_is_not_a_secret(self):
        # Su Mac un .key è di solito una presentazione Keynote, cioè uno zip o un pacchetto; una chiave è testo.
        (self.root/'Tesi.key').write_bytes(b'PK\x03\x04presentazione'); self.put('server.key','-----BEGIN PRIVATE KEY-----')
        self.put('Vecchia.key/Index.apxl','pacchetto')
        out=m.inventory(self.root); voci={v['nome']:v for v in out['voci']}
        self.assertEqual(out['segreti'],['server.key']); self.assertNotIn('segreto',voci['Tesi.key'])
        self.assertTrue(voci['Vecchia.key']['pacchetto'])

    def test_packages_are_units(self):
        # Pacchetti macOS: il Finder li mostra come un documento o un'app, l'inventario non ci entra.
        self.put('Canzone.band/Media/audio.aif'); self.put('Musica/Demo.band/projectData'); self.put('Musica/nota.txt')
        out=m.inventory(self.root); voci={v['nome']:v for v in out['voci']}
        self.assertEqual(out['pacchetti'],['Canzone.band','Musica/Demo.band'])
        self.assertTrue(voci['Canzone.band']['pacchetto']); self.assertEqual(out['totale']['file'],1)

    def test_finder_metadata_is_ignored(self):
        self.put('.DS_Store','finder'); self.put('Foto/.DS_Store','finder'); self.put('Foto/a.jpg','img')
        out=m.inventory(self.root)
        self.assertEqual((out['totale']['file'],[v['nome'] for v in out['voci']],out['duplicati']),(1,['Foto'],[]))

    def test_depth_limits_descent(self):
        self.put('A/B/c.txt'); voce=m.inventory(self.root,depth=2)['voci'][0]
        self.assertEqual((voce['cartelle'],voce['file'],voce['parziale']),(1,0,True))

    def test_links_are_listed_not_followed(self):
        target=self.base/'fuori'; target.mkdir(); (target/'x.txt').write_text('x'); junction(target,self.root/'link')
        out=m.inventory(self.root)
        self.assertEqual((out['link'],out['totale']['file']),(['link'],0))

    def test_works_without_windows_stat_constants(self):
        # Fuori da Windows il modulo stat non ha le costanti IO_REPARSE_TAG_*.
        fake=types.SimpleNamespace(**{k:getattr(m.stat,k) for k in dir(m.stat) if not k.startswith('IO_REPARSE_TAG')})
        self.put('A/b.txt')
        with patch.object(m,'stat',fake): self.assertEqual(m.inventory(self.root)['totale']['file'],1)

class PlanTests(Base):
    def test_moves_and_creates_folders(self):
        self.put('fattura.pdf'); self.put('Foto mare/1.jpg')
        out,code=m.execute(self.plan(('fattura.pdf','Finanze/Bollette/fattura.pdf'),('Foto mare','Personale/Foto mare')))
        self.assertEqual((code,out['eseguite'],out['conteggio']),(0,2,{'prima':2,'dopo':2}))
        self.assertTrue(self.exists('Finanze/Bollette/fattura.pdf') and self.exists('Personale/Foto mare/1.jpg'))
        righe=[json.loads(r) for r in Path(out['giornale']).read_text(encoding='utf-8').splitlines()]
        self.assertEqual([r.get('cartella') or r['da'] for r in righe],['Finanze','Finanze/Bollette','fattura.pdf','Personale','Foto mare'])

    def test_collision_stops_everything(self):
        self.put('a.pdf'); self.put('b.pdf'); self.put('Finanze/b.pdf','altro')
        out,code=m.execute(self.plan(('a.pdf','Finanze/a.pdf'),('b.pdf','Finanze/b.pdf')))
        self.assertEqual((code,out['problemi'][0]['problema']),(1,'destinazione già occupata'))
        self.assertTrue(self.exists('a.pdf')); self.assertFalse((self.state/'piano.giornale.jsonl').exists())

    def test_invalid_paths_are_rejected(self):
        self.put('y.txt')
        for dst in ('../fuori.txt',str(self.base/'fuori.txt')):
            with self.assertRaises(ValueError): m.execute(self.plan(('y.txt',dst)))

    def test_overlapping_moves_are_rejected(self):
        self.put('A/x.txt'); self.put('y.txt')
        for moves in ([('A','A/B')],[('A','Dest/A'),('A/x.txt','Altro/x.txt')],
                      [('y.txt','Z/y.txt'),('A','Z/y.txt/A')],[('y.txt','w.txt'),('A','w.txt')]):
            out,code=m.execute(self.plan(*moves)); self.assertEqual(code,1,moves); self.assertTrue(out['problemi'])
        self.assertTrue(self.exists('A/x.txt') and self.exists('y.txt'))

    def test_case_only_rename_needs_two_plans(self):
        if not m.NOCASE: self.skipTest('il file system distingue le maiuscole: la rinomina è una mossa qualsiasi')
        self.put('foto/a.jpg')
        out,code=m.execute(self.plan(('foto','Foto')))
        self.assertEqual(code,1); self.assertIn('maiuscole',out['problemi'][0]['problema'])

    def test_accent_forms_are_the_same_name(self):
        # macOS: lo stesso nome può arrivare con gli accenti composti (NFC) o scomposti (NFD).
        self.put('a.txt'); self.put('b.txt')
        out,code=m.execute(self.plan(('a.txt','Città/a.txt'),('b.txt','Città/a.txt')),dry_run=True)
        self.assertEqual((code,out['problemi'][0]['problema']),(1,'origine o destinazione ripetuta nel piano'))

    def test_accents_and_brackets(self):
        self.put('Foto [2019] Città.jpg')
        out,code=m.execute(self.plan(('Foto [2019] Città.jpg','Personale/Foto [2019] Città.jpg')))
        self.assertEqual(code,0); self.assertTrue(self.exists('Personale/Foto [2019] Città.jpg'))

    def test_resume_after_failure(self):
        self.put('a.txt'); self.put('b.txt'); plan=self.plan(('a.txt','X/a.txt'),('b.txt','X/b.txt'))
        real=m.os.rename
        def busy(src,dst):
            if Path(src).name=='b.txt': raise PermissionError('file in uso')
            return real(src,dst)
        with patch.object(m.os,'rename',side_effect=busy): out,code=m.execute(plan)
        self.assertEqual((code,out['eseguite'],out['errore']['da']),(1,1,'b.txt'))
        out,code=m.execute(plan); self.assertEqual((code,out['gia_fatte'],out['eseguite']),(0,1,1))
        self.assertTrue(self.exists('X/a.txt') and self.exists('X/b.txt'))

    def test_lock_blocks_parallel_runs(self):
        self.put('a.txt'); (self.state/'riordina.lock').write_text('altro riordino')
        with self.assertRaises(ValueError): m.execute(self.plan(('a.txt','X/a.txt')))
        self.assertTrue(self.exists('a.txt'))

    def test_dry_run_moves_nothing(self):
        self.put('a.txt'); out,code=m.execute(self.plan(('a.txt','X/a.txt')),dry_run=True)
        self.assertEqual((code,out['da_fare']),(0,1)); self.assertTrue(self.exists('a.txt'))
        self.assertFalse((self.state/'piano.giornale.jsonl').exists())

    def test_links_are_not_moved(self):
        target=self.base/'fuori'; target.mkdir(); junction(target,self.root/'link')
        out,code=m.execute(self.plan(('link','X/link')))
        self.assertEqual((code,out['problemi'][0]['problema']),(1,'link simbolico o junction: da spostare a mano'))

    def test_paths_through_links_are_rejected(self):
        # Dietro una junction ci sono file e cartelle fuori dalla radice: niente mosse né rimozioni.
        target=self.base/'fuori'; (target/'Sotto').mkdir(parents=True); (target/'x.txt').write_text('x')
        junction(target,self.root/'link')
        out,code=m.execute(self.plan(('link/x.txt','X/x.txt'),vuote=['link/Sotto']))
        self.assertEqual((code,[p['problema'] for p in out['problemi']]),
                         (1,['link simbolico o junction: da spostare a mano','non è una cartella da svuotare']))
        self.assertTrue((target/'x.txt').exists() and (target/'Sotto').exists())

    def test_missing_source_is_done_only_if_noted(self):
        # Senza giornale, origine assente e destinazione occupata sono un errore del piano, non una mossa fatta.
        self.put('Finanze/fattura.pdf')
        out,code=m.execute(self.plan(('fattura.pdf','Finanze/fattura.pdf')),dry_run=True)
        self.assertEqual((code,out['gia_fatte'],out['problemi'][0]['problema']),
                         (1,0,'origine mancante e destinazione già occupata'))

    def test_undo_restores_and_removes_created_folders(self):
        self.put('a.txt'); self.put('Esistente/b.txt')
        plan=self.plan(('a.txt','Nuova/Sotto/a.txt'),('Esistente','Nuova/Esistente'))
        m.execute(plan); out,code=m.undo(plan)
        self.assertEqual((code,out['ripristinate'],out['cartelle_rimosse']),(0,2,2))
        self.assertTrue(self.exists('a.txt') and self.exists('Esistente/b.txt')); self.assertFalse(self.exists('Nuova'))
        self.assertFalse((self.state/'piano.giornale.jsonl').exists())

    def test_undo_after_resume(self):
        self.put('a.txt'); self.put('b.txt'); plan=self.plan(('a.txt','X/a.txt'),('b.txt','X/b.txt'))
        real=m.os.rename
        def busy(src,dst):
            if Path(src).name=='b.txt': raise PermissionError('file in uso')
            return real(src,dst)
        with patch.object(m.os,'rename',side_effect=busy): m.execute(plan)
        m.execute(plan); out,code=m.undo(plan)
        self.assertEqual((code,out['ripristinate'],out['gia_al_posto']),(0,2,1))
        self.assertTrue(self.exists('a.txt') and self.exists('b.txt')); self.assertFalse(self.exists('X'))

    def test_emptied_containers_are_removed(self):
        self.put('Nuova cartella/a.txt'); self.put('Varie/b.txt'); self.put('Varie/c.txt')
        out,code=m.execute(self.plan(('Nuova cartella/a.txt','X/a.txt'),('Varie/b.txt','X/b.txt'),vuote=['Nuova cartella','Varie']))
        self.assertEqual((code,out['cartelle_rimosse'],out['cartelle_rimaste']),(0,['Nuova cartella'],['Varie']))
        self.assertFalse(self.exists('Nuova cartella')); self.assertTrue(self.exists('Varie/c.txt'))

    def test_undo_recreates_removed_containers(self):
        self.put('Nuova cartella/a.txt'); plan=self.plan(('Nuova cartella/a.txt','X/a.txt'),vuote=['Nuova cartella'])
        m.execute(plan); out,code=m.undo(plan)
        self.assertEqual((code,out['cartelle_ricreate'],out['ripristinate']),(0,1,1))
        self.assertTrue(self.exists('Nuova cartella/a.txt')); self.assertFalse(self.exists('X'))

    def test_containers_with_only_metadata_are_removed(self):
        # Il Finder lascia un .DS_Store in ogni cartella aperta: non basta a tenerla sul Desktop.
        self.put('Nuova cartella/a.txt'); self.put('Nuova cartella/.DS_Store','finder')
        self.put('Varie/b.txt'); self.put('Varie/.DS_Store','finder')
        plan=self.plan(('Nuova cartella/a.txt','X/a.txt'),vuote=['Nuova cartella','Varie'])
        out,code=m.execute(plan)
        self.assertEqual((code,out['cartelle_rimosse'],out['cartelle_rimaste']),(0,['Nuova cartella'],['Varie']))
        self.assertEqual(out['conteggio']['prima'],out['conteggio']['dopo']); self.assertFalse(self.exists('Nuova cartella'))
        giornale=(self.state/'piano.giornale.jsonl').read_text(encoding='utf-8').splitlines()
        self.assertEqual(json.loads(giornale[-1])['metadati'],['.DS_Store'])
        out,code=m.undo(plan)
        self.assertEqual((code,out['cartelle_ricreate']),(0,1)); self.assertTrue(self.exists('Nuova cartella/a.txt'))

    def test_metadata_in_use_keeps_the_container(self):
        self.put('Vecchia/a.txt'); self.put('Vecchia/Thumbs.db','anteprime'); real=m.os.unlink
        def busy(path):
            if Path(path).name=='Thumbs.db': raise PermissionError('in uso')
            return real(path)
        with patch.object(m.os,'unlink',side_effect=busy):
            out,code=m.execute(self.plan(('Vecchia/a.txt','X/a.txt'),vuote=['Vecchia']))
        self.assertEqual((code,out['cartelle_rimaste'],out['errore']),(0,['Vecchia'],None))

    def test_undo_removes_created_folders_with_metadata(self):
        self.put('a.txt'); plan=self.plan(('a.txt','Nuova/a.txt')); m.execute(plan)
        (self.root/'Nuova/.DS_Store').write_text('finder')
        out,code=m.undo(plan)
        self.assertEqual((code,out['cartelle_rimosse']),(0,1)); self.assertFalse(self.exists('Nuova'))

    def test_unreadable_container_is_reported(self):
        self.put('Nuova cartella/a.txt'); plan=self.plan(('Nuova cartella/a.txt','X/a.txt'),vuote=['Nuova cartella'])
        real=m.os.scandir
        def denied(path):
            if Path(path).name=='Nuova cartella': raise PermissionError('accesso negato')
            return real(path)
        with patch.object(m.os,'scandir',side_effect=denied): out,code=m.execute(plan)
        self.assertEqual((code,out['eseguite'],out['errore']['vuota']),(1,1,'Nuova cartella'))
        self.assertTrue(self.exists('Nuova cartella') and self.exists('X/a.txt'))

    def test_unreadable_journal_is_named(self):
        self.put('a.txt'); plan=self.plan(('a.txt','X/a.txt'))
        (self.state/'piano.giornale.jsonl').write_text('{"da": "a.txt", "a": "X/a.t',encoding='utf-8')
        for run in (lambda: m.execute(plan,dry_run=True),lambda: m.undo(plan)):
            with self.assertRaisesRegex(ValueError,'riga 1'): run()

    def test_only_folders_can_be_emptied(self):
        self.put('a.txt'); out,code=m.execute(self.plan(vuote=['a.txt']))
        self.assertEqual((code,out['problemi'][0]['problema']),(1,'non è una cartella da svuotare'))

    def test_undo_reports_conflicts(self):
        self.put('a.txt'); self.put('b.txt'); plan=self.plan(('a.txt','X/a.txt'),('b.txt','X/b.txt'))
        m.execute(plan); (self.root/'X/b.txt').rename(self.root/'altrove.txt')
        out,code=m.undo(plan)
        self.assertEqual(code,1); self.assertEqual(out['conflitti'][0]['problema'],'origine e destinazione assenti')
        self.assertTrue(self.exists('a.txt')); self.assertTrue((self.state/'piano.giornale.jsonl').exists())

if __name__=='__main__': unittest.main()
