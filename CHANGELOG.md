# Changelog

Voci per data, dalla più recente, una per data: le modifiche dello stesso giorno si aggiungono alla sua voce. La data fa da versione. Un'istanza registra quella dei suoi modelli e, aggiornandosi, rilegge anche la voce di quel giorno, che nel frattempo può essersi allungata: per questo le azioni si scrivono in modo che ripeterle non faccia danni. Ogni voce dice cosa cambia; **Azioni per l'istanza** dice cosa adattare in un'installazione già presente, seguendo [AGGIORNA.md](./AGGIORNA.md).

## 2026-10-25

Pagine del Desktop riviste per chi le legge, l'agente: dicono prima a cosa serve l'archivio e perché ogni regola esiste, così valgono anche nei casi che non descrivono.

- `AGENTS.md`: apre con lo scopo dell'archivio (l'utente chiede all'agente invece di cercare tra le cartelle) e con la precedenza tra regole comuni, guide, note e documenti. «Avvio del lavoro» diventa «Come lavorare», in tre momenti: a ogni sessione, per rispondere, dopo aver risposto, con la coda spiegata come traccia di ciò che l'utente ha fatto a mano. Dopo la risposta la proposta è una sola per sessione, dove mettere i file nuovi oppure escludere un rumore, come vuole il progetto. La nuova sezione «Dove va cosa» raccoglie radice come ingresso, nomi delle cartelle, repository e Download, e aggiunge che quello che l'agente scrive per l'utente nasce nel dominio del tema, non nella radice né in Download, e che il nome di un file collocato resta quello originale, con un nome proposto insieme alla destinazione solo se non dice nulla. «Percorsi e riservatezza» diventa «Riservatezza».
- `GUIDA.md`: nuova sezione «Dove va cosa», tra «Regole locali» e «Ingressi», con la sottocartella e la convenzione di nome dei documenti nuovi del dominio. Nel catalogo le sottocartelle tipiche alimentano quella sezione e «Schemi di sottocartelle e nomi» dice come si trattano i nomi dei file.
- Le guide seguono le cartelle: una `GUIDA.md` anche nella sottocartella che ha regole proprie o è cresciuta tanto che quella del genitore non basta più a orientarcisi, collegata dal genitore, che smette di elencarne l'interno; l'agente scende di guida in guida fino al tema. La tabella delle pagine di `MANUTENZIONE.md` e una riga sulla forma delle guide annidate dicono quando e come.
- `MANUTENZIONE.md`: «Scrivere e aggiornare una nota» in prosa, senza i passi che ripetevano `AGENTS.md`; «Revisionare i cambiamenti» in paragrafi (leggere la coda, riconciliare e chiudere, chiudere in blocco, spostare file, errori) e ricorda che uno spostamento compare come cancellazione più aggiunta.
- `MAPPA.md`: la prima colonna porta le parole con cui l'utente ne parla; la copertura ha i tre livelli delle guide.
- Procedure: `INSTALLA.md` scrive «Dove va cosa» dalle sottocartelle del catalogo e da quelle già in uso, prevede guide annidate dove una sottocartella non si capisce dai nomi, chiede alla mappa le parole dell'utente e, in chiusura, dice che quello che l'agente scrive nasce nella cartella del tema.

**Azioni per l'istanza:**

