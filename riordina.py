"""Inventario di una cartella e riordino secondo un piano approvato. Solo libreria standard; nessuna rete.

Lo script non decide nulla: l'agente scrive il piano, l'utente lo approva, lo script lo esegue.
Non sovrascrive, non cancella, si ferma al primo problema e annota ogni mossa nel giornale.
"""
from __future__ import annotations
import argparse
from collections import Counter
from contextlib import contextmanager
import fnmatch
import hashlib
import heapq
import json
import os
from pathlib import Path
import stat
import sys
import time

# Attributi Windows dei file solo nel cloud: leggerli li scaricherebbe.
CLOUD = 0x1000 | 0x40000 | 0x400000
# Cartelle trattate come unità: l'inventario non scende al loro interno.
HEAVY = {n.casefold() for n in ('.git', '.hg', '.svn', 'node_modules', '.venv', 'venv', '__pycache__',
                                '.pytest_cache', '.mypy_cache', '.cache', '.uv-cache', '.tox', '.next')}
# Segnali di cartella-progetto: si sposta intera o resta dov'è.
PROJECT = {n.casefold() for n in ('.git', '.venv', 'venv', 'node_modules', 'package.json', 'pyproject.toml',
                                  'requirements.txt', 'Cargo.toml', 'go.mod')}
# Nomi da segreto: l'inventario li segnala senza leggerli.
SECRETS = ('.env', '.env.*', '*.pem', '*.key', 'id_rsa*', 'id_ed25519*', '*.pfx', '*.p12', '*.kdbx',
           '*passw*', '*credenzial*', '*credential*')

def stamp():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

def day(ns):
    return time.strftime('%Y-%m-%d', time.localtime(ns / 1e9))

def is_link(info):
    # Link simbolici e junction non si seguono e non si spostano.
    return stat.S_ISLNK(info.st_mode) or getattr(info, 'st_reparse_tag', 0) == stat.IO_REPARSE_TAG_MOUNT_POINT

def is_cloud(info):
    return bool(getattr(info, 'st_file_attributes', 0) & CLOUD)

def is_secret(name):
    return any(fnmatch.fnmatchcase(name.casefold(), p) for p in SECRETS)

def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

# --- Inventario ---

def tally():
    return {'file': 0, 'cartelle': 0, 'byte': 0, 'solo_cloud': 0, 'estensioni': Counter(),
            'dal': None, 'al': None, 'pesanti': set(), 'parziale': False}

def add_file(rel, path, info, acc, state):
    size, mtime, name = info.st_size, info.st_mtime_ns, rel.rsplit('/', 1)[-1]
    ext = Path(name).suffix.casefold() or '(nessuna)'
    for t in (acc, state['totale']):
        t['file'] += 1
        t['byte'] += size
    acc['estensioni'][ext] += 1
    state['estensioni'][ext] += 1
    acc['dal'] = min(acc['dal'] or mtime, mtime)
    acc['al'] = max(acc['al'] or mtime, mtime)
    heapq.heappush(state['grandi'], (size, rel))
    if len(state['grandi']) > 10:
        heapq.heappop(state['grandi'])
    if is_secret(name):
        state['segreti'].append(rel)
    if is_cloud(info):
        acc['solo_cloud'] += 1
        state['totale']['solo_cloud'] += 1
    elif size and not is_secret(name):
        state['per_dimensione'].setdefault(size, []).append((rel, path))

def visit(folder, rel, level, depth, acc, state):
    try:
        with os.scandir(folder) as listing:
            entries = sorted(listing, key=lambda e: e.name.casefold())
    except OSError as exc:
        state['errori'].append({'percorso': rel, 'errore': str(exc)})
        acc['parziale'] = True
        return
    if any(e.name.casefold() in PROJECT for e in entries):
        state['progetti'].append(rel)
    for entry in entries:
        child = f'{rel}/{entry.name}'
        try:
            info = os.stat(entry.path, follow_symlinks=False)
        except OSError as exc:
            state['errori'].append({'percorso': child, 'errore': str(exc)})
            continue
        if is_link(info):
            state['link'].append(child)
        elif stat.S_ISDIR(info.st_mode):
            acc['cartelle'] += 1
            state['totale']['cartelle'] += 1
            if entry.name.casefold() in HEAVY:
                acc['pesanti'].add(entry.name)
                state['pesanti'].add(entry.name)
            elif depth is None or level + 1 < depth:
                visit(entry.path, child, level + 1, depth, acc, state)
            else:
                acc['parziale'] = True
        elif stat.S_ISREG(info.st_mode):
            add_file(child, entry.path, info, acc, state)

