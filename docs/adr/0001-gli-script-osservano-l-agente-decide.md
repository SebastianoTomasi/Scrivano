# Gli script osservano ed eseguono, l'agente decide

Scrivano si installa su PC di persone che non programmano, partendo da un Desktop disordinato. Non c'è un plugin né un installatore: l'installazione la fa l'agente, seguendo istruzioni scritte in `INSTALLA.md`, e le pagine del Desktop gli danno obiettivi, principi e poche regole di sicurezza, lasciando a lui quante domande fare, come adattare la tassonomia e quando sfoltire la coda. Gli script esistono solo dove servono garanzie che non possono dipendere dal giudizio: spostare senza perdere nulla (`riordina.py`, con piano approvato, giornale e annullamento) e sapere cosa è cambiato (`controlla.py`).

## Considered Options

- **Plugin o installatore deterministico.** Scartato come eccessivo: la soluzione più semplice che regge è un agente che segue istruzioni.
- **Spostamenti fatti direttamente dall'agente.** Scartati per il riordino: negli spostamenti servono garanzie che solo uno script dà sempre, cioè piano controllato per intero, nessuna sovrascrittura, giornale scritto prima di ogni mossa e annullamento.
- **Regole rigide e passo per passo nelle pagine.** Scartate: le pagine dicono a cosa serve ogni regola, così valgono anche nei casi che non descrivono.
