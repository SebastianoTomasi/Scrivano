# Changelog

Voci per data, dalla più recente. Ogni voce dice cosa cambia; **Azioni per l'istanza** dice cosa adattare in un'installazione già presente, seguendo [AGGIORNA.md](./AGGIORNA.md).

## 2026-10-09

Prima versione installabile.

- Modelli delle pagine del Desktop e catalogo dei domini in `modelli/`; procedure di installazione e aggiornamento.
- Le pagine trattano il Desktop come archivio personale: le note raccolgono ciò che si sa dei documenti e delle questioni dell'utente; le preferenze sul modo di lavorare restano nella memoria dell'agente, il resoconto di un lavoro nella risposta.
- `controlla.py`: coda dal cambiamento più recente, filtro `--depth`, chiusura per filtro con `review --root`/`--prefix`, file solo nel cloud confrontati senza scaricarli.
- `riordina.py`: inventario e riordino con piano, giornale, ripresa e annullamento; le cartelle-contenitore svuotate si tolgono con `vuote`.
- `tests/desktop_finto.py`: Desktop disordinato finto e verifica di un'installazione, per le prove complete con un agente.

**Azioni per l'istanza:** nessuna. Un'istanza nata prima di questa data si porta ai modelli a mano.
