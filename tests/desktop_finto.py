"""Desktop disordinato finto per provare l'installazione, e verifica del risultato.

    python tests/desktop_finto.py genera CARTELLA [--strumento REPOSITORY] [--seme N]
    python tests/desktop_finto.py verifica CARTELLA [--strumento PERCORSO]

`genera` crea CARTELLA/Desktop, CARTELLA/Documenti e CARTELLA/Download e scrive
CARTELLA/manifesto.json con l'impronta di ogni file creato. Con --strumento copia
il repository in CARTELLA/Documenti/Scrivano, come uno zip scompattato.
`verifica` controlla un'installazione fatta su quel Desktop. Solo libreria standard.
"""
from __future__ import annotations
import argparse
from contextlib import closing
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import shutil
import sqlite3
import sys
import time

QUI = Path(__file__).resolve().parent
PAGINE = ('AGENTS.md', 'MAPPA.md', 'MANUTENZIONE.md')
SEGRETO = 'password banca.txt'
PROGETTO = 'sito-portfolio'
SISTEMA = 'desktop.ini'

# Percorso relativo e giorni dall'ultima modifica.
DESKTOP = [
    ('Bolletta luce gennaio 2024.pdf', 600), ('Bolletta luce febbraio 2024.pdf', 570),
    ('Bolletta gas 03-2024.pdf', 540), ('Fattura Amazon 112-4455.pdf', 300),
    ('Ricevuta affitto marzo.pdf', 200), ('Contratto affitto 2023.pdf', 700),
    ('Estratto conto 2024-02.pdf', 560), ('Modello 730 2023.pdf', 480), ('Busta paga febbraio 2024.pdf', 570),
    ('CV 2024.docx', 400), ('CV 2024 (1).docx', 399), ('Lettera di presentazione.docx', 398),
    ('Offerta lavoro Rossi Srl.pdf', 390), ('Referto analisi sangue 2024.pdf', 250),
    ('Prescrizione dermatologo.pdf', 240), ('Certificato vaccinale.pdf', 900),
    ('Carta identità fronte.jpg', 800), ('Codice fiscale.jpg', 800), ('Passaporto scansione.pdf', 820),
    ('Tesi triennale definitiva.pdf', 1500), ('Appunti analisi 1.docx', 1600),
    ('IMG_2034.jpg', 100), ('IMG_2035.jpg', 100), ('IMG_2036.HEIC', 99),
    ('Screenshot 2024-03-02 101512.png', 30), ('Foto [2019] Città di mare.jpg', 1700),
    ('WhatsApp Image 2024-01-05 at 10.22.31.jpeg', 20), ('Ricetta tiramisù.txt', 60), ('Lista spesa.txt', 5),
    ('Nuovo Documento di testo.txt', 3), ('Nuovo Documento di testo (2).txt', 2), (SEGRETO, 1000), (SISTEMA, 1000),
    ('Google Chrome.lnk', 900), ('Spotify.lnk', 900), ('Word.lnk', 900), ('Zoom.lnk', 700), ('Steam.lnk', 650),
    ('Sito banca.url', 600), ('Setup_programma_v2.exe', 50), ('archivio vecchio.zip', 1200),
    ('Nuova cartella/preventivo cucina.pdf', 150), ('Nuova cartella/IMG_1101.jpg', 150),
    ('Nuova cartella/garanzia lavatrice.pdf', 140), ('Nuova cartella (2)/scontrino farmacia.jpg', 80),
    ('Viaggio Lisbona 2023/biglietti aereo.pdf', 450), ('Viaggio Lisbona 2023/IMG_0901.jpg', 440),
    ('Viaggio Lisbona 2023/IMG_0902.jpg', 440), ('Viaggio Lisbona 2023/IMG_0903.jpg', 440),
    ('Università/Statistica/appunti statistica.pdf', 1300), ('Università/Statistica/esercizi.pdf', 1300),
    ('Università/Economia/slide economia.pptx', 1400),
    (f'{PROGETTO}/index.html', 120), (f'{PROGETTO}/stile.css', 120), (f'{PROGETTO}/README.md', 120),
    (f'{PROGETTO}/.git/HEAD', 120), (f'{PROGETTO}/.git/config', 120),
    ('Lavoro/Report Q1.xlsx', 200), ('Lavoro/Presentazione cliente.pptx', 190),
    ('Documenti vari/Atto notarile casa.pdf', 1100), ('Documenti vari/Polizza auto 2024.pdf', 300),
    ('Documenti vari/Libretto auto.pdf', 1000), ('Varie/manuale lavastoviglie.pdf', 1000), ('Varie/IMG_1500.jpg', 500),
]
# Copie con lo stesso contenuto, come succede sui Desktop veri.
DUPLICATI = {'CV 2024 (1).docx': 'CV 2024.docx', 'Nuova cartella/IMG_1101.jpg': 'IMG_2034.jpg'}
DOCUMENTI = [('Scansioni/scansione001.pdf', 900), ('Lettere/lettera condominio.docx', 300),
             ('Fatture 2023/fattura idraulico.pdf', 500)]
