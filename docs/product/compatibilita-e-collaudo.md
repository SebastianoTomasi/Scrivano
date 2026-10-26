# Compatibilità e collaudo di Scrivano

**Status:** proposed

## Scope

Dice cosa Scrivano promette di non rompere alle istanze già installate e come si verifica da fuori che il prodotto fa ciò che dichiara. La procedura che porta un cambiamento alle istanze sta in [Rilascio e aggiornamento](../deployment/rilascio-e-aggiornamento.md); i tipi di test in [Flusso di lavoro e test](../development/flusso-di-lavoro-e-test.md).

## Dependencies

- [Capacità osservabili](capacita-e-confini.md#capacità-osservabili) — la compatibilità protegge installazione, riordino, coda e aggiornamento così come l'utente li conosce.
- [Classi di dati](dati-e-obblighi.md#classi-di-dati) — non perdere né alterare documenti e non spostare segreti sono parte della promessa.

## Promessa di compatibilità

Risponde a `compatibility-baseline`.

Un cambiamento è ordinario se un'istanza installata lo assorbe seguendo `AGGIORNA.md`; altrimenti è un cambiamento che rompe. La promessa vale per chi usa un'istanza, cioè per l'utente e per il suo agente.

- **Ogni istanza si aggiorna.** Ogni modifica a modelli o procedure porta nel `CHANGELOG.md`, sotto la sua data, le azioni per l'istanza; le azioni si possono ripetere senza danni. La data dei modelli scritta in «Questa istanza» fa da versione, come spiega l'[ADR 0003](../adr/0003-la-data-del-changelog-fa-da-versione.md).
- **Le pagine restano dell'utente.** Un aggiornamento integra gli adattamenti locali e non sovrascrive le pagine del Desktop.
- **I file dell'istanza restano leggibili.** `config.json`, il registro e i giornali dei piani scritti da una versione restano validi per le successive, o il CHANGELOG dice come adeguarli. Un ID di radice esistente non cambia percorso.
- **I comandi delle pagine continuano a funzionare.** Un comando che le pagine del Desktop usano non cambia senza un'azione nel CHANGELOG che lo aggiorni.
- **Le garanzie degli script non si allentano.** Il rilevatore non modifica i file osservati; il riordino non sovrascrive e non cancella oltre i metadati rigenerati; nessuno dei due usa la rete.
- **Le piattaforme non si restringono.** Windows 11, macOS e Python 3.10 restano supportati.
- **Disinstallare non toglie lavoro.** Riordino e note restano dopo la disinstallazione.

## Criteri di successo

Risponde a `success-criteria`.

Il prodotto fa ciò che dichiara quando, dall'esterno:

1. **Una prova completa riesce.** Un agente segue `INSTALLA.md` su un Desktop finto generato da `tests/desktop_finto.py`, e `verifica` passa tutti i controlli: nessun file perso, duplicato o alterato sul Desktop, in Documenti e in Download; pagine del sistema presenti, senza segnaposto e senza altri `AGENTS.md` o `CLAUDE.md`; ogni guida raggiungibile dalla mappa e `links` senza problemi; base del registro creata senza errori; segreto e file di sistema rimasti nella radice; repository e pacchetto spostati interi.
2. **Riesce con entrambi gli agenti.** La prova passa con Claude Code e con Codex, sul Desktop finto di Windows e su quello di un Mac (`genera --mac`).
3. **Il riordino si annulla.** Dopo `annulla` ogni file è dove stava.
4. **La coda vede il lavoro a mano.** Un file aggiunto, modificato o cancellato dall'utente compare nella coda della sessione successiva, e la chiusura rifiuta un file cambiato dopo la lettura.
5. **I test passano.** `python -m unittest discover -s tests -v` riesce.

## Punti aperti

- Registro, configurazione e giornali sono parte della promessa, o un cambiamento può chiedere di ricreare la base?
