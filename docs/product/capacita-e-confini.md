# Capacità e confini di Scrivano

**Status:** proposed

## Scope

Elenca ciò che l'utente può fare con Scrivano, come lo vedrebbe da fuori, come si scelgono i domini e ciò che Scrivano sceglie di non fare. Come l'agente conversa con l'utente sta in [Conversazione con l'utente](../frontend/conversazione-con-l-utente.md); i componenti che realizzano queste capacità in [Sistema e componenti](../architecture/sistema-e-componenti.md).

## Dependencies

- [Scopo](scopo-e-persone.md#scopo) — ogni capacità serve a chiedere all'agente invece di cercare tra le cartelle.
- [Utente principale](scopo-e-persone.md#utente-principale) — l'utente decide a parole e non tocca comandi, quindi ogni capacità passa dall'agente.

## Capacità osservabili

Risponde a `observable-capabilities`.

1. **Installare chiedendolo.** L'utente apre l'agente sul Desktop e scrive *installa Scrivano da* seguito dall'indirizzo del repository. Se il sistema c'è già, l'agente passa all'aggiornamento. L'installazione si chiude con quattro cose da sapere: aprire l'agente sul Desktop, dove lasciare i file nuovi, cosa chiedere, a cosa serve la coda. Poi l'agente offre di interpretare subito un dominio.
2. **Approvare un'organizzazione.** L'agente propone domini e un livello di riordino (completo, leggero o nessuno), con poche domande legate al materiale; l'utente approva il riassunto o lo corregge.
3. **Riordinare e tornare indietro.** Il Desktop si riordina secondo il piano approvato; ogni correzione a parole diventa un piano in più, e ogni spostamento si può annullare. Si spostano file sparsi o cartelle intere, mai l'interno di una cartella. Una cartella-contenitore anonima si svuota solo con l'approvazione dell'utente e, rimasta vuota o con i soli metadati rigenerati, si toglie. I collegamenti alle applicazioni vanno in `Collegamenti`. Dove stanno i repository si decide all'installazione: dopo restano fermi, e uno con un ambiente virtuale resta dov'è.
4. **Chiedere dei propri documenti.** L'agente risponde partendo da mappa, guide e note, e sa dire quanto di un dominio ha letto. Dopo l'installazione le guide sono uno scheletro con copertura «censito»: i domini si interpretano quando l'utente lo chiede.
5. **Lasciare i file nuovi sul Desktop.** L'agente propone dove metterli, e un nome se quello che hanno non dice nulla, al massimo una volta per sessione; un no chiude la questione.
6. **Ricevere ciò che l'agente scrive già al suo posto.** Una lettera o un riepilogo nasce nella cartella del tema, non nella radice né in Download.
7. **Avere note al passo con i documenti.** A ogni sessione l'agente sa quali file sono cambiati dall'ultima volta e riconcilia le note prima di fidarsene. La coda si tiene corta da sola: oltre i 50 eventi, una volta per sessione e dopo aver risposto, l'agente chiude ciò che non richiede lavoro, come rinomine e gruppi che non toccano note, e propone di escludere il rumore che si ripete.
8. **Aggiornare chiedendolo.** Con *aggiorna Scrivano* l'istanza arriva alla versione più recente, senza perdere gli adattamenti delle pagine.
9. **Disinstallare.** Si cancellano strumento, registro e pagine del sistema; riordino e note restano.
10. **Usarlo con il Desktop nel cloud.** Il Desktop è quello reale, anche quando Windows lo reindirizza su OneDrive o macOS lo tiene su iCloud. Il sistema funziona lì e non scarica i file che stanno solo nel cloud.

## Domini

I domini si scelgono dall'oggetto delle domande, non dal tipo di file o dal contenitore. Si parte da una tassonomia di riferimento e si tengono solo i domini che hanno materiale:

| Dominio | Contenuto |
| --- | --- |
| Amministrazione | pratiche, documenti d'identità, contratti, acquisti e garanzie |
| Finanze | banche, bilancio, tasse, investimenti |
| Salute | visite, referti, prescrizioni |
| Lavoro | CV, impieghi, opportunità; una sottocartella per azienda o cliente |
| Studi | scuola, corsi, tesi, certificazioni |
| Personale | casa, hobby, foto, dispositivi, viaggi |
| Progetti | software e strumenti personali, se ci sono |
| Collegamenti | collegamenti alle applicazioni |

Nessun dominio vuoto. I nomi sono in PascalCase ASCII. Ricerca, o un dominio per un'attività propria, si aggiungono quando il materiale lo giustifica. Le guide di Finanze, Salute e Amministrazione portano già le regole locali, come distinguere fatti e stime e lasciare gli identificativi negli originali. Ciò che l'utente non sa collocare resta nella radice del Desktop. Il dettaglio di ogni dominio sta nel [catalogo dei domini](../../modelli/domini.md).

## Non-obiettivi

Risponde a `non-goals`.

- **Non è un backup né una cronologia.** Il registro conserva metadati, non copie; un file creato e cancellato tra due scansioni non si vede.
- **Non è la memoria dell'agente.** Le note raccolgono ciò che si sa dei documenti e delle questioni dell'utente. Le preferenze sul modo di lavorare restano nella memoria di Claude o Codex e il resoconto di un lavoro sta nella risposta: copiati sul Desktop diventerebbero doppioni che invecchiano.
- **Non gira in background.** Il rilevatore parte quando l'agente lo lancia, all'inizio della sessione.
- **Niente installatore, plugin o skill.** Installa l'agente seguendo istruzioni scritte, come spiega l'[ADR 0001](../adr/0001-gli-script-osservano-l-agente-decide.md); nulla va in `~/.claude` o `~/.codex`, salvo il marcatore che Codex richiede.
- **Gli script non decidono.** Non interpretano i cambiamenti, non scelgono dove va un file e non riconoscono autore o significato di una modifica.
- **Non tocca l'interno di una cartella con un'identità.** Progetti, corsi, viaggi e pratiche si spostano interi; i repository restano fermi dopo l'installazione.
- **Non cancella da solo.** Ciò che è superato l'agente propone di buttarlo e lo mette nel Cestino dopo il sì dell'utente, così si recupera; gli script tolgono solo i metadati che il sistema rigenera, nelle cartelle che il piano svuota.
- **Non custodisce segreti.** Li segnala; il loro posto è il password manager.
- **Non condivide.** Nessuna sincronizzazione tra PC o persone, nessuna esportazione delle note, nessun accesso alla rete dagli script.
- **Non serve gli altri utenti del PC.** `Public\Desktop` resta fuori.
- **Non scrive regole di permesso dell'agente.** La modalità consigliata è auto in Claude Code e accesso completo in Codex.

## Feature

Le capacità diventano cinque feature, documentate una per sessione a partire da installazione:

| Feature | Slug | Capacità |
| --- | --- | --- |
| Installazione | `installazione` | 1, 2, 10 |
| Riordino | `riordino` | 3 |
| Coda dei cambiamenti | `coda-dei-cambiamenti` | 5, 7 |
| Consultazione | `consultazione` | 4, 6 |
| Aggiornamento | `aggiornamento` | 8, 9 |

Ogni feature nasce con il suo primo artifact Product in `docs/features/<slug>/product/`. Fino ad allora il comportamento di ciascuna è quello che implementano procedure, modelli e script.
