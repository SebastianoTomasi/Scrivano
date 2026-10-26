# Flusso di lavoro e test di Scrivano

**Status:** proposed

## Scope

Dice come un cambiamento al repository arriva su `main` e quali prove deve portare. Come un cambiamento arriva poi alle istanze sta in [Rilascio e aggiornamento](../deployment/rilascio-e-aggiornamento.md); i criteri con cui si giudica il prodotto da fuori in [Criteri di successo](../product/compatibilita-e-collaudo.md#criteri-di-successo).

## Dependencies

- [Classi di dati](../product/dati-e-obblighi.md#classi-di-dati) — il repository è pubblico, quindi nessun dato di un'istanza entra nei commit.
- [Criteri di successo](../product/compatibilita-e-collaudo.md#criteri-di-successo) — le prove di un cambiamento sono quelle che dimostrano i criteri che il cambiamento tocca.
- [Convenzioni degli script](../implementation/convenzioni-degli-script.md#convenzioni-condivise) — i test simulano i comportamenti di piattaforma che il sistema in uso non riproduce.

## Flusso di lavoro

Risponde a `development-workflow`.

- **Branch e pull request per gli script.** Un cambiamento a `controlla.py` o `riordina.py` si fa su un branch e arriva su `main` con una pull request. Modelli, procedure e documenti possono andare direttamente su `main`.
- **Prima di consegnare.** `python -m unittest discover -s tests -v` passa.
- **Nello stesso commit.** Se cambiano comandi, formato della configurazione o del piano, o il comportamento della coda, il README si aggiorna insieme al codice. Se cambiano modelli o procedure, il CHANGELOG riceve la voce del giorno con le azioni per l'istanza, come dice [Rilascio e aggiornamento](../deployment/rilascio-e-aggiornamento.md#procedura-di-rilascio).
- **Repository pubblico.** Restano fuori `config.json`, `.stato/`, percorsi, nomi, note e dati personali, anche dai messaggi di commit. Modelli e procedure sono generici, con segnaposto `{{...}}`.
- **Messaggi di commit.** In italiano, con un prefisso come `feat`, `fix` o `docs` e, se serve, il componente tra parentesi: `fix(riordina): ...`.

## Test

Risponde a `development-test-strategy`.

| Tipo | Cosa copre | Quando serve |
| --- | --- | --- |
| Test degli script (`tests/test_controlla.py`, `tests/test_riordina.py`) | Rilevamento, coda, revisione, conflitti, errori, concorrenza, esclusioni, link; inventario, piani, ripresa, annullamento, lucchetto. Lavorano solo in cartelle temporanee e simulano cloud, junction, accenti scomposti e maiuscole | A ogni cambiamento degli script; un comportamento nuovo porta il suo test |
| Test del Desktop finto (`tests/test_desktop_finto.py`) | Il generatore produce un Desktop disordinato, uguale a parità di seme, anche nella versione Mac, e `verifica` rifiuta un Desktop non installato | A ogni cambiamento del generatore o della verifica |
| Prova completa | Un agente segue `INSTALLA.md` in modalità prova su un Desktop finto, poi `tests/desktop_finto.py verifica` controlla il risultato | Quando cambiano `INSTALLA.md`, i modelli o il comportamento di inventario e piano. Basta un agente; servono Claude Code e Codex quando cambia `INSTALLA.md` |

Il Desktop finto ha nomi realistici, collegamenti, un repository git, duplicati, un finto file di credenziali, nomi con accenti e parentesi quadre; con `--mac` aggiunge metadati del Finder, una presentazione Keynote accanto a una chiave vera e un pacchetto. Per la prova completa `INSTALLA.md` accetta una radice diversa dal Desktop. Codex gira con `codex exec` nella sandbox `workspace-write`, che gli lascia scrivere solo nella cartella di prova.

Cancellazioni e spostamenti si provano solo in cartelle temporanee, mai su documenti personali.
