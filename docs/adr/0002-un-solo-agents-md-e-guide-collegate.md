# Un solo AGENTS.md, guide collegate

Il Desktop ha un solo `AGENTS.md`, nella radice; le guide dei domini sono file Markdown normali, `GUIDA.md`, raggiunti dai link della mappa. Codex non carica gli `AGENTS.md` sotto la cartella da cui parte, mentre Claude Code li caricherebbe solo leggendo un file lì dentro: un link esplicito funziona allo stesso modo con entrambi gli agenti.

## Considered Options

- **Un `AGENTS.md` per dominio.** Scartato: i due agenti lo leggerebbero in momenti diversi, o Codex mai.
- **`CLAUDE.md` al posto o accanto ad `AGENTS.md`.** Scartato: un `CLAUDE.md`, `CLAUDE.local.md` o `.claude/CLAUDE.md` nel Desktop o più in alto fa leggere a Claude Code quello invece di `AGENTS.md`, e Codex non lo legge.
