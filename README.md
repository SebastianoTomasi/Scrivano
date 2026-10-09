# Scrivano

Scrivano mette in ordine il Desktop e ne fa un archivio personale che il tuo agente, Claude Code o Codex, sa consultare e tenere aggiornato. Ogni cartella ha una guida che dice cosa contiene; un rilevatore annota i file che cambiano, così l'agente sa cosa rileggere.

## Per cominciare

Serve Windows 11 con Claude Code o Codex. Se manca Python, lo installa l'agente.

Apri l'agente sul tuo Desktop, in modalità auto (Claude Code) o con accesso completo (Codex), e scrivigli *Installa Scrivano da* seguito dall'indirizzo di questo repository.

L'agente guarda cosa c'è sul Desktop, ti propone un'organizzazione per argomenti e la applica quando sei d'accordo. Se preferisci non spostare nulla, il sistema si installa sulle cartelle che hai già.

## Uso quotidiano

- Per le cose personali apri l'agente sul Desktop.
- Lascia i file nuovi sul Desktop: l'agente propone dove metterli, al massimo una volta per sessione.
- Chiedi quello che ti serve, per esempio "dov'è il contratto d'affitto?" o "quanto ho speso di luce quest'anno?": l'agente parte dalla mappa e dalle guide.
- Quando apri l'agente, un rilevatore gli dice quali file sono cambiati dall'ultima volta. Non gira in background e non devi occupartene.

Per aggiornare il sistema scrivi all'agente *aggiorna Scrivano*.

## Domande frequenti

- **Cosa legge l'agente?** Quello che gli serve per orientarsi, tranne chiavi, `.env` e file di password, che ti segnala senza aprirli. Ciò che legge passa al fornitore del modello: Anthropic per Claude, OpenAI per Codex.
- **E la memoria di Claude o Codex?** Resta com'è e ricorda come preferisci lavorare. L'archivio tiene ciò che si sa dei tuoi documenti: sta sul Desktop, lo leggi anche tu e lo usano entrambi gli agenti.
- **Si può tornare indietro?** Sì: ogni spostamento è annotato e l'agente può annullarlo.
- **Il Desktop è su OneDrive.** Funziona: i file solo nel cloud vengono controllati senza scaricarli.
- **Alcune icone non si spostano.** Sono in `Public\Desktop`, condiviso tra gli utenti del PC: servono i permessi di amministratore, quindi restano dove sono.
- **Word non trova più un documento recente.** È normale dopo il riordino: aprilo dalla nuova cartella.
- **Disinstallare.** Cancella `Documenti\Scrivano`, poi sul Desktop `AGENTS.md`, `MAPPA.md`, `MANUTENZIONE.md` e le `GUIDA.md` delle cartelle. Se usi Codex, cancella anche `.codex-root` e togli `".codex-root"` da `project_root_markers` in `~/.codex/config.toml`. Il riordino e le note restano.

## Per l'agente

Se l'utente ti chiede di installare il sistema, segui [INSTALLA.md](./INSTALLA.md); per aggiornarlo, [AGGIORNA.md](./AGGIORNA.md).

## Strumenti

`controlla.py` rileva i cambiamenti nei file e li tiene in una coda da revisionare, così le note derivate non restano indietro rispetto alle fonti. `riordina.py` fa l'inventario di una cartella ed esegue un piano di riordino approvato. Usano Python 3.10+ e solo la libreria standard, senza inviare dati in rete. Le decisioni spettano all'agente: `controlla.py` non modifica i file osservati e non interpreta i cambiamenti, `riordina.py` esegue soltanto il piano che riceve.

Le decisioni di progetto sono nel [progetto di installazione](docs/progetto-installazione.md); i modelli delle pagine del Desktop e il catalogo dei domini in [modelli](./modelli/); le novità di ogni versione nel [CHANGELOG](./CHANGELOG.md).

### Comandi del rilevatore

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

