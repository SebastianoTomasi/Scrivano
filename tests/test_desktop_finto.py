import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

d = load('desktop_finto', REPO/'tests'/'desktop_finto.py')
r = load('riordina', REPO/'riordina.py')

class FakeDesktopTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)/'prova'

    def test_generated_desktop_looks_messy(self):
        manifesto=d.genera(self.base)
        self.assertEqual(len(manifesto['Desktop']),len(d.DESKTOP))
        self.assertEqual(json.loads((self.base/'manifesto.json').read_text(encoding='utf-8')),manifesto)
        out=r.inventory(self.base/'Desktop')
        self.assertIn(d.SEGRETO,out['segreti']); self.assertIn(d.PROGETTO,out['progetti'])
        self.assertTrue(any('CV 2024.docx' in g['percorsi'] for g in out['duplicati']))

    def test_mac_desktop(self):
        manifesto=d.genera(self.base,mac=True)
        self.assertIn(d.LOCALIZZATO,manifesto['Desktop']); self.assertNotIn(d.SISTEMA,manifesto['Desktop'])
        self.assertFalse(any(rel.endswith('.lnk') for rel in manifesto['Desktop']))
        out=r.inventory(self.base/'Desktop')
        self.assertEqual(sorted(out['segreti']),sorted([d.CHIAVE,d.SEGRETO])); self.assertEqual(out['pacchetti'],[d.PACCHETTO])
        esiti=d.verifica(self.base)['esiti']
        self.assertTrue(esiti['contenuti']['ok'] and esiti['sistema']['ok'] and esiti['pacchetto']['ok'])

    def test_same_seed_same_desktop(self):
        self.assertEqual(d.genera(self.base,seme=7),d.genera(Path(self.temp.name)/'altra',seme=7))

    def test_verification_needs_an_installation(self):
        d.genera(self.base,strumento=REPO)
        self.assertTrue((self.base/'Documenti'/'Scrivano'/'INSTALLA.md').is_file())
        out=d.verifica(self.base)
        self.assertTrue(out['esiti']['contenuti']['ok']); self.assertTrue(out['esiti']['esterni']['ok'])
        self.assertFalse(out['esiti']['pagine']['ok']); self.assertFalse(out['ok'])

if __name__=='__main__': unittest.main()
