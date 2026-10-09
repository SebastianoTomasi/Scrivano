"""Registro locale dei cambiamenti. Solo libreria standard; nessuna rete."""
from __future__ import annotations
import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import sys
import time
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / 'config.json'
# Attributi Windows dei file solo nel cloud (offline, recall on open, recall on data access).
CLOUD = 0x1000 | 0x40000 | 0x400000
# Bit "name surrogate" del reparse tag: il reparse point rimanda a un altro percorso (junction, link WSL).
SURROGATE = 0x20000000

class Linked(OSError):
    """Link simbolico o junction: non si segue."""

def stamp():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def is_link(info):
    # Link simbolici e junction, con lo stesso criterio di os.lstat; gli altri reparse point,
    # come i file di OneDrive, sono file normali.
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_reparse_tag', 0) & SURROGATE)

def signature(path, old=None, full=False):
    info = path.stat(follow_symlinks=False)
    if is_link(info):
        raise Linked('Link/junction escluso')
    if stat.S_ISDIR(info.st_mode):
        return {'kind': 'directory', 'size': 0, 'mtime': 0, 'hash': None}
    if not stat.S_ISREG(info.st_mode):
        raise OSError('Tipo di file non supportato')
    meta = (info.st_size, info.st_mtime_ns)
    if old and not full and old['kind'] == 'file' and meta == (old['size'], old['mtime']):
        return old
    if getattr(info, 'st_file_attributes', 0) & CLOUD:
        # Leggerlo lo scaricherebbe dal cloud: bastano dimensione e data.
        return {'kind': 'file', 'size': meta[0], 'mtime': meta[1], 'hash': None}
    sha = digest(path)
    after = path.stat(follow_symlinks=False)
    if (after.st_size, after.st_mtime_ns) != meta:
        raise OSError('File modificato durante la lettura; riprovare')
    return {'kind': 'file', 'size': meta[0], 'mtime': meta[1], 'hash': sha}

def same(a, b):
    if a is None or b is None:
        return a == b
    if (a['kind'], a['size']) != (b['kind'], b['size']):
        return False
    if a['hash'] and b['hash']:
        return a['hash'] == b['hash']
    # Senza impronta (cartelle, file solo nel cloud) confronta la data.
    return a['kind'] == 'directory' or a['mtime'] == b['mtime']

def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)

def connect(db):
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db, timeout=15)
    con.row_factory = sqlite3.Row
    con.executescript('''
    CREATE TABLE IF NOT EXISTS roots(id TEXT PRIMARY KEY, path TEXT NOT NULL,
      baseline_at TEXT NOT NULL, last_scan TEXT, errors TEXT NOT NULL DEFAULT '[]');
    CREATE TABLE IF NOT EXISTS observed(root TEXT, path TEXT, sig TEXT NOT NULL,
      PRIMARY KEY(root,path));
    CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, root TEXT NOT NULL,
      path TEXT NOT NULL, kind TEXT NOT NULL, before_sig TEXT NOT NULL,
      after_sig TEXT NOT NULL, created TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending', reviewed TEXT, note TEXT,
      superseded_by INTEGER);
    CREATE INDEX IF NOT EXISTS pending_events ON events(status,root,path);
    ''')
    return con

def load_config(path):
    config = json.loads(path.read_text(encoding='utf-8-sig'))
    roots = config.get('roots') if isinstance(config, dict) else None
    text = lambda value: isinstance(value, str) and value.strip()
    if not isinstance(roots, list) or not all(isinstance(r, dict) and text(r.get('id')) and text(r.get('path')) for r in roots):
        raise ValueError('Configurazione non valida: "roots" è un elenco di radici con "id" e "path"')
    for key in ('desktop', 'database'):
        if key in config and not text(config[key]):
            raise ValueError(f'Configurazione non valida: "{key}" è un percorso')
    ids = [r['id'] for r in roots]
    if len(ids) != len(set(ids)):
        raise ValueError('ID delle radici duplicati')
    # Percorsi relativi al file di configurazione, non alla cartella corrente; resolve() porta
    # una radice che è un link alla sua destinazione.
    for root in roots:
        root['path'] = str((path.parent / root['path']).resolve())
        if 'depth' in root and (type(root['depth']) is not int or root['depth'] < 1):
            raise ValueError(f"Profondità non valida per {root['id']}: usare un intero >= 1")
    if 'desktop' in config:
        config['desktop'] = str((path.parent / config['desktop']).resolve())
    config['database'] = str(path.parent / config.get('database', '.stato/registro.sqlite'))
    return config

