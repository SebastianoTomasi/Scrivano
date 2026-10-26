# Tecnologie di Scrivano

**Status:** proposed

## Scope

Elenca linguaggi, ambienti e servizi che Scrivano usa, con le versioni, e le regole che ogni componente eredita. Perché gli script usano solo la libreria standard sta in [Dipendenze tra componenti](../architecture/sistema-e-componenti.md#dipendenze-tra-componenti).

## Dependencies

- [Utente principale](../product/scopo-e-persone.md#utente-principale) — l'utente può non avere Python né git: l'inventario tiene conto di come l'agente li procura.
- [Promessa di compatibilità](../product/compatibilita-e-collaudo.md#promessa-di-compatibilità) — piattaforme e versione minima di Python fanno parte di ciò che non si restringe.

## Inventario

Risponde a `stack-inventory`.

| Tecnologia | Ruolo | Versione |
| --- | --- | --- |
| Python (CPython) | Esegue gli script e i test | 3.10 o successivo; si scrive per la 3.10 |
| Libreria standard di Python | Tutto ciò che serve agli script: `sqlite3`, `hashlib`, `json`, `argparse`, `unicodedata`, `fnmatch` | Quella della 3.10 |
| SQLite | Registro del rilevatore, tramite `sqlite3` | Quella inclusa in Python |
| `unittest` | Test | Quello della libreria standard |
| Windows 11 | Piattaforma supportata, con NTFS e OneDrive | 11 |
| macOS | Piattaforma supportata, con APFS, iCloud e altri File Provider | Non fissata |
| Claude Code | Agente supportato; legge `AGENTS.md` | 2.1.277 o successiva |
| Codex | Agente supportato; legge `AGENTS.md`, con `.codex-root` per le sottocartelle | Non fissata |
| git | Porta e aggiorna lo strumento; facoltativo | Qualsiasi |
| winget, python.org, Homebrew | Installano Python quando manca: winget su Windows, python.org o Homebrew su macOS | Su Windows `Python.Python.3.14` |
| GitHub | Ospita il repository, oggi privato e poi pubblico con licenza MIT | — |

Linux non è una piattaforma supportata: procedure e test di piattaforma non lo considerano.

## Regole comuni

Risponde a `stack-shared-defaults`.

- **Nessuna dipendenza esterna.** `pyproject.toml` dichiara `dependencies = []`: non c'è niente da fissare. Una libreria esterna sarebbe una scelta da discutere, perché l'utente dovrebbe installarla.
- **Nessun accesso alla rete.** Vale per gli script e per i test.
- **Configurazione.** Il rilevatore legge `config.json` accanto allo script, o quello indicato con `--config`; i percorsi relativi partono dal file e `~` vale la cartella dell'utente. Il riordinatore non ha configurazione: riceve la cartella o il piano da riga di comando. I JSON si leggono in UTF-8, anche con BOM.
- **Versione.** La versione di un'istanza è la data dei modelli nel CHANGELOG, non il campo `version` di `pyproject.toml`.
- **Python sul Mac.** Il `python3` di Apple è spesso la 3.9: le pagine del Desktop chiamano Python con il percorso completo di quello giusto (`{{python}}`).