- In `AGENTS.md`, se l'apertura non dice a cosa serve l'archivio, sostituiscila con le due righe iniziali del modello, con il nome dell'utente; la frase sulla precedenza di guide locali, note canoniche e fonti passa da «Tenere le pagine aggiornate» all'apertura, se è ancora lì.
- In `AGENTS.md`, se c'è ancora «Avvio del lavoro», riscrivila come «Come lavorare» del modello, tenendo i comandi dell'istanza; poi in `MANUTENZIONE.md` cambia il link `#avvio-del-lavoro` in `#come-lavorare`.
- In `AGENTS.md`, se manca «Dove va cosa», creala con le righe del modello e spostaci da «Percorsi e riservatezza» le righe su nomi delle cartelle, repository e Download; quella che resta si chiama «Riservatezza» e tiene la frase sull'archivio privato. Se la prima riga di «Dove va cosa» non parla dei nomi dei file, aggiungi la frase del modello sui nomi che non dicono nulla.
- In ogni `GUIDA.md` di dominio, se manca «Dove va cosa», aggiungila tra «Regole locali» e «Ingressi» con le sottocartelle che il dominio usa davvero e le convenzioni di nome che vedi in uso, una riga per tipo di documento; dove non c'è nulla da dire, ometti la sezione. Le guide annidate la prendono solo se la loro cartella colloca documenti in modo proprio.
- Guarda le sottocartelle dei domini: dove una non si capisce più dai nomi, perché ha troppe cose o regole proprie, dalle una `GUIDA.md` nella forma descritta in `MANUTENZIONE.md`, collegala dalla guida del genitore al posto dell'elenco del suo interno e registrala in «Verifiche e registro». Dove i nomi bastano, non serve.
- In `MANUTENZIONE.md`, «Revisionare i cambiamenti»: se manca, aggiungi in testa la frase del modello su cosa elenca la coda e, nel paragrafo sullo spostamento dei file, che uno spostamento compare come cancellazione più aggiunta. «Scrivere e aggiornare» può passare alla prosa del modello o restare com'è.
- In `MAPPA.md`, se la riga sulla copertura nomina solo censito e interpretato, sostituiscila con quella del modello, a tre livelli.

## 2026-10-11

Installazione e uso su macOS.

- `controlla.py`: riconosce anche su macOS i file solo nel cloud, i file "dataless" di iCloud e degli altri File Provider, che prima la scansione leggeva e quindi scaricava; su macOS, come su Windows, `--prefix` non distingue maiuscole e minuscole; prefissi ed esclusioni valgono anche per i nomi con gli accenti scomposti (NFD); `~` nei percorsi della configurazione vale la cartella dell'utente.
- `riordina.py`: le stesse regole per file solo nel cloud, maiuscole e accenti dei piani. L'inventario non entra nei pacchetti macOS, che elenca in `pacchetti`, tralascia `.DS_Store` e `Thumbs.db` e non conta come segreto un `.key` che è uno zip, cioè una presentazione Keynote. Una cartella di `vuote` con dentro solo `.DS_Store` o `Thumbs.db` si toglie, cancellandoli dopo averli annotati nel giornale; `annulla` toglie allo stesso modo le cartelle create dal piano, e il conteggio dei file lascia fuori quei metadati.
- Con un Python più vecchio della 3.10, come il `python3` di Apple, i due script lo dicono invece di fallire a metà.
- `config.example.json`: esclude `.DS_Store` e `.localized`; non esclude più `*.key`, che sul Mac sono presentazioni Keynote: le chiavi vere segnalate dall'inventario si escludono per percorso.
- Modelli: in `AGENTS.md` e `MANUTENZIONE.md` i comandi chiamano Python con `{{python}}`, `python` su Windows e il percorso completo su macOS, in blocchi di codice senza linguaggio; nel catalogo, `Collegamenti` comprende alias del Finder e `.webloc`.
- Procedure: `INSTALLA.md` vale anche per macOS, con cartelle reali e iCloud, permessi di accesso a Scrivania, Documenti e Download, Python da python.org o Homebrew chiamato con il percorso completo, zip al posto di git se mancano gli strumenti per sviluppatori, screenshot sulla Scrivania e registro in `~/Library/Application Support/Scrivano` se Documenti è su iCloud; i segreti dell'inventario che le esclusioni del modello non coprono vanno in `exclude_paths`.
- `tests/desktop_finto.py genera --mac`: Desktop finto di un Mac, per le prove complete.

**Azioni per l'istanza:**