def exclusions(config):
    # Compila le esclusioni una volta per scansione: stessa semantica di fnmatch.fnmatch.
    dirs = {x.casefold() for x in config.get('exclude_dirs', [])}
    def patterns(key):
        return [re.compile(fnmatch.translate(os.path.normcase(p.casefold()))).match for p in config.get(key, [])]
    paths, files = patterns('exclude_paths'), patterns('exclude_files')
    def check(rel):
        parts = rel.split('/')
        if any(p.casefold() in dirs for p in parts):
            return True
        full, name = os.path.normcase(rel.casefold()), os.path.normcase(parts[-1].casefold())
        return any(m(full) for m in paths) or any(m(name) for m in files)
    return check

def root_depth(root):
    # Livelli osservati sotto la radice (None = tutti); recursive=false equivale a depth=1.
    return root.get('depth', None if root.get('recursive', True) else 1)

def walk(root, config, previous, full=False):
    found, blocked, errors = {}, [], []
    skip, depth = exclusions(config), root_depth(root)
    def visit(folder, prefix, level):
        try:
            with os.scandir(folder) as listing:
                entries = sorted(listing, key=lambda e: e.name.casefold())
        except OSError as exc:
            blocked.append(prefix)
            errors.append({'path': str(folder), 'error': str(exc)})
            return
        for entry in entries:
            rel = prefix + '/' + entry.name if prefix else entry.name
            if skip(rel):
                blocked.append(rel)
                continue
            path = Path(entry.path)
            try:
                # Stat aggiornato, non entry.stat(): l'elenco può riportare dimensione e data
                # vecchie per i file ancora aperti in scrittura.
                sig = signature(path, previous.get(rel), full)
            except Linked:
                # Link e junction non si seguono: restano fuori, senza errore.
                blocked.append(rel)
                continue
            except OSError as exc:
                blocked.append(rel)
                errors.append({'path': str(path), 'error': str(exc)})
                continue
            found[rel] = sig
            if sig['kind'] == 'directory' and (depth is None or level < depth):
                visit(path, rel, level + 1)
            elif sig['kind'] == 'directory':
                blocked.append(rel)
    visit(Path(root['path']), '', 1)
    return found, blocked, errors

def beneath(path, prefix):
    return not prefix or path == prefix or path.startswith(prefix + '/')

def clean_prefix(prefix):
    # I percorsi del registro usano '/': accetta anche '\' e le barre in testa o in coda.
    return prefix.replace('\\', '/').strip('/') if prefix else prefix

def matches(row, root=None, prefix=None, depth=None):
    # Filtri comuni a pending e review; depth conta i livelli sotto la radice (1 = solo la radice).
    # Su Windows il prefisso, come i nomi dei file, non distingue maiuscole e minuscole.
    path = row['path']
    if prefix and os.name == 'nt':
        path, prefix = path.casefold(), prefix.casefold()
    return ((not root or row['root'] == root) and (not prefix or beneath(path, prefix))
            and (depth is None or path.count('/') < depth))

def known(con, config, root):
    # Una radice tolta dalla configurazione resta nel registro con i suoi eventi.
    if root and root not in {r['id'] for r in config['roots']} | {r[0] for r in con.execute('SELECT id FROM roots')}:
        raise ValueError(f'Radice sconosciuta: {root}')

def under_any(path, prefixes):
    # Equivale ad any(beneath(path, p) for p in prefixes), in tempo proporzionale alla profondità.
    if '' in prefixes:
        return True
    parts = path.split('/')
    return any('/'.join(parts[:i]) in prefixes for i in range(1, len(parts) + 1))

