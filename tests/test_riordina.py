import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('riordina', Path(__file__).resolve().parents[1]/'riordina.py')
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
    def plan(self, *moves):
        p=self.state/'piano.json'
        p.write_text(json.dumps({'radice':str(self.root),'mosse':[{'da':a,'a':b} for a,b in moves]}),encoding='utf-8')
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

    def test_depth_limits_descent(self):
        self.put('A/B/c.txt'); voce=m.inventory(self.root,depth=2)['voci'][0]
        self.assertEqual((voce['cartelle'],voce['file'],voce['parziale']),(1,0,True))

    def test_links_are_listed_not_followed(self):
        target=self.base/'fuori'; target.mkdir(); (target/'x.txt').write_text('x'); junction(target,self.root/'link')
        out=m.inventory(self.root)
        self.assertEqual((out['link'],out['totale']['file']),(['link'],0))

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
        self.assertEqual((code,out['problemi'][0]['problema']),(1,'link o junction: da spostare a mano'))

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

    def test_undo_reports_conflicts(self):
        self.put('a.txt'); self.put('b.txt'); plan=self.plan(('a.txt','X/a.txt'),('b.txt','X/b.txt'))
        m.execute(plan); (self.root/'X/b.txt').rename(self.root/'altrove.txt')
        out,code=m.undo(plan)
        self.assertEqual(code,1); self.assertEqual(out['conflitti'][0]['problema'],'origine e destinazione assenti')
        self.assertTrue(self.exists('a.txt')); self.assertTrue((self.state/'piano.giornale.jsonl').exists())

if __name__=='__main__': unittest.main()
