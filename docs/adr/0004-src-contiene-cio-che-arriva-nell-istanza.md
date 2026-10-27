# `src/` contiene ciò che arriva nell'istanza

Il repository tiene insieme il prodotto e ciò che serve a svilupparlo: le regole del delivery process advisor, gli artifact in `docs/`, il glossario, gli ADR e i test. Mescolati nella radice, non si capiva quali file arrivano sul PC di chi installa Scrivano e quali governano solo il lavoro sul repository. Come nel repository dell'advisor, il prodotto sta in `src/`: i due script, `config.example.json` e i modelli delle pagine del Desktop, cioè ciò che un'istanza esegue o copia. Un'istanza tiene lì anche la sua `config.json` e la cartella `.stato/`, accanto agli script e ignorate da git.

In radice restano `INSTALLA.md`, `AGGIORNA.md`, `CHANGELOG.md` e il README. Le due procedure fanno per Scrivano quello che l'installatore fa per l'advisor, che sta anch'esso fuori da `src/`: portano il prodotto nell'istanza senza esserne parte. Lo strumento resta la copia dell'intero repository: `src/` separa i ruoli, non cambia cosa si scarica.

## Considered Options

- **Anche le procedure in `src/`.** Scartato: un'istanza si aggiorna seguendo la procedura che ha già, e quella cerca `CHANGELOG.md` nella radice; spostarlo avrebbe lasciato le istanze esistenti senza la voce che spiega lo spostamento.
- **`config.json` e `.stato/` nella radice dello strumento.** Scartato: `controlla.py` cerca la configurazione accanto a sé, e tenerla fuori da `src/` avrebbe chiesto un percorso predefinito legato alla forma del repository o un `--config` in ogni comando delle pagine.
- **`src/` come specchio del Desktop, alla maniera di `src/target/` dell'advisor.** Scartato: un modello non ha una destinazione fissa, perché `GUIDA.md` va in ogni dominio e il catalogo non diventa una pagina, e l'agente adatta i modelli invece di copiarli.
