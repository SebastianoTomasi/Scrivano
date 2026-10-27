# Rilascio e aggiornamento di Scrivano

**Status:** proposed

## Scope

Dice dove passa un cambiamento per arrivare a un'istanza e come si rilascia, si verifica e si torna indietro. I passi che l'agente segue sul PC dell'utente sono in [INSTALLA.md](../../INSTALLA.md) e [AGGIORNA.md](../../AGGIORNA.md); la promessa di compatibilità che il rilascio deve rispettare in [Compatibilità e collaudo](../product/compatibilita-e-collaudo.md#promessa-di-compatibilità).

## Dependencies

- [Promessa di compatibilità](../product/compatibilita-e-collaudo.md#promessa-di-compatibilità) — ogni rilascio deve essere assorbibile da un'istanza con le azioni del CHANGELOG.
- [Flussi verso l'esterno](../architecture/contratti-e-guasti.md#flussi-verso-lesterno) — lo strumento arriva con git o con lo zip, le pagine solo tramite l'agente.

## Ambienti

Risponde a `deployment-environments`.

| Ambiente | Cosa contiene | Come ci arriva un cambiamento |
| --- | --- | --- |
| Branch di lavoro | Il cambiamento in corso | Commit del manutentore |
| `main` su GitHub | La versione rilasciata | Pull request per gli script, commit diretto per il resto; sempre dopo i test |
| Strumento di un'istanza (`Documenti/Scrivano`) | L'intero repository: script e modelli in `src/`, con accanto `config.json` e `.stato/` dell'istanza; procedure in radice | `git pull`, o un nuovo zip che lascia `config.json` e `.stato/`, quando l'utente chiede *aggiorna Scrivano* |
| Pagine del Desktop dell'istanza | Copie adattate dei modelli | L'agente applica le azioni del CHANGELOG seguendo `AGGIORNA.md` |
| Desktop finto | Un'istanza di prova in una cartella temporanea | `tests/desktop_finto.py genera --strumento .` copia la copia di lavoro |

Rilasciato vuol dire su `main`: non ci sono tag né pacchetti. Un'istanza resta alla sua versione finché l'utente non chiede di aggiornarla.

## Procedura di rilascio

Risponde a `deployment-release-procedure`.

1. **Voce del CHANGELOG.** Un cambiamento a modelli o procedure aggiunge alla voce della data di oggi cosa cambia e le **Azioni per l'istanza**. Una sola voce per data: le modifiche dello stesso giorno si aggiungono alla sua voce, perché la data fa da versione ([ADR 0003](../adr/0003-la-data-del-changelog-fa-da-versione.md)).
2. **Azioni ripetibili.** Ogni azione si scrive in modo che applicarla due volte non faccia danni: un'istanza che si è aggiornata in quella data rilegge anche la voce del suo giorno, che nel frattempo può essersi allungata.
3. **Verifica.** I test passano; la prova completa sul Desktop finto conferma installazione e pagine.
4. **Pubblicazione.** Il cambiamento arriva su `main`.
5. **Aggiornamento di un'istanza.** L'agente legge la data dei modelli in «Questa istanza», aggiorna lo strumento, applica le azioni dalla voce più vecchia alla più recente, compresa quella del giorno registrato, aggiorna la data, poi esegue `links` e `scan` e chiude gli eventi delle pagine che ha aggiornato.

**Tornare indietro.** Non c'è un ritorno automatico. Uno strumento aggiornato con git torna a un commit precedente con git; le pagine del Desktop restano quelle aggiornate, perché sono dell'utente e un'azione già applicata non si disfa da sola. Un rilascio sbagliato si corregge con un rilascio nuovo e un'azione che ripara.

**Disinstallazione.** Il README la descrive: si cancellano lo strumento, l'eventuale registro fuori dallo strumento, le pagine del sistema e la configurazione di Codex; riordino e note restano.