def summary(acc):
    out = {'file': acc['file'], 'cartelle': acc['cartelle'], 'byte': acc['byte'],
           'estensioni': dict(acc['estensioni'].most_common(5))}
    if acc['dal']:
        out.update(dal=day(acc['dal']), al=day(acc['al']))
    if acc['solo_cloud']:
        out['solo_cloud'] = acc['solo_cloud']
    if acc['pesanti']:
        out['pesanti'] = sorted(acc['pesanti'], key=str.casefold)
    if acc['parziale']:
        out['parziale'] = True
    return out

def duplicates(by_size, limit=20):
    # Impronte solo fra file locali della stessa dimensione: niente letture inutili.
    groups = []
    for size, files in by_size.items():
        if len(files) < 2:
            continue
        by_hash = {}
        for rel, path in files:
            try:
                by_hash.setdefault(digest(path), []).append(rel)
            except OSError:
                continue
        groups += [{'byte': size, 'percorsi': sorted(r)} for r in by_hash.values() if len(r) > 1]
    groups.sort(key=lambda g: g['byte'] * (len(g['percorsi']) - 1), reverse=True)
    return groups[:limit]

def inventory(root, depth=None, limit=300):
    base = Path(root).resolve()
    if not base.is_dir():
        raise ValueError(f'Cartella non trovata: {root}')
    if depth is not None and depth < 1:
        raise ValueError('Profondità non valida: usare un intero >= 1')
    state = {'totale': {'file': 0, 'cartelle': 0, 'byte': 0, 'solo_cloud': 0}, 'estensioni': Counter(),
             'progetti': [], 'segreti': [], 'link': [], 'pesanti': set(), 'errori': [], 'grandi': [],
             'per_dimensione': {}}
    with os.scandir(base) as listing:
        entries = sorted(listing, key=lambda e: e.name.casefold())
    items = []
    for entry in entries:
        name = entry.name
        try:
            info = os.stat(entry.path, follow_symlinks=False)
        except OSError as exc:
            state['errori'].append({'percorso': name, 'errore': str(exc)})
            continue
        if is_link(info):
            state['link'].append(name)
            items.append({'nome': name, 'tipo': 'link'})
        elif stat.S_ISDIR(info.st_mode):
            state['totale']['cartelle'] += 1
            acc, item = tally(), {'nome': name, 'tipo': 'cartella'}
            if name.casefold() in HEAVY:
                acc['pesanti'].add(name)
                state['pesanti'].add(name)
            elif depth is None or depth > 1:
                visit(entry.path, name, 1, depth, acc, state)
            else:
                acc['parziale'] = True
            item.update(summary(acc))
            if name in state['progetti']:
                item['progetto'] = True
            items.append(item)
        elif stat.S_ISREG(info.st_mode):
            add_file(name, entry.path, info, tally(), state)
            item = {'nome': name, 'tipo': 'file', 'byte': info.st_size, 'modificato': day(info.st_mtime_ns)}
            if is_cloud(info):
                item['solo_cloud'] = True
            if is_secret(name):
                item['segreto'] = True
            items.append(item)
    return {'radice': str(base), 'totale': state['totale'], 'voci': items[:limit],
            'altre_voci': max(0, len(items) - limit), 'estensioni': dict(state['estensioni'].most_common(15)),
            'progetti': state['progetti'][:50], 'segreti': state['segreti'][:50], 'link': state['link'][:50],
            'duplicati': duplicates(state['per_dimensione']),
            'grandi': [{'percorso': rel, 'byte': size} for size, rel in sorted(state['grandi'], reverse=True)],
            'esclusioni_suggerite': sorted(state['pesanti'], key=str.casefold), 'errori': state['errori'][:50]}

# --- Piano ---

def relative(rel):
    # Percorso relativo alla radice, separato da '/': niente percorsi assoluti né risalite.
    p = Path(str(rel))
    if p.is_absolute() or p.drive or p.root or not p.parts or '..' in p.parts:
        raise ValueError(f'Percorso non valido nel piano: {rel}')
    return p.as_posix()

def load_plan(path):
    plan = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if not isinstance(plan, dict) or 'radice' not in plan or not isinstance(plan.get('mosse'), list):
        raise ValueError('Piano non valido: servono "radice" e "mosse"')
    root = Path(plan['radice']).resolve()
    if not root.is_dir():
        raise ValueError(f'Radice del piano non trovata: {root}')
    moves = []
    for move in plan['mosse']:
        if not isinstance(move, dict) or 'da' not in move or 'a' not in move:
            raise ValueError('Mossa non valida: servono "da" e "a"')
        moves.append((relative(move['da']), relative(move['a'])))
    # Cartelle-contenitore da togliere se le mosse le lasciano vuote.
    if not isinstance(plan.get('vuote', []), list):
        raise ValueError('Piano non valido: "vuote" è un elenco di cartelle')
    return root, moves, [relative(folder) for folder in plan.get('vuote', [])]

