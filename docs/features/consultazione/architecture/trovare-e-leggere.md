# Trovare e leggere in Consultazione

**Status:** accepted

## Scope

Dice quali pagine usa l'agente per rispondere, in che ordine le apre, cosa fa quando il percorso non porta alla risposta, cosa vince quando una nota e un documento non dicono la stessa cosa e cosa passa a chi riceve una parte del lavoro. Cosa ne vede l'utente sta in [Consultazione](../product/consultazione.md); la forma delle pagine in [Sistema e componenti](../../../architecture/sistema-e-componenti.md#componenti).

## Dependencies

- [Esiti](../product/consultazione.md#esiti) — l'ordine di lettura serve a dare copertura e data dei fatti in ogni risposta, e il ripiego serve a insegnare parole nuove alla mappa.
- [Componenti](../../../architecture/sistema-e-componenti.md#componenti) — una sola mappa, importata da `AGENTS.md`, e una guida per dominio.
- [Proprietà dei dati](../../../architecture/dati-e-fiducia.md#proprietà-dei-dati) — note e mappa le scrive l'agente; i documenti restano dell'utente e non si correggono.

## Pagine

Risponde a `feature-components`.

| Pagina | Ruolo nella risposta |
| --- | --- |
| `AGENTS.md`, con la mappa importata | Porta dalle parole della domanda al dominio, senza una lettura in più |
| `GUIDA.md` del dominio e guide annidate | Confine, regole locali, ingressi e copertura, che valgono per la risposta |
| Nota canonica | Stato, decisioni e data dei fatti di un tema |
| Documenti e fonti | I fatti di cui la nota è la sintesi |
| Coda del rilevatore | Quali documenti sono cambiati dopo la nota |

## Percorso

Risponde a `feature-interfaces`.

1. **Dalla mappa alla guida, sempre.** La mappa è già nel contesto: la riga con le parole della domanda porta alla guida del dominio, che si apre sempre, perché le sue regole e la sua copertura valgono per la risposta. Un ingresso con una guida propria si apre allo stesso modo.
2. **Nel dominio si cerca liberamente.** Oltre agli ingressi della guida, anche per parole: le cartelle del dominio fanno da indice, come la documentazione per gli agenti che usano il delivery process advisor ([fonte](../../../sources/2026-10-27-advisor-navigazione-e-lettura.md)). Come leggere una pagina, intera o a pezzi, lo decide l'agente; una regola si aggiunge solo se la [misura](https://github.com/SebastianoTomasi/Scrivano/issues/11) mostra che serve.
3. **Prima la nota, poi i documenti.** Il documento si apre quando la coda dice che è cambiato dopo la nota, quando la data dei fatti della nota è più vecchia di quanto serve alla domanda, o quando serve il dato esatto.

**Delega.** Un brief che affida una parte del lavoro, come l'interpretazione di un dominio, nomina la guida del dominio e le note del tema, con la copertura: chi lo riceve trova le pagine dal brief, non dalla mappa.

## Coerenza tra note e documenti

Risponde a `feature-consistency`.

- **Sui fatti vince il documento.** La nota si corregge, con la data dei fatti nuova.
- **Sulle decisioni vince la nota**, perché i documenti non le registrano: un fatto nuovo che la contraddice resta nella nota come conflitto e si chiede all'utente.
- **Le note prevalgono sulle sintesi** di guide e mappa.

## Quando il percorso non porta

Risponde a `feature-failure-behavior`.

- **La mappa non ha la riga, o il dominio non risponde.** Si cerca in tutto il Desktop e nei percorsi esterni. Se la risposta salta fuori, la riga del suo dominio nella mappa prende le parole della domanda.
- **Manca la nota.** Non vuol dire che manchi l'informazione: si cerca nei documenti censiti e si dice cosa resta non letto.

## Compatibilità

Risponde a `feature-compatibility`.

Un'istanza con i modelli anteriori al 2026-10-27 non importa la mappa e la legge come prima: funziona lo stesso. L'aggiornamento porta import e percorso con le azioni della voce del 2026-10-27 del [CHANGELOG](../../../../CHANGELOG.md).
