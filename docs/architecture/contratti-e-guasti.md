# Contratti e guasti di Scrivano

**Status:** proposed

## Scope

Dice cosa garantiscono i flussi che attraversano il confine del sistema, quali operazioni sono atomiche e cosa si può osservare a metà di una che non lo è, e cosa succede quando qualcosa da cui Scrivano dipende non risponde. La sintassi di comandi, configurazione e piano sta nel [README](../../README.md#strumenti); le meccaniche che realizzano queste garanzie in [Registro e giornale](../implementation/registro-e-giornale.md).

## Dependencies

- [Confine del sistema](sistema-e-componenti.md#confine-del-sistema) — i flussi sono quelli verso i sistemi elencati lì.
- [Proprietà dei dati](dati-e-fiducia.md#proprietà-dei-dati) — atomicità e ripresa proteggono i dati che rilevatore e riordinatore possiedono.
- [Promessa di compatibilità](../product/compatibilita-e-collaudo.md#promessa-di-compatibilità) — le garanzie degli script sono parte di ciò che non si rompe.

## Flussi verso l'esterno

Risponde a `cross-system-flows`.

**Agente → script.** L'agente lancia `controlla.py` e `riordina.py` da riga di comando. Ogni comando risponde con un JSON su stdout. Un errore che impedisce il comando esce con codice 2 e un JSON `{"error": ...}` su stderr. Un problema trovato dal comando esce con codice 1 e il resoconto su stdout: `scan` quando una radice ha errori, `links` quando un collegamento è rotto, `riordina.py` quando il piano ha problemi, il conteggio dei file cambia o l'inventario non legge qualcosa. L'agente può contare su queste garanzie:

- il rilevatore non modifica, non sposta e non scarica i file osservati;
- la prima scansione di una radice crea la base e non dichiara letto nessun documento;
- un evento chiuso corrisponde al file com'era quando l'agente l'ha letto;
- i suggerimenti di rinomina, di file e di cartella, sono solo suggerimenti: nessuno viene applicato;
- il riordinatore esegue solo il piano ricevuto, non sovrascrive, non cancella altro che `.DS_Store` e `Thumbs.db` nelle cartelle che il piano toglie, e annota ogni mossa prima di farla;
- link simbolici e junction non si seguono e non si spostano.

**Agente ↔ pagine.** Claude Code dalla versione 2.1.277 e Codex leggono `AGENTS.md` nella radice del Desktop. Le guide sono file Markdown raggiunti dai link della mappa, non altri `AGENTS.md`: Codex non carica gli `AGENTS.md` sotto la cartella di avvio, Claude Code li caricherebbe solo leggendo un file lì dentro, e un link funziona allo stesso modo con entrambi ([ADR 0002](../adr/0002-un-solo-agents-md-e-guide-collegate.md)). Con Codex, `.codex-root` nella radice e il marcatore in `project_root_markers` fanno leggere `AGENTS.md` anche a una sessione aperta in una sottocartella.

**Repository → istanza.** Lo strumento arriva con `git clone` o con lo zip e si aggiorna con `git pull` o con un nuovo zip che lascia `config.json` e `.stato/`. Le pagine del Desktop si aggiornano solo tramite l'agente, con le azioni del CHANGELOG.

**File system e cloud.** Un file solo nel cloud si confronta su dimensione e data, senza leggerlo e quindi senza scaricarlo. Il registro sta in una cartella locale: un client di sincronizzazione potrebbe bloccarlo o duplicarlo.

## Atomicità e stati intermedi

Risponde a `consistency-boundaries`.

- **`scan` è atomica.** Tutte le radici selezionate si aggiornano in una transazione: un'eccezione o un'interruzione prima del commit non lascia traccia, e la scansione si ripete.
- **`review` è atomica.** Se un solo evento non passa i controlli, non si chiude nulla, anche nella chiusura per filtro.
- **Scritture serializzate.** Scansioni e revisioni concorrenti si mettono in fila; dopo 15 secondi di attesa il comando fallisce e si riprova.
- **Un piano si controlla per intero, ma si esegue mossa per mossa.** Con un solo problema non si sposta nulla. Durante l'esecuzione un errore ferma il riordino a metà: lo stato parziale è permesso, perché ogni mossa fatta è nel giornale e rilanciare lo stesso piano riprende da lì.
- **Il giornale precede la mossa.** Una riga annotata e non eseguita è possibile; una mossa eseguita e non annotata no. Una mossa risulta già fatta solo se il giornale la registra.
- **Un riordino alla volta.** `riordina.lock`, accanto al piano, impedisce due esecuzioni insieme.
- **Riordino e rilevatore non si coordinano.** Una scansione durante o dopo un riordino vede ogni spostamento come una cancellazione più un'aggiunta. Per questo all'installazione il riordino, e la scelta di esclusioni e profondità fatta sull'inventario, precedono la prima scansione: dopo, ogni cambio di copertura costa eventi.
- **Il conteggio dei file controlla il resto.** Il riordinatore conta i file prima e dopo: se il numero cambia, qualcos'altro ha toccato la cartella nel frattempo.

## Guasti e degrado

Risponde a `failure-and-degradation`.

| Guasto | Comportamento | Conta come funzionante? |
| --- | --- | --- |
| Radice mancante o illeggibile | Errore della radice, nessuna cancellazione registrata, stato precedente conservato; `review` rifiuta gli eventi di quella radice finché l'errore resta | No: va corretto o escluso |
| Sottocartella illeggibile | Le parti leggibili si aggiornano, quella illeggibile conserva il suo stato; come per la radice, `review` rifiuta gli eventi della radice finché l'errore resta | In parte: la coda si legge, la scansione parziale si dichiara, e si chiude dopo aver corretto o escluso il percorso |
| File solo nel cloud | Confronto su dimensione e data, niente impronta e niente suggerimento di rinomina | Sì |
| Modifica a dimensione e data invariate | La scansione veloce può perderla; `--full` ricalcola le impronte | Sì, con il limite dichiarato |
| File che cambia mentre si legge | Errore su quel file; la scansione successiva riprova | Sì |
| Percorso uscito dalla copertura | Nessuna falsa cancellazione; i suoi eventi si chiudono senza ricontrollo | Sì |
| Riordino interrotto | Il lucchetto resta: l'utente verifica lo stato e lo cancella; un'ultima riga del giornale troncata si segnala con il suo numero | No, finché non si verifica |
| File aperto durante il riordino | Il riordino si ferma su quella mossa; si risolve e si rilancia | Sì, dopo la ripresa |
| Python più vecchio della 3.10 | Gli script lo dicono e non partono | No |
| Pagina di partenza mancante o illeggibile | `links` la segnala | No |

Il registro non è un backup: un file creato e cancellato tra due scansioni non è osservabile. Se il registro si perde o si rovina, una nuova scansione ricrea la base e la coda si perde. Scrivano non copia né il registro né il Desktop: il backup dei documenti resta all'utente.
