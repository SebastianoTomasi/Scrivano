# Sistema e componenti di Scrivano

**Status:** accepted

## Scope

Separa ciò che Scrivano possiede dai sistemi con cui parla, divide il sistema in componenti e dice quali dipendenze sono permesse. Chi possiede ciascun dato e dove passano i confini di fiducia sta in [Dati e fiducia](dati-e-fiducia.md); i contratti verso l'esterno e il comportamento nei guasti in [Contratti e guasti](contratti-e-guasti.md).

## Dependencies

- [Attori e soggetti](../product/scopo-e-persone.md#attori-e-soggetti) — agente e script sono parti distinte: i componenti tengono separato chi decide da chi esegue.
- [Capacità osservabili](../product/capacita-e-confini.md#capacità-osservabili) — ogni capacità deve cadere in un componente.

## Confine del sistema

Risponde a `system-boundary`.

Scrivano possiede il repository e ciò che ne nasce in un'istanza:

- gli script, i modelli, il catalogo dei domini e le procedure del repository;
- in un'istanza, lo strumento in `Documenti/Scrivano`, con in `src/`, accanto a `controlla.py`, la configurazione e la cartella `.stato/` di registro, piani e giornali, ignorate da git; il rilevatore esclude lo strumento dalle radici che osserva;
- sul Desktop, la forma delle pagine del sistema: `AGENTS.md`, `MAPPA.md`, `MANUTENZIONE.md` e le `GUIDA.md`, più `.codex-root` se l'utente usa Codex. Il contenuto delle pagine e le note appartengono all'utente.

Sul Desktop non va nient'altro: nessuna skill, nessun puntatore in `~/.claude` o `~/.codex` oltre al marcatore di Codex. Per le cose personali l'utente apre l'agente sul Desktop.

**Forma del repository.** `src/` contiene solo ciò che un'istanza esegue o copia: i due script, `config.example.json` e i modelli con il catalogo dei domini. Fuori da `src/` stanno le procedure che installano e aggiornano un'istanza, con il CHANGELOG e il README, e ciò che serve solo a sviluppare Scrivano: questi artifact, gli ADR, il glossario, le regole del delivery process advisor e i test. Lo strumento di un'istanza resta la copia dell'intero repository. I motivi sono nell'[ADR 0004](../adr/0004-src-contiene-cio-che-arriva-nell-istanza.md).

Le pagine e le procedure sono istruzioni per un agente: per Scrivano valgono quanto il codice. Lo stato tecnico lo descrive il codice degli script; il comportamento dell'agente lo descrivono modelli e procedure.

Scrivano parla con questi sistemi senza possederli:

| Sistema | Cosa gli chiede Scrivano |
| --- | --- |
| Agente (Claude Code, Codex) | Leggere `AGENTS.md`, seguire pagine e procedure, lanciare gli script, conversare con l'utente |
| Fornitore del modello | Nulla: riceve ciò che l'agente legge, fuori dal controllo di Scrivano |
| File system di Windows e macOS | Elenchi, metadati, letture e rinomine; maiuscole che non contano, accenti scomposti, link e junction |
| OneDrive, iCloud e altri File Provider | Nulla: Scrivano riconosce i file solo nel cloud e non li legge |
| Python 3.10 o successivo | Eseguire gli script con la sola libreria standard |
| git o lo zip del repository | Portare lo strumento nell'istanza e aggiornarlo |
| Configurazione di Codex | Il marcatore `.codex-root` in `project_root_markers`, con il consenso dell'utente |

## Componenti

Risponde a `components`.

| Componente | Responsabilità |
| --- | --- |
| Rilevatore (`src/controlla.py`) | Osserva le radici, registra i cambiamenti in una coda, chiude gli eventi revisionati dopo averne ricontrollato il file, controlla link e ancore delle pagine. Non legge i documenti per capirli. |
| Riordinatore (`src/riordina.py`) | Riassume una cartella in un inventario; esegue, riprende e annulla un piano approvato. Non sceglie le mosse. |
| Modelli (`src/modelli/`) | Danno forma alle pagine del sistema e il catalogo dei domini da cui partono le proposte. Non si chiamano mai come i file che gli agenti caricano da soli (`AGENTS.md`, `CLAUDE.md`), così nessuno li scambia per istruzioni: il modello dell'`AGENTS.md` del Desktop è `scrivano-agents.md`, perché dal nome si capisca cosa diventa. L'agente li copia sul Desktop e li adatta. |
| Procedure (`INSTALLA.md`, `AGGIORNA.md`, `CHANGELOG.md`) | Dicono all'agente come installare e aggiornare un'istanza; il CHANGELOG porta, per data, le azioni che un'istanza deve applicare. |
| Pagine del sistema (sul Desktop) | Dicono all'agente di ogni sessione come lavorare, dove sta cosa e come tenere aggiornato l'archivio. Nascono dai modelli e poi sono dell'utente. |
| Riferimento dello strumento (`README.md`) | Descrive comandi, configurazione, formato del piano e limiti degli script. Gli artifact fissano le garanzie e rimandano qui per la sintassi, senza copiarla. |

L'agente non è un componente: è il sistema esterno che interpreta e decide. Ogni regola che richiede giudizio sta in una pagina o in una procedura; ogni garanzia che non può dipendere dal giudizio sta in uno script. Le garanzie servono in due punti, e solo lì ci sono script: spostare senza perdere nulla e sapere cosa è cambiato. Pagine e procedure danno obiettivi, principi e poche regole di sicurezza; il resto lo decide l'agente, come quante domande fare, come adattare la tassonomia, quando sfoltire la coda. I motivi sono nell'[ADR 0001](../adr/0001-gli-script-osservano-l-agente-decide.md).

**Forma delle pagine.** C'è un solo `AGENTS.md`, nella radice del Desktop; le guide sono Markdown normali raggiunti dai link, come spiega l'[ADR 0002](../adr/0002-un-solo-agents-md-e-guide-collegate.md). Ogni dominio ha una `GUIDA.md` con confine, regole locali, dove vanno i documenti nuovi, ingressi e copertura. Le guide seguono le cartelle: una sottocartella con regole proprie, o cresciuta tanto che la guida del dominio non basta più a orientarcisi, prende una guida propria collegata dal genitore. La mappa resta una, nella radice, ed entra nel contesto di ogni sessione perché `AGENTS.md` la importa: è corta, e così il primo passo verso la guida non costa una lettura.

## Dipendenze tra componenti

Risponde a `component-dependencies`.

- **Gli script dipendono solo dalla libreria standard.** Nessuno importa l'altro: un'istanza può lanciarli da un altro percorso, quindi le poche funzioni comuni restano duplicate.
- **Gli script non dipendono dall'agente.** Ricevono comandi, configurazione e piani e rispondono in JSON; non chiamano l'agente e non leggono le pagine per prendere decisioni.
- **Il rilevatore conosce solo i nomi delle pagine di partenza.** `links` parte da `AGENTS.md`, `MAPPA.md` e `MANUTENZIONE.md` e salta le cartelle `Archivio`, rimaste dalle istanze che le usavano: è l'unico punto in cui uno script dipende dalla forma delle pagine.
- **Pagine e procedure dipendono dagli script.** Ne usano i comandi; il README è il riferimento della loro sintassi.
- **Le pagine non dipendono dal repository dopo l'installazione.** Un'istanza funziona anche se il repository cambia, finché non si aggiorna.
- **Direzioni vietate.** Uno script non legge il contenuto dei documenti per interpretarlo; il riordinatore non usa il registro e il rilevatore non usa i piani.

## Punti aperti

Nessuno. Il dubbio sulle mappe dentro i domini è stato chiuso il 2026-10-26: la mappa resta una, nella radice, e il modello di `MANUTENZIONE.md` lo dice.