Gli ID sono esempi. `--prefix` è un percorso relativo alla radice, con `/` o `\`. L'output è JSON. Senza `--config` si usa `config.json` accanto allo script; per un'istanza altrove: `python controlla.py --config percorso/config.json scan`.

### Configurazione

Parti da [config.example.json](./config.example.json). I percorsi relativi sono risolti rispetto al file di configurazione.

- `desktop`: radice dell'archivio da cui parte `links`.
- `database`: registro SQLite, di norma `.stato/registro.sqlite`.
- `roots`: radici osservate, ognuna con `id` e `path`. `depth: N` osserva N livelli sotto la radice; `recursive: false` equivale a 1.
- `exclude_dirs`: nomi esatti di cartelle (o file) da saltare a qualsiasi livello.
- `exclude_paths`: percorsi relativi a ciascuna radice; `exclude_files`: nomi di file. Entrambi accettano i caratteri jolly `*` e `?`.

Le esclusioni non distinguono maiuscole e minuscole.

Un nuovo ID radice crea una nuova base; cambiare il percorso di un ID esistente è rifiutato. Cambiare esclusioni o ridurre la profondità modifica la copertura senza produrre false cancellazioni dei percorsi non più osservati e conserva i pendenti. Symlink e junction non vengono seguiti; il filtro dei nomi sensibili non garantisce di riconoscere ogni segreto.

### Ciclo di revisione

1. `scan` registra aggiunte, modifiche e cancellazioni, incluse le cartelle vuote. La prima scansione di una radice crea solo la base osservata e non dichiara letti i documenti.
2. `pending` mostra la coda dal cambiamento più recente. Un cambiamento successivo dello stesso percorso supera l'evento precedente e ne crea uno nuovo: rileggi la coda prima di chiudere. Le rinomine sono suggerimenti basati su coppie univoche di impronte tra aggiunte e cancellazioni; non vengono applicate.
3. L'agente legge i file, aggiorna le note e riesegue `scan`: anche le note modificate generano eventi.
4. `review` chiude gli eventi indicati per ID o per filtro (`--root`, `--prefix`) con una nota obbligatoria. Ricontrolla l'impronta di ogni file e rifiuta ID superati, file nuovamente modificati e radici con errori; se un solo evento non passa, non chiude nulla.

Il registro conserva metadati, impronte ed eventi, senza copie dei contenuti. Le note di `review` restano nella tabella `events`.

### Riordino

`riordina.py` sposta file e cartelle secondo un piano deciso dall'agente e approvato dall'utente.

| Comando | Effetto |
| --- | --- |
| `python riordina.py inventario C:/Users/utente/Desktop` | Riassume la cartella: voci della radice con conteggi ed estensioni, cartelle-progetto, file solo nel cloud, nomi da segreto, duplicati, file grandi, esclusioni suggerite; `--profondita N` limita la discesa, `--max N` le voci elencate (300) |
| `python riordina.py esegui piano.json --prova` | Controlla il piano senza spostare nulla |
| `python riordina.py esegui piano.json` | Esegue il piano |
| `python riordina.py annulla piano.json` | Riporta indietro le mosse annotate nel giornale |

Il piano è un JSON con la radice, le mosse e, se servono, le cartelle-contenitore da togliere quando restano vuote. I percorsi sono relativi alla radice:

```json
{"radice": "C:/Users/utente/Desktop",
 "mosse": [{"da": "fattura.pdf", "a": "Finanze/fattura.pdf"},
           {"da": "Nuova cartella/Foto mare", "a": "Personale/Foto mare"}],
 "vuote": ["Nuova cartella"]}
