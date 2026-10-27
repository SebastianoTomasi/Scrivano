# Navigazione e lettura: cosa è cambiato nell'advisor

Fonte del 2026-10-27. Raccoglie le modifiche delle versioni 0.5.0 e 0.5.1 del
[delivery process advisor](https://github.com/SebastianoTomasi/delivery-process-advisor),
nate da un'analisi di come gli agenti trovano e leggono i documenti. Serve a
rivedere con il processo dell'advisor il modo in cui l'agente dello Scrivano
naviga l'archivio. Come ogni fonte informa le decisioni e non ne stabilisce:
le regole dello Scrivano restano quelle dei suoi documenti accettati.

## Da dove nasce

Un'analisi di 296 sessioni principali e dei loro subagent, in sette progetti
che usano l'advisor, ha misurato come gli agenti arrivano ai documenti in
`docs/`. Il [report](https://github.com/SebastianoTomasi/delivery-process-advisor/blob/main/docs/sources/experiments/2026-10-26-agent-docs-navigation/report-navigazione-advisor.md)
e gli script sono pubblici; una seconda sessione ha rifatto le misure con uno
script indipendente e le ha confermate, tranne una.

| Misura | Valore |
|---|---|
| Sessioni che leggono la mappa prima del primo documento | circa 10% |
| Ricerche fatte dentro una sola cartella | maggioranza (63–87% secondo il criterio) |
| Documenti trovati da una ricerca / dal compito / da un link / dalla mappa | 27–52% / 15–33% / 14% / 6–8% |
| Documenti letti solo a pezzi, senza stato e Scope, nel progetto più grande | 41–43% (22% nei progetti piccoli) |
| Sessioni in cui l'utente corregge un documento non letto | nessuna |
| Costo prima del primo documento, partendo dalla mappa / cercando | 34 KB / 25 KB di output, mediana |

Le conclusioni:

- **Per trovare, gli agenti usano i nomi delle cartelle come indice** e
  arrivano al passaggio giusto in uno-tre comandi. Le parole della domanda
  stanno nei documenti, non nella mappa.
- **La mappa costa e serve ad altro.** Il file delle regole comuni pesa 17 KB,
  circa 4.300 token, prima di vedere un documento. Gli agenti lo aprono
  quando devono collocare o scrivere un documento, e lì funziona.
- **Il rischio vero è la lettura a pezzi.** Chi legge con `grep -n` o
  `sed -n 120,160p` non vede se il documento è accettato o una proposta. In
  una sessione l'agente ha letto pezzi di un documento proposed ed è passato
  a un piano e all'implementazione senza mai vederne lo stato.
- **I subagent trovano i documenti dal brief** (29%) e da codice e README
  (32%), quasi mai dalla mappa (1%).

La 0.5.1 nasce da un problema diverso, segnalato dall'utente lo stesso giorno:
l'agente rispondeva dai documenti senza aprire il codice, e descriveva un
comportamento che il codice aveva già sostituito.

## Cosa è cambiato

Tutte le modifiche stanno nel file radice `advisor-agents.md`, caricato in ogni
sessione, e nel modello della documentazione che lo governa.

1. **Trovare passa dalle cartelle (0.5.0).** Per sapere cosa il progetto ha
   deciso su un tema l'agente cerca dentro la cartella che lo contiene:
   `docs/<autorità>/`, `docs/features/<feature>/` o `docs/adr/`, poi segue i
   link. Se la ricerca non trova nulla, il tema può essere scritto con altre
   parole: apre il file di confine o la tabella delle autorità. La mappa,
   cioè `docs/advisor-docs.md`, il confine e un solo catalogo, serve a
   collocare un documento e a sapere quali decisioni un'azione deve coprire.
   [ADR-0046](https://github.com/SebastianoTomasi/delivery-process-advisor/blob/main/docs/adr/0046-finding-goes-through-folders-the-map-serves-placement.md).
2. **Un passaggio senza busta non è un input (0.5.0).** La busta (*routing
   envelope*, ora nel glossario) è nome del file, titolo, riga di stato e
   Scope. Prima di pianificare, costruire, rivedere o dire all'utente cosa ha
   deciso il progetto, l'agente legge la busta del documento, e le
   Dependencies se il passaggio è una decisione che dipende da altre. Il
   motivo è scritto nella regola: un pezzo di proposta sembra un pezzo di
   regola accettata. La regola sta tra quelle di interpretazione, non di
   navigazione: non chiede di cercare in un altro modo, dice quando la busta
   deve essere stata letta.
3. **Chi delega nomina i documenti (0.5.0).** Un brief per un subagent nomina
   i documenti che possiedono il tema, con il loro stato.
4. **Le regole comuni restano un contratto (0.5.0).** `docs/advisor-docs.md`
   non diventa un indice e non viene accorciato: l'indice è già il layout
   delle cartelle.
5. **Prima il codice, poi i documenti (0.5.1).** Prima di spiegare,
   pianificare o cambiare un comportamento che il progetto può già avere,
   l'agente legge il codice, poi la documentazione, e risponde da entrambi.
   Se si contraddicono lo dice, tiene l'implementazione e propone di allineare
   i documenti al codice; l'utente può invece confermare i documenti come
   direzione voluta. Anche la preparazione di una sessione grill-with-docs
   legge il codice di ciò che esiste già.
   [ADR-0047](https://github.com/SebastianoTomasi/delivery-process-advisor/blob/main/docs/adr/0047-code-is-read-before-documentation.md)
   sostituisce il default neutro dell'ADR-0032.

## Come è stato fatto

- **Verifica prima di decidere.** I risultati del report sono stati rimisurati
  in modo indipendente; la quota di ricerche in una sola cartella è confermata
  solo nella direzione, non nel valore. Il costo delle due strade è stato
  misurato a parte.
- **Decisioni in una sessione grill-with-docs.** Dieci domande, ognuna con una
  risposta raccomandata: le due modalità (trovare e collocare), cosa
  ottimizzare (token, con la busta come vincolo), quanto prescrivere (le
  cartelle sì, i comandi no, perché cambiano con l'host), quando scatta la
  regola della busta, dove vive, il fallback, i brief, la rimisura.
- **Testi rivisti con improve-prompt.** Il file radice costa token in ogni
  sessione, quindi ogni regola dice il suo perché in una frase, descrive
  l'esito e non i comandi, e non ripete ciò che il file dice altrove.
- **Propagazione della regola accettata.** Il passaggio sul file radice nel
  modello della documentazione era accettato: è stato riscritto con
  propagate-change, controllando i documenti che lo citano. Nessuno è dovuto
  passare a needs-review.
- **Consegna.** Versione 0.5.0, poi 0.5.1; init in tutti i progetti, compreso
  questo, con una verifica file per file contro il payload.
- **Rimisura.** Un'[issue deferred](https://github.com/SebastianoTomasi/delivery-process-advisor/issues/12)
  riapre la misura dal 2026-11-27, sul progetto più usato o su tutti insieme.
  Obiettivo: letture senza busta sotto il 20%. Se la regola scritta non
  basta, il passo successivo è uno strumento di ricerca che stampa la busta
  accanto a ogni risultato.

## Cosa può voler dire per lo Scrivano

Lo sviluppo di questo repository segue già le regole nuove, arrivate con
l'init. L'archivio sul Desktop è un sistema a parte con lo stesso schema,
mappa → guida → note, quindi le stesse domande valgono lì. Sono domande, non
decisioni:

1. **Partire dalla mappa.** [Il modello di `AGENTS.md`](../../src/modelli/scrivano-agents.md)
   dice «Per rispondere, parti dalla mappa», e così
   [Capacità e confini](../product/capacita-e-confini.md), capacità 4.
   Le condizioni però sono diverse dall'advisor: il
   [modello di `MAPPA.md`](../../src/modelli/mappa.md) è piccolo e la sua prima
   colonna contiene proprio le parole dell'utente, quindi è fatto per
   instradare una domanda; molti documenti sono PDF o scansioni che una
   ricerca testuale non legge. L'argomento del costo può non valere qui.
   Va misurato sulle sessioni aperte sul Desktop prima di cambiare? Oppure
   basta permettere di cercare subito nel dominio quando il dominio è ovvio?
2. **Una busta per note e guide.** La guida ha già «Copertura» e
   «Verificato». Una nota letta a pezzi mostra il tema, la data dei fatti e
   cosa resta aperto? Serve una regola come quella dell'advisor: prima di
   rispondere da un pezzo di nota, leggine l'intestazione?
3. **Prima i documenti, poi le note.** Il modello dice «Leggi prima le note,
   poi fonti e documenti»; la coda di `controlla.py` serve a riconciliare le
   note prima di fidarsene. È lo stesso rischio dell'ADR-0047: rispondere da
   una sintesi che la fonte ha già superato. Quando una nota e i suoi
   documenti si contraddicono, è scritto che vincono i documenti e che la
   nota si corregge? Oggi il modello dice solo che le note prevalgono sulle
   sintesi di guide e mappa.
4. **Brief.** Quando l'agente dell'archivio delega, per esempio
   l'interpretazione di un dominio, il brief nomina la guida e le note del
   dominio?
5. **Misurare.** Gli script dell'advisor misurano la navigazione dentro
   `docs/` di un repository. Per l'archivio andrebbero adattati a `MAPPA.md`,
   `GUIDA.md` e note. Le sessioni sul Desktop toccano documenti personali:
   i risultati restano fuori da qualunque repository.
