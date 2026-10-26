# Registro e giornale di Scrivano

**Status:** proposed

## Scope

Descrive come il rilevatore conserva stato osservato ed eventi, come il riordinatore annota e riprende un piano, e come un cambiamento di questi formati arriva a un'istanza installata. Le garanzie verso l'agente stanno in [Contratti e guasti](../architecture/contratti-e-guasti.md); le convenzioni comuni in [Convenzioni degli script](convenzioni-degli-script.md).

## Dependencies

- [Atomicità e stati intermedi](../architecture/contratti-e-guasti.md#atomicità-e-stati-intermedi) — transazioni, giornale e lucchetto realizzano quelle garanzie.
- [Proprietà dei dati](../architecture/dati-e-fiducia.md#proprietà-dei-dati) — registro e giornale hanno un solo scrittore ciascuno.
- [Promessa di compatibilità](../product/compatibilita-e-collaudo.md#promessa-di-compatibilità) — un registro o un giornale scritto da una versione deve restare leggibile.

## Registro del rilevatore

Un file SQLite indicato da `database`, di norma `.stato/registro.sqlite` accanto allo script. Quando lo strumento sta in una cartella sincronizzata da OneDrive o da iCloud, il registro va in `%LOCALAPPDATA%\Scrivano` o, su macOS, in `~/Library/Application Support/Scrivano`: un database che cambia a ogni sessione non sta bene in una cartella sincronizzata, che può bloccarlo mentre lo carica o crearne copie in conflitto. Tre tabelle:

- `roots`: una riga per ID di radice, con percorso, data della base, ultima scansione ed errori dell'ultima scansione. Il percorso di un ID non cambia: un percorso diverso è rifiutato e richiede un ID nuovo, cioè una base nuova.
- `observed`: la firma di ogni percorso osservato, cioè tipo, dimensione, data in nanosecondi e impronta SHA-256. Le cartelle hanno firma senza dimensione e senza impronta; i file solo nel cloud senza impronta.
- `events`: aggiunte, modifiche e cancellazioni con firma prima e dopo, stato (`pending`, `superseded`, `reviewed`), data della revisione, nota e, per un evento superato, l'ID di quello che lo supera.

Gli eventi non si cancellano mai: la nota di ogni revisione resta nella tabella.

**Scansione veloce.** Se dimensione e data di un file non sono cambiate, la firma precedente si riusa senza leggere il file; `--full` ricalcola tutto. Dopo aver calcolato un'impronta lo script rilegge dimensione e data: se sono cambiate nel frattempo, il file dà errore invece di un'impronta sbagliata.

**Supersessione.** Un nuovo evento sullo stesso percorso marca come superati quelli pendenti: per ogni percorso resta pendente al massimo l'evento più recente.

**Revisione.** Ricalcola sempre l'impronta del file corrente e la confronta con la firma dopo l'evento. Una cancellazione si conferma anche quando il file system trova ancora il vecchio nome con altre maiuscole: conta come presente solo il nome scritto esattamente così. Gli eventi di percorsi non più osservati, esclusi, oltre la profondità o di una radice tolta, si chiudono senza ricontrollo, perché non c'è più uno stato con cui confrontarli.

**Copertura.** Ciò che una nuova esclusione o una profondità minore toglie dalla vista non diventa cancellato, e gli eventi pendenti restano.

**Suggerimenti.** Una rinomina di file si suggerisce solo quando un'impronta compare in una sola cancellazione e in una sola aggiunta pendenti. Una rinomina di cartella si riconosce tra le cartelle più alte di un gruppo cancellato e di uno aggiunto nella stessa radice, quando almeno metà dei file è identica; vince la coppia con più file identici.

**Transazioni.** Ogni scrittura apre `BEGIN IMMEDIATE`, così scansioni e revisioni si mettono in fila; la connessione aspetta 15 secondi.

## Piano, giornale e lucchetto

- **Giornale.** `<piano>.giornale.jsonl`, accanto al piano: una riga JSON per azione, con l'ora. Tre forme: una cartella creata (`cartella`), una mossa (`da`, `a`), una cartella tolta con i metadati che conteneva (`rimossa`, `metadati`). Ogni riga si scrive con flush e `fsync` prima della mossa o della rimozione; la creazione di una cartella si annota subito dopo averla creata.
- **Ripresa.** Una mossa con l'origine sparita e la destinazione presente conta come fatta solo se il giornale la registra; senza traccia è un problema del piano.
- **Annullamento.** `annulla` ripercorre il giornale al contrario: ricrea le cartelle tolte, riporta i file, toglie le cartelle create se sono rimaste vuote a parte i metadati, e lascia dove sono i conflitti. Quando non resta né errore né conflitto rinomina il giornale in `<piano>.giornale.annullato-<data>.jsonl`, così una nuova esecuzione ne apre uno pulito.
- **Lucchetto.** `riordina.lock`, accanto al piano, si crea in modo esclusivo con l'ora e si toglie alla fine. Uno rimasto dopo un'interruzione si cancella a mano, dopo aver verificato lo stato.

## Come un cambiamento arriva a un'istanza

Risponde a `implementation-persistence-defaults`.

Oggi lo schema del registro si crea con `CREATE TABLE IF NOT EXISTS` e non ha versione: nessun cambiamento di formato è ancora servito. Un'istanza riceve gli script nuovi con `git pull` o lo zip e li usa sul registro, sulla configurazione e sui giornali che ha già. Ciò che l'agente deve adeguare a mano, come `config.json`, arriva come azione nel CHANGELOG.

Proposta per il primo cambiamento di formato: solo cambiamenti additivi, applicati dallo script stesso all'apertura del registro e ripetibili, senza mai chiedere di cancellare il registro; il CHANGELOG lo dice nella voce del giorno.

## Punti aperti

- Confermare la regola per il primo cambiamento di formato del registro, o sceglierne un'altra.