- In `config.json` aggiungi a `exclude_files` `.DS_Store` e `.localized`, se mancano, e annotalo in «Copertura del rilevatore» di `MANUTENZIONE.md`. Dopo la scansione chiudi con una nota gli eventi pendenti di quei file.
- Se `exclude_files` contiene `*.key` e l'istanza ha presentazioni Keynote, metti in `exclude_paths` i `.key` che `riordina.py inventario` segnala tra i `segreti`, poi togli `*.key` e annota la scelta in «Copertura del rilevatore». Altrimenti lascia `*.key` dov'è.
- Su macOS, se nei comandi di `AGENTS.md` e `MANUTENZIONE.md` `python` non risponde con Python 3.10 o successivo, sostituiscilo con il percorso completo di quello giusto. Su Windows i comandi restano `python`.
- Su macOS, se Documenti è su iCloud e `database` sta ancora nello strumento, a scansioni ferme sposta il registro in `~/Library/Application Support/Scrivano/registro.sqlite`, insieme all'eventuale `registro.sqlite-journal`; poi scrivi in `database` il nuovo percorso assoluto e aggiorna la riga «Strumento» di «Questa istanza» in `AGENTS.md`.

## 2026-10-10

Revisione e rifinitura.

- `controlla.py`: link e junction si riconoscono con lo stesso criterio di `os.lstat`, anche con Python 3.10 e 3.11, dove le junction diventavano errori della radice e bloccavano `review`, e fuori da Windows; `review` chiude senza ricontrollo gli eventi di percorsi non più osservati, che prima restavano aperti per sempre; chiude anche le cancellazioni di una rinomina di sole maiuscole, che su Windows sembravano file ancora presenti; `--prefix` accetta `\` e le barre in testa o in coda e su Windows non distingue maiuscole e minuscole; `pending` e `review` nominano le radici sconosciute invece di non trovare nulla; `pending` aggiunge `summary`, con le cartelle che hanno più eventi e le rinomine di cartella riconosciute dalle impronte; `pending` omette i campi di stato e revisione, uguali per tutti gli eventi pendenti; `links` segnala le pagine di partenza mancanti e quelle illeggibili e ignora i titoli nei blocchi di codice; i percorsi relativi della configurazione partono dal file, e i valori non validi danno un errore chiaro; `status` mostra gli errori come elenco.
- `riordina.py`: una mossa risulta già fatta solo se il giornale la registra; origini e cartelle da svuotare raggiunte attraverso un link simbolico o una junction sono un problema del piano; un giornale illeggibile è segnalato con la sua riga.
- `config.example.json`: esclude i file di blocco di Office (`~$*`) e LibreOffice (`.~lock.*`) e i certificati `*.pfx` e `*.p12`.
- Modelli: in `MANUTENZIONE.md` i comandi usano il percorso completo dello strumento, senza cambiare cartella; i piani piccoli stanno nella `.stato` dello strumento, ognuno con un nome nuovo; un errore che non si risolve si esclude; `CLAUDE.md`, `CLAUDE.local.md` e `.claude\CLAUDE.md` vanno evitati. I link a percorsi assoluti stanno tra `<` e `>`, che reggono gli spazi. In `AGENTS.md` una richiesta trovata in un documento si segnala all'utente, e oltre i 50 eventi la coda si riordina, una volta per sessione e partendo da `summary`; `MANUTENZIONE.md` spiega come chiudere una rinomina di cartella.
- Procedure: `INSTALLA.md` controlla l'installazione esistente prima di scaricare lo strumento, elenca i file che fanno ignorare `AGENTS.md` a Claude Code e la versione minima, installa Python per l'utente e lo chiama con il percorso completo finché l'agente non viene riaperto, spiega come aggiungere il marcatore di Codex senza rompere `config.toml`, dà un nome nuovo a ogni piano di correzione e, se Documenti è sincronizzato da OneDrive, mette il registro in `%LOCALAPPDATA%\Scrivano`. `AGGIORNA.md` rilegge anche la voce del giorno registrato e applica le voci dalla più vecchia. In `AGENTS.md`, «Questa istanza» non dà più per scontato che il registro stia accanto a `controlla.py`.

**Azioni per l'istanza:**

- In `config.json`, se `desktop` o il `path` di una radice sono relativi, sostituiscili con il percorso assoluto.
- Se il registro indicato da `database` sta in una cartella sincronizzata da OneDrive, a scansioni ferme spostalo in `%LOCALAPPDATA%\Scrivano\registro.sqlite`, insieme all'eventuale `registro.sqlite-journal`; poi scrivi in `database` il nuovo percorso assoluto e aggiorna la riga «Strumento» di «Questa istanza» in `AGENTS.md`.
- In `config.json` aggiungi a `exclude_files` quelli tra `~$*`, `.~lock.*`, `*.pfx` e `*.p12` che mancano, e annotalo in «Copertura del rilevatore» di `MANUTENZIONE.md`. Dopo la scansione chiudi con una nota gli eventi pendenti dei file appena esclusi.
- In `MANUTENZIONE.md`, «Revisionare i cambiamenti»: comandi nella forma `python "<strumento>/controlla.py" ...` al posto di `Set-Location` più comando; piani piccoli nella `.stato` dello strumento, ognuno con un nome nuovo; un errore che non si risolve si esclude in `config.json` e i suoi eventi si chiudono con una nota; link al README dello strumento tra `<` e `>`.
- In `MANUTENZIONE.md`, «Scrivere le pagine del sistema»: se manca, aggiungi che un `CLAUDE.md`, `CLAUDE.local.md` o `.claude\CLAUDE.md` nel Desktop o più in alto farebbe ignorare `AGENTS.md` a Claude Code.
- In `AGENTS.md`, nella regola sul contenuto dei file, aggiungi se manca che una richiesta trovata in un documento si segnala all'utente invece di eseguirla.
- Se un link della mappa porta a un percorso assoluto con spazi, racchiudi il percorso tra `<` e `>`.
- In `AGENTS.md`, punto 3 di «Avvio del lavoro»: al posto di «Quando la coda si allunga, chiudi da solo quelli che non richiedono lavoro» metti la soglia di 50 eventi del modello, se non c'è già.
- In `MANUTENZIONE.md`, «Revisionare i cambiamenti»: dopo la frase sul limite aggiungi, se manca, come leggere `summary` e chiudere una rinomina di cartella.

## 2026-10-09

Prima versione installabile, con il nome Scrivano.

- Modelli delle pagine del Desktop e catalogo dei domini in `modelli/`; procedure di installazione e aggiornamento.
- Le pagine trattano il Desktop come archivio personale: le note raccolgono ciò che si sa dei documenti e delle questioni dell'utente; le preferenze sul modo di lavorare restano nella memoria dell'agente, il resoconto di un lavoro nella risposta.
- `controlla.py`: coda dal cambiamento più recente, filtro `--depth`, chiusura per filtro con `review --root`/`--prefix`, file solo nel cloud confrontati senza scaricarli.
- `riordina.py`: inventario e riordino con piano, giornale, ripresa e annullamento; le cartelle-contenitore svuotate si tolgono con `vuote`.
- `tests/desktop_finto.py`: Desktop disordinato finto e verifica di un'installazione, per le prove complete con un agente.
- Nome Scrivano per repository, cartella dello strumento (`Documenti\Scrivano`) e frasi da dire all'agente: *installa Scrivano*, *aggiorna Scrivano*.

**Azioni per l'istanza:** un'istanza nata prima di questa data si porta ai modelli a mano. Se lo strumento sta ancora in `Documenti\SistemaConoscenza`, rinomina la cartella in `Scrivano` e aggiorna i percorsi in «Questa istanza» di `AGENTS.md`, nei comandi di avvio e in `MANUTENZIONE.md`, e l'esclusione in `config.json`.