def scan(config, root_ids=None, full=False):
    unknown = sorted(set(root_ids or ()) - {r['id'] for r in config['roots']})
    if unknown:
        raise ValueError(f"Radice sconosciuta: {', '.join(unknown)}")
    selected = [r for r in config['roots'] if not root_ids or r['id'] in root_ids]
    con = connect(Path(config['database']))
    results = []
    try:
        # Serializza scansioni e revisioni; nessuna scrittura dei file osservati.
        con.execute('BEGIN IMMEDIATE')
        for root in selected:
            root_id = root['id']
            prior_root = con.execute('SELECT * FROM roots WHERE id=?', (root_id,)).fetchone()
            if prior_root and os.path.normcase(prior_root['path']) != os.path.normcase(root['path']):
                raise ValueError(f'Percorso cambiato per {root_id}: usare un nuovo ID radice')
            previous = {r['path']: json.loads(r['sig']) for r in con.execute(
                'SELECT path,sig FROM observed WHERE root=?', (root_id,))}
            found, blocked, errors = walk(root, config, previous, full)
            if '' in blocked:
                if prior_root:
                    con.execute('UPDATE roots SET errors=? WHERE id=?', (packed(errors), root_id))
                results.append({'root': root_id, 'baseline': False, 'observed': 0, 'events': 0, 'errors': errors})
                continue
            baseline = prior_root is None
            if baseline:
                con.execute('INSERT INTO roots(id,path,baseline_at) VALUES(?,?,?)', (root_id, root['path'], stamp()))
            changes = []
            if not baseline:
                for rel, sig in found.items():
                    old = previous.get(rel)
                    if not same(old, sig):
                        changes.append((rel, 'added' if old is None else 'modified', old, sig))
                skip, blocked_set, depth = exclusions(config), set(blocked), root_depth(root)
                for rel, old in previous.items():
                    # Come per le esclusioni: le voci oltre la profondità osservata non diventano cancellazioni.
                    if (rel not in found and not under_any(rel, blocked_set) and not skip(rel)
                            and (depth is None or rel.count('/') < depth)):
                        changes.append((rel, 'deleted', old, None))
            for rel, kind, before, after in changes:
                cursor = con.execute('''INSERT INTO events(root,path,kind,before_sig,after_sig,created)
                    VALUES(?,?,?,?,?,?)''', (root_id, rel, kind, packed(before), packed(after), stamp()))
                new_id = cursor.lastrowid
                con.execute('''UPDATE events SET status='superseded',superseded_by=?
                    WHERE root=? AND path=? AND status='pending' AND id<>?''', (new_id, root_id, rel, new_id))
                if after is None:
                    con.execute('DELETE FROM observed WHERE root=? AND path=?', (root_id, rel))
            for rel, sig in found.items():
                con.execute('INSERT OR REPLACE INTO observed VALUES(?,?,?)', (root_id, rel, packed(sig)))
            con.execute('UPDATE roots SET last_scan=?,errors=? WHERE id=?', (stamp(), packed(errors), root_id))
            results.append({'root': root_id, 'baseline': baseline, 'observed': len(found), 'events': len(changes), 'errors': errors})
        con.commit()
    except BaseException:
        con.rollback()
        raise
    finally:
        con.close()
    return results

