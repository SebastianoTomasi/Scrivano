# SistemaConoscenza

Se l'utente ti chiede di installare o aggiornare il sistema, segui [INSTALLA.md](./INSTALLA.md) o [AGGIORNA.md](./AGGIORNA.md) e basta: il resto di questa pagina vale solo per chi sviluppa il repository.

Strumenti descritti nel [README](./README.md): `controlla.py` rileva i cambiamenti, `riordina.py` esegue piani di riordino approvati. I [modelli](./modelli/) diventano le pagine del Desktop di chi installa il sistema. Il [progetto di installazione](docs/progetto-installazione.md) raccoglie decisioni e ordine dei lavori. Configurazione reale, registro e pagine dell'archivio appartengono all'istanza che usa gli strumenti.

## Regole

- Gli script osservano ed eseguono; l'agente interpreta e decide. `controlla.py` lascia intatti i file osservati; `riordina.py` esegue solo il piano ricevuto, senza sovrascrivere né cancellare, e annota ogni mossa prima di farla.
- Solo libreria standard, Python 3.10+, nessun accesso alla rete.
- Prova le modifiche su cartelle temporanee: rilevamento, pendenti, conflitti, errori, concorrenza e spostamenti. Cancellazioni e spostamenti si simulano solo lì, mai su documenti personali.
- Prima di consegnare esegui `python -m unittest discover -s tests -v`.
- Il repository diventerà pubblico: tieni fuori `config.json`, `.stato/`, percorsi, nomi, note e dati personali, anche dai messaggi di commit. Un'istanza reale passa la propria configurazione con `--config`.
- I modelli e le procedure valgono per chiunque: scrivili generici, con segnaposto `{{...}}` dove servono i valori di un'installazione.
- Se cambi comandi, formato della configurazione o del piano, o comportamento della coda, aggiorna il README nello stesso commit. Se cambi modelli o procedure, aggiungi una voce al [CHANGELOG](./CHANGELOG.md) con le azioni per un'istanza già installata.
