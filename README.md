# SistemaConoscenza

Strumenti per una memoria in Markdown mantenuta da agenti. `controlla.py` rileva i cambiamenti nei file e li tiene in una coda da revisionare, così le note derivate non restano indietro rispetto alle fonti. `riordina.py` fa l'inventario di una cartella ed esegue un piano di riordino approvato.

Usa Python 3.10+ e solo la libreria standard, senza inviare dati in rete. Le decisioni spettano all'agente: `controlla.py` non modifica i file osservati e non interpreta i cambiamenti, `riordina.py` esegue soltanto il piano che riceve.

L'installazione del sistema su un altro PC è in preparazione: decisioni e ordine dei lavori sono nel [progetto di installazione](docs/progetto-installazione.md).

## Comandi del rilevatore

| Comando | Effetto |
| --- | --- |
| `python controlla.py scan` | Confronta tutte le radici con l'ultimo stato osservato |
| `python controlla.py scan --root Desktop` | Controlla una radice; `--root` è ripetibile |
| `python controlla.py scan --root Desktop --full` | Ricalcola le impronte anche a dimensione e timestamp invariati |
| `python controlla.py pending --root Desktop --prefix Finanze --limit 30` | Filtra la coda, dal cambiamento più recente; non elimina gli elementi omessi |
| `python controlla.py pending --root Desktop --depth 1` | Solo i cambiamenti nella radice; `--depth N` arriva fino a N livelli |
| `python controlla.py review 12 13 --note 'esito della revisione'` | Chiude gli ID indicati dopo verifica del file corrente |
| `python controlla.py review --root Desktop --prefix Personale/Foto --note 'foto censite'` | Chiude tutti gli eventi pendenti del filtro, con gli stessi controlli |
| `python controlla.py status` | Mostra radici, errori e conteggi degli eventi |
| `python controlla.py links` | Controlla link locali e ancore Markdown |

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
2. `pending` mostra la coda dal cambiamento più recente. Un cambiamento successivo dello stesso percorso supera l'evento precedente e ne crea uno nuovo: rileggi la coda prima di chiudere. Le rinomine sono suggerimenti basati su coppie univoche di impronte tra aggiunte e cancellazioni; non vengono applicate.
3. L'agente legge i file, aggiorna le note e riesegue `scan`: anche le note modificate generano eventi.
4. `review` chiude gli eventi indicati per ID o per filtro (`--root`, `--prefix`) con una nota obbligatoria. Ricontrolla l'impronta di ogni file e rifiuta ID superati, file nuovamente modificati e radici con errori; se un solo evento non passa, non chiude nulla.

Il registro conserva metadati, impronte ed eventi, senza copie dei contenuti. Le note di `review` restano nella tabella `events`.

## Riordino

`riordina.py` sposta file e cartelle secondo un piano deciso dall'agente e approvato dall'utente.

| Comando | Effetto |
| --- | --- |
| `python riordina.py inventario C:/Users/utente/Desktop` | Riassume la cartella: voci della radice con conteggi ed estensioni, cartelle-progetto, file solo nel cloud, nomi da segreto, duplicati, file grandi, esclusioni suggerite; `--profondita N` limita la discesa |
| `python riordina.py esegui piano.json --prova` | Controlla il piano senza spostare nulla |
| `python riordina.py esegui piano.json` | Esegue il piano |
| `python riordina.py annulla piano.json` | Riporta indietro le mosse annotate nel giornale |

Il piano è un JSON con la radice e le mosse, in percorsi relativi alla radice:

```json
{"radice": "C:/Users/utente/Desktop",
 "mosse": [{"da": "fattura.pdf", "a": "Finanze/fattura.pdf"},
           {"da": "Foto mare", "a": "Personale/Foto mare"}]}
```

- Le mosse descrivono l'albero di partenza: origini e destinazioni non si ripetono, non si sovrappongono e restano dentro la radice. Le cartelle mancanti vengono create.
- Prima di spostare, lo script controlla l'intero piano: con un solo problema non sposta nulla. Non sovrascrive, non cancella e lascia a mano link e junction.
- Durante l'esecuzione si ferma al primo errore, per esempio un file aperto. Rilanciato sullo stesso piano, salta le mosse già fatte e riprende.
- Ogni mossa è annotata in `piano.giornale.jsonl`, accanto al piano, prima di essere eseguita. `annulla` ripercorre il giornale al contrario, rimuove le cartelle create se sono rimaste vuote e lascia dove sono i file aggiunti dopo; a lavoro completo rinomina il giornale.
- `riordina.lock`, accanto al piano, impedisce due esecuzioni insieme. Se resta dopo un'interruzione, verifica lo stato della cartella e poi cancellalo.
- L'esecuzione confronta il numero di file prima e dopo: se cambia, qualcos'altro ha toccato la cartella nel frattempo.

Riordina prima della prima scansione di `controlla.py`: dopo, ogni spostamento diventa una cancellazione più un'aggiunta da revisionare.

## Limiti e recupero

| Caso | Comportamento / azione |
| --- | --- |
| Dimensione e timestamp invariati | La scansione veloce può perdere l'edit; usa `--full` se sospetto |
| File solo nel cloud (OneDrive) | Confrontati su dimensione e data senza leggerli, quindi senza scaricarli; niente suggerimenti di rinomina |
| File creato e cancellato tra scansioni | Non osservabile; il registro non è un backup né una cronologia dei contenuti |
| Radice o sottocartella inaccessibile | Segnala errore, conserva lo stato della parte inaccessibile; le parti leggibili possono essere aggiornate |
| Eccezione o interruzione prima del commit | Annulla la transazione; ripeti la scansione |
| Scansioni/revisioni concorrenti | Scritture serializzate; in caso di lock oltre 15 secondi, riprova |
| Autore o significato di una modifica | Non rilevati dallo strumento |

I comandi restituiscono codice non zero in caso di errore; `links` anche quando trova collegamenti rotti, `riordina.py` anche quando il piano ha problemi o il conteggio dei file cambia. Il controllo link parte da `AGENTS.md`, `MAPPA.md` e `MANUTENZIONE.md` nella radice `desktop` e segue i Markdown locali collegati, saltando le cartelle `Archivio` e i percorsi esclusi dalla configurazione. Non trova pagine isolate né verifica URL remoti o contenuti.

## Test

```bash
python -m unittest discover -s tests -v
```

I test lavorano solo su cartelle temporanee.