def pending(config, root=None, prefix=None, limit=100, depth=None):
    if depth is not None and depth < 1:
        raise ValueError('Profondità non valida: usare un intero >= 1')
    if limit < 0:
        raise ValueError('Limite non valido: usare un intero >= 0')
    prefix = clean_prefix(prefix)
    con = connect(Path(config['database']))
    try:
        known(con, config, root)
        # Dal più recente: con il limite restano in vista i cambiamenti nuovi. I campi di stato e
        # di revisione sono uguali per tutti gli eventi pendenti, quindi restano fuori dall'output.
        all_rows = [dict(r) for r in con.execute('''SELECT id,root,path,kind,before_sig,after_sig,created
            FROM events WHERE status='pending' ORDER BY id DESC''')]
        rows = [r for r in all_rows if matches(r, root, prefix, depth)]
        # Nessun rinomino viene applicato: solo suggerimenti univoci fra eventi pendenti.
        # Indice per impronta costruito una volta: ogni evento è decodificato al massimo una volta.
        # Senza impronta (cartelle, file solo nel cloud) non c'è suggerimento.
        deleted_by_hash, added_by_hash = {}, {}
        for r in all_rows:
            if r['kind'] == 'deleted':
                sha = (json.loads(r['before_sig']) or {}).get('hash')
                if sha:
                    deleted_by_hash.setdefault(sha, []).append(r)
            elif r['kind'] == 'added':
                sha = (json.loads(r['after_sig']) or {}).get('hash')
                if sha:
                    added_by_hash[sha] = added_by_hash.get(sha, 0) + 1
        # Il limite tronca solo l'output: arricchisce soltanto gli elementi mostrati.
        items = rows[:limit]
        for row in items:
            row['before'] = json.loads(row.pop('before_sig'))
            row['after'] = json.loads(row.pop('after_sig'))
            if row['kind'] == 'added' and row['after']['kind'] == 'file':
                sha = row['after']['hash']
                candidates = deleted_by_hash.get(sha, []) if sha else []
                if len(candidates) == added_by_hash.get(sha, 0) == 1:
                    row['possible_rename_from'] = {'root': candidates[0]['root'], 'path': candidates[0]['path'], 'id': candidates[0]['id']}
            row['superseded_events'] = con.execute(
                "SELECT count(*) FROM events WHERE root=? AND path=? AND status='superseded'", (row['root'], row['path'])).fetchone()[0]
        return {'total_pending': len(all_rows), 'matched': len(rows), 'items': items}
    finally:
        con.close()

def review(config, ids, note, root=None, prefix=None):
    if not note.strip():
        raise ValueError('Indicare esito della revisione e note/fonti aggiornate')
    prefix = clean_prefix(prefix)
    by_filter = bool(root or prefix)
    if bool(ids) == by_filter:
        raise ValueError('Indicare gli ID oppure un filtro (--root, --prefix)')
    ids = list(dict.fromkeys(ids))  # un ID ripetuto si chiude una volta sola
    skip, depths = exclusions(config), {r['id']: root_depth(r) for r in config['roots']}
    def observed(row):
        # Percorso ancora osservato: radice configurata, non escluso, entro la profondità.
        depth = depths.get(row['root'], 0)
        return row['root'] in depths and not skip(row['path']) and (depth is None or row['path'].count('/') < depth)
    con = connect(Path(config['database']))
    try:
        known(con, config, root)
        con.execute('BEGIN IMMEDIATE')
        if by_filter:
            # Chiusura per filtro: stessi controlli evento per evento, nella stessa transazione.
            ids = [r['id'] for r in con.execute("SELECT id,root,path FROM events WHERE status='pending' ORDER BY id")
                   if matches(r, root, prefix)]
        for event_id in ids:
            row = con.execute('SELECT * FROM events WHERE id=?', (event_id,)).fetchone()
            if row is None or row['status'] != 'pending':
                raise ValueError(f'Evento {event_id} non pendente; rileggere la coda')
            # Un percorso uscito dalla copertura non ha più uno stato osservato con cui confrontarlo:
            # l'evento si chiude con la sua nota, senza ricontrollare il file.
            if observed(row):
                base = con.execute('SELECT path,errors FROM roots WHERE id=?', (row['root'],)).fetchone()
                if json.loads(base['errors']):
                    raise ValueError(f"Radice {row['root']} con errori di scansione: correggerli o escluderli "
                                     'nella configurazione, poi rieseguire scan prima della revisione')
                path = Path(base['path']) / row['path']
                try:
                    current = signature(path, full=True)
                except FileNotFoundError:
                    # Una radice sparita non equivale alla cancellazione del file.
                    if not Path(base['path']).is_dir():
                        raise ValueError('Radice non disponibile')
                    current = None
                if not same(current, json.loads(row['after_sig'])):
                    raise ValueError(f'Evento {event_id}: file cambiato; scansionare e riesaminare')
            con.execute("UPDATE events SET status='reviewed',reviewed=?,note=? WHERE id=?", (stamp(), note, event_id))
        con.commit()
    except BaseException:
        con.rollback()
        raise
    finally:
        con.close()
    return {'reviewed': len(ids), 'root': root, 'prefix': prefix} if by_filter else {'reviewed': ids}