def journal_path(plan_path):
    return plan_path.with_name(plan_path.stem + '.giornale.jsonl')

def key(rel):
    return rel.casefold() if os.name == 'nt' else rel

def ancestors(rel):
    # 'a/b/c' -> ['a', 'a/b', 'a/b/c']
    parts = rel.split('/')
    return ['/'.join(parts[:i]) for i in range(1, len(parts) + 1)]

def status(root, src, dst):
    has_src, has_dst = os.path.lexists(root / src), os.path.lexists(root / dst)
    if has_src and has_dst:
        return 'destinazione già occupata', None
    if not has_src:
        # Origine assente e destinazione presente: mossa già fatta in un'esecuzione interrotta.
        return (None, 'fatta') if has_dst else ('origine mancante', None)
    if is_link(os.stat(root / src, follow_symlinks=False)):
        return 'link simbolico o junction: da spostare a mano', None
    for folder in ancestors(dst)[:-1]:
        if os.path.lexists(root / folder):
            info = os.stat(root / folder, follow_symlinks=False)
            if is_link(info):
                return 'la destinazione passa da un link simbolico o una junction', None
            if not stat.S_ISDIR(info.st_mode):
                return 'un file occupa il percorso di destinazione', None
    return None, 'da_fare'

def check(root, moves, empties=()):
    # Il piano descrive l'albero originale: origini e destinazioni non si sovrappongono.
    keys = [(key(s), key(d)) for s, d in moves]
    sources, targets = Counter(s for s, _ in keys), Counter(d for _, d in keys)
    states, problems = [], []
    for number, ((src, dst), (ks, kd)) in enumerate(zip(moves, keys), 1):
        state = None
        if sources[ks] > 1 or targets[kd] > 1:
            issue = 'origine o destinazione ripetuta nel piano'
        elif ks == kd:
            issue = ('origine e destinazione coincidono' if src == dst else
                     'cambia solo maiuscole e minuscole: passa da un nome intermedio, in due piani')
        elif any(a in sources for a in ancestors(kd)):
            issue = "destinazione dentro un'origine del piano"
        elif any(a in targets for a in ancestors(ks)):
            issue = 'origine dentro una destinazione del piano'
        elif any(a in sources for a in ancestors(ks)[:-1]):
            issue = "origine dentro un'altra origine del piano"
        elif any(a in targets for a in ancestors(kd)[:-1]):
            issue = "destinazione dentro un'altra destinazione del piano"
        else:
            issue, state = status(root, src, dst)
        states.append(state)
        if issue:
            problems.append({'mossa': number, 'da': src, 'a': dst, 'problema': issue})
    for folder in empties:
        if os.path.lexists(root / folder):
            info = os.stat(root / folder, follow_symlinks=False)
            if is_link(info) or not stat.S_ISDIR(info.st_mode):
                problems.append({'vuota': folder, 'problema': 'non è una cartella da svuotare'})
    return states, problems

def missing_parents(root, rel):
    return [f for f in ancestors(rel)[:-1] if not os.path.lexists(root / f)]

