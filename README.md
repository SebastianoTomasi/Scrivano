# SistemaConoscenza

Rilevatore locale dei cambiamenti nei file, con una coda persistente da revisionare. Serve a una memoria in Markdown mantenuta da agenti: dice quali file sono cambiati dall'ultima volta, così le note derivate non restano indietro rispetto alle fonti.

Usa Python 3.10+ e solo la libreria standard. Non invia dati in rete, non modifica i file osservati e non interpreta i cambiamenti: quello spetta all'agente.

## Comandi

| Comando | Effetto |
| --- | --- |
| `python controlla.py scan` | Confronta tutte le radici con l'ultimo stato osservato |
| `python controlla.py scan --root Desktop` | Controlla una radice; `--root` è ripetibile |
| `python controlla.py scan --root Desktop --full` | Ricalcola le impronte anche a dimensione e timestamp invariati |
| `python controlla.py pending --root Desktop --prefix Finanze --limit 30` | Filtra la coda; non elimina gli elementi omessi |
| `python controlla.py review 12 13 --note 'esito della revisione'` | Chiude gli ID indicati dopo verifica del file corrente |
| `python controlla.py status` | Mostra radici, errori e conteggi degli eventi |
| `python controlla.py links` | Controlla link locali, ancore Markdown e import CLAUDE.md |

Gli ID sono esempi. L'output è JSON. Senza `--config` si usa `config.json` accanto allo script; per un'istanza altrove: `python controlla.py --config percorso/config.json scan`.

## Configurazione

Parti da [config.example.json](./config.example.json):

- `desktop`: radice della memoria da cui parte `links`.
- `database`: registro SQLite; se relativo, è risolto rispetto al file di configurazione.
- `roots`: radici osservate, ognuna con `id` e `path`. `depth: N` osserva N livelli sotto la radice; `recursive: false` equivale a 1.
- `exclude_dirs`, `exclude_paths`, `exclude_files`: nomi di cartella, percorsi relativi e nomi di file da saltare, con caratteri jolly.

Un nuovo ID radice crea una nuova base; cambiare il percorso di un ID esistente è rifiutato. Cambiare esclusioni o ridurre la profondità modifica la copertura senza produrre false cancellazioni dei percorsi non più osservati e conserva i pendenti. Symlink e junction non vengono seguiti; il filtro dei nomi sensibili non garantisce di riconoscere ogni segreto.

## Ciclo di revisione

1. `scan` registra aggiunte, modifiche e cancellazioni, incluse le cartelle vuote. La prima scansione di una radice crea solo la base osservata e non dichiara letti i documenti.
2. `pending` mostra la coda. Un cambiamento successivo dello stesso percorso supera l'evento precedente e ne crea uno nuovo: rileggi la coda prima di chiudere. Le rinomine sono suggerimenti basati su coppie univoche di impronte tra aggiunte e cancellazioni; non vengono applicate.
3. L'agente legge i file, aggiorna le note e riesegue `scan`: anche le note modificate generano eventi.
4. `review` chiude gli eventi con una nota obbligatoria. Ricontrolla l'impronta del file e rifiuta ID superati, file nuovamente modificati e radici con errori.

Il registro conserva metadati, impronte ed eventi, senza copie dei contenuti. Le note di `review` restano nella tabella `events`.

## Limiti e recupero

| Caso | Comportamento / azione |
| --- | --- |
| Dimensione e timestamp invariati | La scansione veloce può perdere l'edit; usa `--full` se sospetto |
| File creato e cancellato tra scansioni | Non osservabile; il registro non è un backup né una cronologia dei contenuti |
| Radice o sottocartella inaccessibile | Segnala errore, conserva lo stato della parte inaccessibile; le parti leggibili possono essere aggiornate |
| Eccezione o interruzione prima del commit | Annulla la transazione; ripeti la scansione |
| Scansioni/revisioni concorrenti | Scritture serializzate; in caso di lock oltre 15 secondi, riprova |
| Autore o significato di una modifica | Non rilevati dallo strumento |

I comandi restituiscono codice non zero in caso di errore; `links` anche quando trova collegamenti rotti. Il controllo link parte da `AGENTS.md`, `MAPPA.md` e `MANUTENZIONE.md` nella radice `desktop` e segue i Markdown locali collegati, saltando `Archivio` e `.codex-tmp`. Non trova pagine isolate né verifica URL remoti o contenuti.

## Test

```bash
python -m unittest discover -s tests -v
```

I test lavorano solo su cartelle temporanee.