def status(config):
    con = connect(Path(config['database']))
    try:
        return {'roots': [{**dict(r), 'errors': json.loads(r['errors'])} for r in con.execute('SELECT * FROM roots')],
                'events': {r[0]: r[1] for r in con.execute('SELECT status,count(*) FROM events GROUP BY status')}}
    finally:
        con.close()

LINK = re.compile(r'\]\((<[^>]+>|[^\)\n]+)\)')
FENCE = re.compile(r'(?ms)^```.*?^```[^\n]*')
HEADING = re.compile(r'^#{1,6}\s+(.+)$', re.M)
START = ('AGENTS.md', 'MAPPA.md', 'MANUTENZIONE.md')

def slug(s):
    s = re.sub(r'[^\w\s-]', '', s.lower(), flags=re.UNICODE)
    return s.strip().replace(' ', '-')

def links(config):
    if not config.get('desktop'):
        raise ValueError('Configurazione senza "desktop": serve a links come radice dell\'archivio')
    base = Path(config['desktop']).resolve()
    skip = exclusions(config)
    issues, visited, pages = [], set(), {}
    def page(path):
        # Testo senza blocchi di codice, letto una volta: link e titoli degli esempi non contano.
        if path not in pages:
            try:
                pages[path] = FENCE.sub('', path.read_text(encoding='utf-8-sig'))
            except (OSError, UnicodeDecodeError):
                pages[path] = None
        return pages[path]
    queue = [base / name for name in START if (base / name).is_file()]
    issues += [{'file': str(base), 'target': name, 'error': 'missing'} for name in START if not (base / name).is_file()]
    while queue:
        path = queue.pop()
        if path in visited:
            continue
        # Le pagine in Archivio sono storiche; i percorsi esclusi sono fuori dall'archivio personale.
        rel = path.relative_to(base).as_posix()
        if 'Archivio' in rel.split('/') or skip(rel):
            continue
        visited.add(path)
        if page(path) is None:
            issues.append({'file': str(path), 'target': '', 'error': 'unreadable'})
            continue
        for match in LINK.finditer(page(path)):
            href = match[1].strip('<>')
            if re.match(r'^(https?|mailto|app|codex|memory):', href):
                continue
            ref, _, anchor = href.partition('#')
            dest = (path.parent / unquote(ref)).resolve() if ref else path
            if not dest.exists():
                issues.append({'file': str(path), 'target': href, 'error': 'missing'})
                continue
            markdown = dest.is_file() and dest.suffix.lower() == '.md'
            if anchor and markdown and page(dest) is not None:
                if unquote(anchor) not in {slug(x) for x in HEADING.findall(page(dest))}:
                    issues.append({'file': str(path), 'target': href, 'error': 'anchor'})
            if markdown and dest.is_relative_to(base):
                queue.append(dest)
    return {'checked': len(visited), 'issues': issues, 'visited': sorted(map(str, visited))}

def main():
    # PowerShell e percorsi Unicode: output UTF-8 anche con locale Windows legacy.
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('scan'); p.add_argument('--root', action='append'); p.add_argument('--full', action='store_true')
    p = sub.add_parser('pending'); p.add_argument('--root'); p.add_argument('--prefix'); p.add_argument('--depth', type=int)
    p.add_argument('--limit', type=int, default=100)
    p = sub.add_parser('review'); p.add_argument('ids', nargs='*', type=int); p.add_argument('--root'); p.add_argument('--prefix')
    p.add_argument('--note', required=True)
    sub.add_parser('status'); sub.add_parser('links')
    args = parser.parse_args()
    config = load_config(args.config.resolve())
    code = 0
    if args.command == 'scan':
        out = scan(config, args.root, args.full)
        code = int(any(r['errors'] for r in out))
    elif args.command == 'pending':
        out = pending(config, args.root, args.prefix, args.limit, args.depth)
    elif args.command == 'review':
        out = review(config, args.ids, args.note, args.root, args.prefix)
    elif args.command == 'links':
        out = links(config)
        code = int(bool(out['issues']))
    else:
        out = status(config)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return code

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, sqlite3.Error) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
