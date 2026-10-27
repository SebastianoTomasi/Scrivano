# Consultazione

**Status:** accepted

## Scope

Dice cosa ottiene l'utente quando chiede qualcosa dei propri documenti: da dove viene la risposta, cosa la accompagna, cosa succede quando l'archivio non risponde e cosa la feature non fa. Come l'agente trova e legge pagine, note e documenti sta in [Trovare e leggere](../architecture/trovare-e-leggere.md); le regole di ogni conversazione in [Conversazione con l'utente](../../../frontend/conversazione-con-l-utente.md). La capacità 6, ricevere ciò che l'agente scrive già al suo posto, appartiene a questa feature ma non è ancora scritta qui: vale quello che dicono [Capacità e confini](../../../product/capacita-e-confini.md#capacità-osservabili) e il modello di `AGENTS.md`.

## Dependencies

- [Capacità osservabili](../../../product/capacita-e-confini.md#capacità-osservabili) — la feature realizza la capacità 4, chiedere dei propri documenti.
- [Utente principale](../../../product/scopo-e-persone.md#utente-principale) — l'utente chiede a parole e non apre le pagine, quindi la risposta porta con sé quanto fidarsene.
- [Classi di dati](../../../product/dati-e-obblighi.md#classi-di-dati) — la feature legge solo classi già dichiarate, e ciò che legge arriva al fornitore del modello.

## Scopo

Risponde a `feature-purpose`.

L'utente chiede dei propri documenti a parole, per esempio «quando scade il contratto d'affitto?», e riceve una risposta tratta dall'archivio invece di cercare tra le cartelle.

## Attori

Risponde a `feature-actors`.

L'utente chiede; l'agente trova, legge, risponde e aggiorna note e mappa. Un subagent a cui l'agente affida una parte del lavoro è l'agente stesso, non un attore nuovo. Il fornitore del modello riceve ciò che l'agente legge.

## Dati

Risponde a `feature-data`.

La feature legge pagine del sistema, note e documenti dell'utente, e scrive note e mappa. Nessuna classe nuova.

## Precondizioni

Risponde a `feature-preconditions`.

L'istanza è installata e l'agente è aperto sul Desktop, con `AGENTS.md` nella radice. Ogni dominio ha una guida, almeno con copertura «censito».

## Esiti

Risponde a `feature-outcomes`.

- **Risposta.** Viene dalle note e dai documenti del dominio e dice quanto del dominio è stato letto, cioè la copertura della guida, e la data dei fatti su cui si basa.
- **Nota e documento discordano su un fatto.** La risposta segue il documento e la nota si corregge.
- **Un fatto nuovo contraddice una decisione dell'utente.** L'agente lo dice e chiede; la nota conserva il conflitto.
- **L'archivio non risponde.** L'agente dice dove ha cercato e cosa resta soltanto censito, senza concludere che l'informazione manchi.
- **La risposta sta dove la mappa non portava.** La riga della mappa del dominio impara le parole della domanda, e la volta dopo porta lì.

## Non-obiettivi

Risponde a `feature-non-goals`.

- **Non risponde senza aprire l'archivio.** Anche una domanda già fatta passa da note e documenti.
- **Non legge tutto per rispondere.** Legge ciò che serve alla richiesta, perché ciò che legge arriva al fornitore del modello.
- **Non interpreta un dominio intero da sola.** L'interpretazione di un dominio si fa quando l'utente la chiede.

## Screening

`security-new-subject-or-data`: nessun attore, soggetto o classe di dati nuova; il subagent è l'agente.
