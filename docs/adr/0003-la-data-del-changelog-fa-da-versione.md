# La data del CHANGELOG fa da versione

Un'istanza registra in «Questa istanza» la data della voce del CHANGELOG a cui corrispondono le sue pagine, e si aggiorna applicando le **Azioni per l'istanza** dalle voci di quella data in poi. Il CHANGELOG ha una sola voce per data. Un'istanza aggiornata in un certo giorno rilegge anche la voce di quel giorno, che nel frattempo può essersi allungata: per questo ogni azione si scrive in modo che ripeterla non faccia danni.

## Consequences

- Non ci sono tag né numeri di versione: il campo `version` di `pyproject.toml` non identifica un'istanza.
- Le modifiche dello stesso giorno si aggiungono alla voce esistente invece di aprirne una nuova.
