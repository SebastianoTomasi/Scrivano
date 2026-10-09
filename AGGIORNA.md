# Aggiornare Scrivano

Procedura per l'agente quando l'utente chiede di aggiornare il sistema già installato. Le pagine del Desktop appartengono all'utente: un aggiornamento le integra, senza sovrascriverle.

1. Dalla sezione «Questa istanza» dell'`AGENTS.md` del Desktop leggi il percorso dello strumento e la data dei modelli.
2. Aggiorna lo strumento:
   - con git: `git -C "<strumento>" pull`;
   - senza git: scarica lo zip del repository e sostituisci i file dello strumento, lasciando `config.json` e `.stato/`.
3. Nel [CHANGELOG](./CHANGELOG.md) leggi le voci dalla data dei modelli in poi, compresa quella stessa data, che può essersi allungata, e applica le loro **Azioni per l'istanza** non ancora fatte, dalla più vecchia alla più recente: porta le modifiche dei [modelli](./modelli/) nelle pagine del Desktop rispettando gli adattamenti locali e adegua `config.json` se serve.
4. Aggiorna la data dei modelli in «Questa istanza». Poi, dallo strumento, esegui `links` e `scan` e chiudi con una nota gli eventi delle pagine che hai aggiornato.

Fatto quando strumento e pagine corrispondono alla voce più recente del CHANGELOG e `links` non segnala problemi.
