# SistemaConoscenza

Rilevatore dei cambiamenti descritto nel [README](./README.md). Questo repository contiene solo lo strumento: configurazione reale, registro e regole della memoria appartengono all'istanza che lo usa.

## Regole

- Il rilevatore osserva i file e conserva eventi; l'agente ne interpreta il significato. Mantieni questa separazione.
- Solo libreria standard, Python 3.10+, nessun accesso alla rete.
- Prova le modifiche su cartelle temporanee: rilevamento, pendenti, conflitti, errori e concorrenza. Mai simulare cancellazioni su documenti personali.
- Prima di consegnare esegui `python -m unittest discover -s tests -v`.
- Non versionare `config.json`, `.stato/` né percorsi, note o dati personali: un'istanza reale passa la propria configurazione con `--config`.
- Se cambi comandi, formato della configurazione o comportamento della coda, aggiorna il README nello stesso commit.