```

- Le mosse descrivono l'albero di partenza: origini e destinazioni non si ripetono, non si sovrappongono e restano dentro la radice. Le cartelle mancanti vengono create. Un cambio di sole maiuscole passa da un nome intermedio, in due piani.
- Dopo le mosse, ogni cartella di `vuote` rimasta davvero vuota viene tolta; una con qualcosa dentro resta e compare in `cartelle_rimaste`.
- Prima di spostare, lo script controlla l'intero piano: con un solo problema non sposta nulla. Non sovrascrive, non cancella e lascia a mano link simbolici e junction, insieme a ciò che si raggiunge attraverso di loro; i collegamenti `.lnk` e `.url` sono file normali.
- Durante l'esecuzione si ferma al primo errore, per esempio un file aperto. Rilanciato sullo stesso piano, salta le mosse che il giornale registra come fatte e riprende. Un'origine assente con la destinazione già occupata, senza traccia nel giornale, è un problema del piano.
- Ogni mossa è annotata in `piano.giornale.jsonl`, accanto al piano, prima di essere eseguita: ogni piano ha il suo giornale, quindi una correzione successiva va in un piano nuovo, con un altro nome. `annulla` ripercorre il giornale al contrario: ricrea le cartelle tolte, riporta i file, rimuove le cartelle create se sono rimaste vuote e lascia dove sono i file aggiunti dopo; a lavoro completo rinomina il giornale.
- `riordina.lock`, accanto al piano, impedisce due esecuzioni insieme. Se resta dopo un'interruzione, verifica lo stato della cartella e poi cancellalo.
- L'esecuzione confronta il numero di file prima e dopo, contando anche l'interno di `.git` e simili, che l'inventario invece salta: se cambia, qualcos'altro ha toccato la cartella nel frattempo.

Riordina prima della prima scansione di `controlla.py`: dopo, ogni spostamento diventa una cancellazione più un'aggiunta da revisionare.

### Limiti e recupero

| Caso | Comportamento / azione |
| --- | --- |
| Dimensione e timestamp invariati | La scansione veloce può perdere l'edit; usa `--full` se sospetto |
| File solo nel cloud (OneDrive) | Confrontati su dimensione e data senza leggerli, quindi senza scaricarli; niente suggerimenti di rinomina |
| File creato e cancellato tra scansioni | Non osservabile; il registro non è un backup né una cronologia dei contenuti |
| Radice o sottocartella inaccessibile | Segnala errore, conserva lo stato della parte inaccessibile; le parti leggibili possono essere aggiornate. Finché l'errore resta, `review` rifiuta gli eventi di quella radice: correggi la causa o escludi il percorso |
| Eccezione o interruzione prima del commit | Annulla la transazione; ripeti la scansione |
| Scansioni/revisioni concorrenti | Scritture serializzate; in caso di lock oltre 15 secondi, riprova |
| Autore o significato di una modifica | Non rilevati dallo strumento |

I comandi restituiscono codice non zero in caso di errore; `scan` anche quando una radice ha errori, `links` anche quando trova collegamenti rotti, `riordina.py` anche quando il piano ha problemi, il conteggio dei file cambia o l'inventario non legge qualcosa. Il controllo link parte da `AGENTS.md`, `MAPPA.md` e `MANUTENZIONE.md` nella radice `desktop`, segnala quelle mancanti e segue i Markdown locali collegati, saltando le cartelle `Archivio`, i percorsi esclusi dalla configurazione e i blocchi di codice. Non trova pagine isolate né verifica URL remoti o contenuti.

### Test

```bash
python -m unittest discover -s tests -v
```

I test lavorano solo su cartelle temporanee. Per provare l'installazione completa, `tests/desktop_finto.py` genera un Desktop disordinato finto e poi verifica il risultato:

```bash
python tests/desktop_finto.py genera C:/Prove/Uno --strumento .
python tests/desktop_finto.py verifica C:/Prove/Uno
```

Poi chiedi all'agente di seguire `INSTALLA.md` in modalità prova, indicandogli `C:/Prove/Uno/Desktop` come Desktop e `C:/Prove/Uno/Documenti/Scrivano` come strumento.