def count_files(root):
    # File sotto la radice, senza seguire link e junction: gli spostamenti non devono cambiarne il numero.
    total, stack = 0, [root]
    while stack:
        try:
            with os.scandir(stack.pop()) as listing:
                entries = list(listing)
        except OSError:
            continue
        for entry in entries:
            try:
                if entry.is_symlink() or is_link(os.stat(entry.path, follow_symlinks=False)):
                    continue
                if entry.is_dir(follow_symlinks=False):
                    stack.append(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    total += 1
            except OSError:
                continue
    return total

@contextmanager
def lock(folder):
    path = Path(folder) / 'riordina.lock'
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ValueError(f'Un altro riordino è in corso o si è interrotto: verifica e poi elimina {path}') from None
    os.write(fd, stamp().encode('ascii'))
    os.close(fd)
    try:
        yield
    finally:
        os.unlink(path)

def note(log, **entry):
    # Riga scritta su disco prima della mossa: un'interruzione non ne perde traccia.
    log.write(json.dumps({**entry, 'ora': stamp()}, ensure_ascii=False) + '\n')
    log.flush()
    os.fsync(log.fileno())

def execute(plan_path, dry_run=False):
    root, moves, empties = load_plan(plan_path)
    states, problems = check(root, moves, empties)
    report = {'radice': str(root), 'mosse': len(moves), 'da_fare': states.count('da_fare'),
              'gia_fatte': states.count('fatta'), 'problemi': problems}
    if problems or dry_run:
        return report, int(bool(problems))
    journal, done, error, removed, kept = journal_path(plan_path), 0, None, [], []
    with lock(plan_path.parent), open(journal, 'a', encoding='utf-8') as log:
        before = count_files(root)
        for (src, dst), state in zip(moves, states):
            if state != 'da_fare':
                continue
            try:
                for folder in missing_parents(root, dst):
                    os.mkdir(root / folder)
                    note(log, cartella=folder)
                note(log, da=src, a=dst)
                if os.path.lexists(root / dst):
                    raise FileExistsError(f'Destinazione comparsa durante il riordino: {dst}')
                os.rename(root / src, root / dst)
                done += 1
            except OSError as exc:
                error = {'da': src, 'a': dst, 'errore': str(exc)}
                break
        for folder in empties if error is None else ():
            # Solo cartelle rimaste davvero vuote: una con qualcosa dentro resta e si segnala.
            if not os.path.lexists(root / folder):
                continue
            with os.scandir(root / folder) as listing:
                if next(listing, None) is not None:
                    kept.append(folder)
                    continue
            try:
                note(log, rimossa=folder)
                os.rmdir(root / folder)
                removed.append(folder)
            except OSError as exc:
                error = {'vuota': folder, 'errore': str(exc)}
                break
        after = count_files(root)
    report.update(eseguite=done, errore=error, cartelle_rimosse=removed, cartelle_rimaste=kept,
                  conteggio={'prima': before, 'dopo': after}, giornale=str(journal))
    return report, int(bool(error) or before != after)

def undo(plan_path):
    root, _, _ = load_plan(plan_path)
    journal = journal_path(plan_path)
    if not journal.is_file():
        raise ValueError(f'Nessun giornale da annullare: {journal}')
    entries = [json.loads(line) for line in journal.read_text(encoding='utf-8').splitlines() if line.strip()]
    restored, in_place, removed, recreated, conflicts, error = 0, 0, 0, 0, [], None
    with lock(plan_path.parent):
        for entry in reversed(entries):
            if 'rimossa' in entry:
                # Una cartella svuotata e tolta torna prima che i file vi rientrino.
                if not os.path.lexists(root / entry['rimossa']):
                    try:
                        for folder in missing_parents(root, entry['rimossa']) + [entry['rimossa']]:
                            os.mkdir(root / folder)
                        recreated += 1
                    except OSError as exc:
                        error = {'vuota': entry['rimossa'], 'errore': str(exc)}
                        break
                continue
            if 'cartella' in entry:
                try:
                    os.rmdir(root / entry['cartella'])
                    removed += 1
                except OSError:
                    pass  # non vuota o già assente: resta dov'è
                continue
            src, dst = root / entry['da'], root / entry['a']
            has_src, has_dst = os.path.lexists(src), os.path.lexists(dst)
            if has_src and not has_dst:
                in_place += 1  # mossa mai avvenuta o già annullata
                continue
            if has_src == has_dst:
                problem = 'origine e destinazione presenti' if has_src else 'origine e destinazione assenti'
                conflicts.append({'da': entry['da'], 'a': entry['a'], 'problema': problem})
                continue
            try:
                for folder in missing_parents(root, entry['da']):
                    os.mkdir(root / folder)
                os.rename(dst, src)
                restored += 1
            except OSError as exc:
                error = {'da': entry['da'], 'a': entry['a'], 'errore': str(exc)}
                break
        if error is None and not conflicts:
            # Giornale chiuso: una nuova esecuzione ne apre uno pulito.
            journal = journal.rename(journal.with_name(f'{journal.stem}.annullato-{time.strftime("%Y%m%d-%H%M%S")}.jsonl'))
    return ({'radice': str(root), 'ripristinate': restored, 'gia_al_posto': in_place, 'cartelle_rimosse': removed,
             'cartelle_ricreate': recreated, 'conflitti': conflicts, 'errore': error, 'giornale': str(journal)},
            int(bool(error or conflicts)))

def main():
    # PowerShell e percorsi Unicode: output UTF-8 anche con locale Windows legacy.
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('inventario'); p.add_argument('radice', type=Path)
    p.add_argument('--profondita', type=int); p.add_argument('--max', type=int, default=300)
    p = sub.add_parser('esegui'); p.add_argument('piano', type=Path); p.add_argument('--prova', action='store_true')
    p = sub.add_parser('annulla'); p.add_argument('piano', type=Path)
    args = parser.parse_args()
    if args.command == 'inventario':
        out = inventory(args.radice, args.profondita, args.max)
        code = int(bool(out['errori']))
    elif args.command == 'esegui':
        out, code = execute(args.piano.resolve(), args.prova)
    else:
        out, code = undo(args.piano.resolve())
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return code

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