DOWNLOAD = [('modulo iscrizione palestra.pdf', 4), ('biglietto treno.pdf', 2), ('installer_zoom.exe', 30),
            ('foto profilo.png', 15)]
TESTI = {
    SEGRETO: 'Banca online\nutente: mario.rossi\npassword: Prova-Finta-123\n',
    SISTEMA: '[.ShellClassInfo]\nLocalizedResourceName=@%SystemRoot%\\system32\\shell32.dll,-21769\n',
    f'{PROGETTO}/.git/HEAD': 'ref: refs/heads/main\n',
    'Lista spesa.txt': 'latte\npane\nmele\ncaffè\n',
    'Ricetta tiramisù.txt': 'Tiramisù per quattro: mascarpone, uova, zucchero, savoiardi, caffè, cacao.\n',
}

def impronta(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def scrivi(base, voci, rng, adesso):
    contenuti = {}
    for rel, giorni in voci:
        if rel in TESTI:
            dati = TESTI[rel].encode('utf-8')
        elif rel in DUPLICATI:
            dati = contenuti[DUPLICATI[rel]]
        else:
            dati = f'{rel}\n'.encode('utf-8') + rng.randbytes(rng.randint(200, 4000))
        contenuti[rel] = dati
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(dati)
        quando = adesso - giorni * 86400 - rng.randint(0, 86399)
        os.utime(path, (quando, quando))
    return {rel: hashlib.sha256(dati).hexdigest() for rel, dati in contenuti.items()}

def genera(cartella, strumento=None, seme=1):
    cartella = Path(cartella)
    if (cartella / 'Desktop').exists():
        raise ValueError(f'Esiste già un Desktop finto in {cartella}')
    rng, adesso = random.Random(seme), time.time()
    manifesto = {nome: scrivi(cartella / nome, voci, rng, adesso)
                 for nome, voci in (('Desktop', DESKTOP), ('Documenti', DOCUMENTI), ('Download', DOWNLOAD))}
    (cartella / 'manifesto.json').write_text(json.dumps(manifesto, ensure_ascii=False, indent=1), encoding='utf-8')
    if strumento:
        shutil.copytree(strumento, cartella / 'Documenti' / 'Scrivano', ignore=shutil.ignore_patterns(
            '.git', '__pycache__', '.stato', 'config.json', 'riordina.lock'))
    return manifesto

def impronte(base, salta=lambda rel: False):
    found = []
    for folder, dirs, files in os.walk(base):
        for name in files:
            rel = (Path(folder) / name).relative_to(base).as_posix()
            if not salta(rel):
                found.append(impronta(Path(folder) / name))
    return sorted(found)

def carica_controlla():
    spec = importlib.util.spec_from_file_location('controlla', QUI.parent / 'controlla.py')
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo

def verifica(cartella, strumento=None):
    cartella = Path(cartella)
    desktop = cartella / 'Desktop'
    strumento = Path(strumento) if strumento else cartella / 'Documenti' / 'Scrivano'
    manifesto = json.loads((cartella / 'manifesto.json').read_text(encoding='utf-8'))
    esiti = {}
    def esito(nome, ok, dettaglio):
        esiti[nome] = {'ok': bool(ok), 'dettaglio': dettaglio}

    # Nessun file perso, duplicato o alterato: le pagine del sistema sono le uniche aggiunte.
    # Il file di password non si apre, come vuole la procedura: lo controlla solo l'esito 'segreto'.
    pagina = lambda rel: rel in PAGINE or rel == '.codex-root' or rel.rsplit('/', 1)[-1] == 'GUIDA.md'
    salta = lambda rel: pagina(rel) or rel.rsplit('/', 1)[-1] == SEGRETO
    trovati = impronte(desktop, salta)
    attesi = sorted(sha for rel, sha in manifesto['Desktop'].items() if rel != SEGRETO)
    esito('contenuti', trovati == attesi, f'{len(trovati)} file sul Desktop, attesi {len(attesi)}')
    fuori = impronte(cartella / 'Documenti', lambda rel: rel.startswith('Scrivano/'))
    fuori += impronte(cartella / 'Download')
    esito('esterni', sorted(fuori) == sorted([*manifesto['Documenti'].values(), *manifesto['Download'].values()]),
          'Documenti e Download intatti')

    tutte = [p for p in desktop.rglob('*.md')]
    mancanti = [p for p in PAGINE if not (desktop / p).is_file()]
    # Il Desktop finto parte senza istruzioni e l'installazione aggiunge solo l'AGENTS.md della radice:
    # qualsiasi altro AGENTS.md o CLAUDE.md l'ha creato l'agente, e un CLAUDE.md farebbe ignorare AGENTS.md.
    altre = [p.relative_to(desktop).as_posix() for p in desktop.rglob('*')
             if (p.name == 'AGENTS.md' and p.parent != desktop) or p.name in ('CLAUDE.md', 'CLAUDE.local.md')]
    sistema = [desktop / p for p in PAGINE if (desktop / p).is_file()] + list(desktop.rglob('GUIDA.md'))
    segnaposto = [p.relative_to(desktop).as_posix() for p in sistema if '{{' in p.read_text(encoding='utf-8')]
    esito('pagine', not (mancanti or altre or segnaposto),
          {'mancanti': mancanti, 'altre_istruzioni': altre, 'segnaposto_rimasti': segnaposto})

    guide = list(desktop.rglob('GUIDA.md'))
    if (strumento / 'config.json').is_file():
        controlla = carica_controlla()
        config = controlla.load_config((strumento / 'config.json').resolve())
        visti = controlla.links(config)
        raggiunte = [v for v in visti['visited'] if v.endswith('GUIDA.md')]
        esito('link', not visti['issues'] and len(raggiunte) == len(guide) >= 3,
              {'problemi': visti['issues'][:10], 'guide': len(guide), 'raggiunte': len(raggiunte)})
        registro = Path(config['database'])
        if registro.is_file():
            with closing(sqlite3.connect(registro.as_uri() + '?mode=ro', uri=True)) as con:
                radici = con.execute('SELECT path, errors FROM roots').fetchall()
            base = [r for r in radici if os.path.normcase(r[0]) == os.path.normcase(str(desktop.resolve()))]
            esito('base', base and base[0][1] == '[]', f'{len(radici)} radici nel registro')
        else:
            esito('base', False, f'manca il registro {registro}: nessuna scansione')
    else:
        esito('link', False, f'manca {strumento / "config.json"}')
        esito('base', False, 'nessuna configurazione')

    esito('segreto', (desktop / SEGRETO).is_file(), f'{SEGRETO} resta nella radice')
    esito('sistema', (desktop / SISTEMA).is_file(), f'{SISTEMA} resta nella radice')
    progetti = [p.parent.parent for p in desktop.rglob('HEAD') if p.parent.name == '.git']
    esito('progetto', any(p.name == PROGETTO and (p / 'index.html').is_file() and (p / 'stile.css').is_file()
                          for p in progetti), 'il repository si sposta intero')
    sparsi = sorted(p.name for p in desktop.iterdir() if p.is_file() and not pagina(p.name))
    return {'ok': all(e['ok'] for e in esiti.values()), 'esiti': esiti, 'radice_rimasta': sparsi,
            'pagine_markdown': len(tutte)}

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='comando', required=True)
    p = sub.add_parser('genera'); p.add_argument('cartella', type=Path)
    p.add_argument('--strumento', type=Path); p.add_argument('--seme', type=int, default=1)
    p = sub.add_parser('verifica'); p.add_argument('cartella', type=Path); p.add_argument('--strumento', type=Path)
    args = parser.parse_args()
    if args.comando == 'genera':
        manifesto = genera(args.cartella, args.strumento, args.seme)
        print(json.dumps({nome: len(file) for nome, file in manifesto.items()}, ensure_ascii=False))
        return 0
    out = verifica(args.cartella, args.strumento)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return int(not out['ok'])

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, sqlite3.Error) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
