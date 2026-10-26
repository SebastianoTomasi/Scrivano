# Scopo e persone di Scrivano

**Status:** proposed

## Scope

Dice a cosa serve Scrivano, per chi è e quali parti agiscono sull'archivio o vi compaiono. Le classi di dati e gli obblighi stanno in [Dati e obblighi](dati-e-obblighi.md); capacità e non-obiettivi in [Capacità e confini](capacita-e-confini.md).

## Scopo

Risponde a `product-purpose`.

Scrivano mette in ordine il Desktop di una persona e ne fa un archivio personale che il suo agente, Claude Code o Codex, sa consultare e tenere aggiornato. La persona chiede all'agente ("dov'è il contratto d'affitto?", "quanto ho speso di luce quest'anno?") invece di cercare tra le cartelle.

Senza Scrivano, chi usa un agente sul proprio PC ha un Desktop che l'agente non sa leggere: lo esplora da capo a ogni sessione, non sa cosa è cambiato dall'ultima volta e le sintesi che scrive restano indietro rispetto ai documenti. Scrivano gli dà domini con una guida ciascuno, una mappa che porta alla guida giusta e un rilevatore che dice cosa rileggere.

## Utente principale

Risponde a `primary-user`.

Una persona sola, proprietaria del Desktop, che usa Claude Code o Codex su Windows 11 o macOS e parla italiano. Non serve che sappia programmare.

Si dà per scontato che abbia un agente funzionante, sappia aprirlo su una cartella e sappia leggere un riassunto per approvarlo o correggerlo a parole.

Non si dà per scontato che:

- abbia Python 3.10 o successivo: lo installa l'agente, con il suo consenso;
- abbia git: in alternativa l'agente usa lo zip del repository;
- conosca percorsi, comandi o il formato delle pagine: le pagine le scrive e le legge l'agente, e l'utente vede riassunti e decisioni.

Per questo Scrivano porta da sé installazione, spiegazioni e manutenzione: l'utente decide, l'agente esegue.

## Attori e soggetti

Risponde a `actors-and-subjects`.

| Parte | Ruolo |
| --- | --- |
| Utente | Proprietario del Desktop e dei documenti. Approva domini e riordino, dice sì o no a ogni spostamento, corregge a parole e può tornare indietro. |
| Agente | Claude Code o Codex aperto sul Desktop. Interpreta, propone e decide entro le regole delle pagine; scrive pagine e note; lancia gli script. Agisce per conto dell'utente. |
| Script | `controlla.py` e `riordina.py`. Osservano ed eseguono: non interpretano e non decidono. |
| Fornitore del modello | Anthropic per Claude, OpenAI per Codex. Riceve ciò che l'agente legge; sta fuori dal sistema. |
| Autori dei documenti | Chi ha scritto un documento che sta sul Desktop: una banca, un medico, uno sconosciuto. Il loro testo è un dato e non dà istruzioni all'agente. |
| Familiari e terzi | Persone i cui dati compaiono nei documenti dell'utente, come i referti di un familiare. Sono soggetti, non attori: non usano l'istanza. |
| Manutentore del repository | Sviluppa strumento, modelli e procedure. Non vede nessuna istanza. |

Un'istanza serve una sola persona: il suo Desktop e le sue cartelle esterne. Gli altri utenti dello stesso PC restano fuori, compreso il `Public\Desktop` di Windows. Un PC di famiglia con un account condiviso non è un caso sostenuto: i familiari compaiono solo come soggetti dei documenti.
