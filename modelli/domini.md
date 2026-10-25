# Catalogo dei domini

Punto di partenza per proporre i domini di un Desktop e scriverne le guide. Si adatta al materiale che c'è: non si applica per intero.

## Come scegliere

- Un dominio risponde a una famiglia di domande ("dov'è il libretto della macchina?", "quanto ho speso di luce?"), non a un tipo di file: niente cartelle "PDF", "Immagini" o "Documenti".
- Proponi solo domini con materiale. Un sottotema diventa dominio quando è grande e si cerca da solo; altrimenti resta una sottocartella.
- Quando un documento starebbe bene in due domini, decide il suo oggetto: contratto, polizza e manutenzione di un bene (la casa, l'auto) stanno insieme al bene in Personale; i pagamenti ricorrenti, come bollette e rate, in Finanze; le garanzie degli acquisti in Amministrazione.
- Nomi in italiano, PascalCase ASCII. Una cartella esistente con un nome riconoscibile può diventare il dominio senza cambiare nome.
- Ciò che non trova posto resta nella radice del Desktop, che fa da ingresso.

Per ogni dominio: cosa possiede, a chi rimanda, le regole locali da riportare nella guida e le sottocartelle che di solito servono, da cui parte la sezione «Dove va cosa» della guida.

## Domini di base

### Amministrazione

- **Possiede:** pratiche e documenti personali senza un dominio più specifico: identità, residenza, contratti che non riguardano un bene, acquisti e garanzie, certificati.
- **Rimanda a:** banche e tasse → Finanze; sanità → Salute; CV e contratti di lavoro → Lavoro; titoli di studio → Studi.
- **Regole locali:**
  - Conserva i documenti con la pratica a cui appartengono.
  - Identificativi e firme restano negli originali, senza trascriverli nelle note o trasmetterli a servizi esterni.
  - Gli altri domini collegano le fatture conservate qui senza copiarle.
- **Sottocartelle tipiche:** `Identita`, `Contratti`, `Acquisti/<Fornitore>`, una per pratica.

### Finanze

- **Possiede:** bilancio personale, entrate e spese, bollette e rate, buste paga, banche, investimenti, tasse e dichiarazioni.
- **Rimanda a:** lavoro e contratti → Lavoro; casa e beni → Personale; identità → Amministrazione.
- **Regole locali:**
  - Le note possono riportare i dati economici durevoli. Indica data, unità, periodicità, lordo/netto, fonte e certezza quando applicabili.
  - Distingui fatti, stime e scenari.
  - IBAN, numeri di carte, codici e credenziali restano fuori dalle note. Conserva i documenti originali senza trascriverne gli identificativi.
- **Sottocartelle tipiche:** una per banca, `Tasse/<Anno>`, `BustePaga/<Anno>`, `Investimenti`.

### Salute

- **Possiede:** salute personale, visite, referti, prescrizioni, analisi e documenti sanitari.
- **Rimanda a:** identità e tessera sanitaria → Amministrazione; sport e benessere → Personale.
- **Regole locali:**
  - Distingui dichiarazioni dell'utente, indicazioni professionali e questioni da chiarire.
  - Un nuovo documento non autorizza inferenze diagnostiche o la sostituzione di indicazioni mediche.
  - Conserva gli originali; non copiare gli identificativi nelle sintesi né trasmettere documenti a servizi esterni.
- **Sottocartelle tipiche:** `Referti`, `Prescrizioni`; una per persona se il PC raccoglie documenti di più familiari.

### Lavoro

- **Possiede:** percorso professionale, CV, contratti di lavoro, candidature e opportunità, materiali di lavoro personali.
- **Rimanda a:** compensi e tasse → Finanze; formazione → Studi; pratiche → Amministrazione.
- **Regole locali:**
  - Distingui opportunità, valutazioni e decisioni.
  - L'archivio è privato anche quando riguarda il lavoro: i materiali condivisi dall'azienda restano negli strumenti dell'azienda.
- **Sottocartelle tipiche:** `CV`, una per azienda, cliente o incarico, `Candidature/<Ente>`.

### Studi

- **Possiede:** scuola, università, corsi, certificazioni, tesi e materiali di studio.
- **Rimanda a:** lavoro → Lavoro; iscrizioni, tasse e attestati → Amministrazione.
- **Regole locali:**
  - Mantieni i nomi riconoscibili dei corsi, anche con spazi: sono un'eccezione al PascalCase.
  - Per cercare, parti dal corso e scendi un livello alla volta; evita letture integrali della raccolta.
- **Sottocartelle tipiche:** una per corso, `Tesi`, `Certificazioni`.

### Personale

- **Possiede:** casa e vita domestica; beni (casa, veicoli, dispositivi) con i loro contratti, polizze e manutenzione; hobby, viaggi, foto, famiglia.
- **Rimanda a:** spese e bilancio → Finanze; salute → Salute; pratiche e contratti → Amministrazione.
- **Regole locali:**
  - Prima di modificare o spostare foto usate altrove (profili, CV), verifica gli usi.
- **Sottocartelle tipiche:** `Casa`, `Foto/<Anno o evento>`, `Viaggi/<Anno Luogo>`, `Dispositivi`, `Veicoli/<Veicolo>`, una per hobby.

### Collegamenti

- **Possiede:** collegamenti ad applicazioni e siti: `.lnk` e `.url` su Windows, alias del Finder e `.webloc` su macOS; documenti, dati ed eseguibili appartengono agli altri domini.
- **Regole locali:**
  - La presenza di un collegamento non prova che l'applicazione sia ancora installata.
  - I collegamenti usati ogni giorno possono restare nella radice del Desktop; su Windows quelli di `Public\Desktop` sono fuori perimetro.
  - Un collegamento non risolvibile si segnala all'utente, invece di eliminarlo.

## Domini facoltativi

### Progetti

Per chi scrive software o costruisce strumenti.

- **Possiede:** software, siti e strumenti personali.
- **Regole locali:** i repository mantengono percorsi, nomi, ambienti e istruzioni propri; si spostano interi o restano dove sono.

### Ricerca

Per chi fa ricerca, anche fuori da un incarico.

- **Possiede:** domande scientifiche, esperimenti, risultati, idee e letteratura.
- **Regole locali:** distingui ipotesi, risultati osservati ed esperimenti proposti.

### Un'attività propria

Per chi ha un'azienda, una partita IVA o un'associazione; il dominio prende il nome dell'attività.

- **Possiede:** contesto privato sull'attività: prodotti, clienti, offerte, strategia, costituzione.
- **Rimanda a:** percorso personale → Lavoro; bilancio personale → Finanze.
- **Regole locali:**
  - L'archivio è privato anche quando riguarda il lavoro; i repository e gli strumenti condivisi non ne ricevono automaticamente le note.
  - Prodotti e clienti autonomi possono avere cartelle proprie, con le fonti vicine.

### Casa

Quando la casa produce molto materiale (mutuo o affitto, condominio, utenze, lavori) può staccarsi da Personale.

- **Possiede:** contratti della casa, utenze, condominio, manutenzione e lavori.
- **Rimanda a:** spese → Finanze; residenza → Amministrazione.

## Schemi di sottocartelle e nomi

- **Per pratica:** una cartella per pratica, con moduli e allegati insieme.
- **Per ente o fornitore:** `<Banca>/`, `Acquisti/<Fornitore>/`.
- **Per anno:** `<Tema>/<AAAA>/`, quando i documenti si cercano per anno (tasse, buste paga, foto).
- **Per evento:** `<Luogo> <AAAA-MM>/` per viaggi, trasferte, cerimonie.
- **Per persona:** `<Nome>/` dentro un dominio, se il PC raccoglie documenti di più familiari.
- **Per bene:** `Veicoli/<Veicolo>/`, `Casa/<Indirizzo>/`: documenti, manutenzione e note insieme.
- **Per progetto:** la cartella del progetto si sposta intera, senza toccarne l'interno.
- **Nomi dei file:** restano quelli originali. Una cartella può darsi una convenzione, scritta in «Dove va cosa» della guida, per esempio `AAAA-MM-GG Oggetto` per i documenti datati o `Fornitore AAAA-MM` per le bollette: serve ai nomi che non dicono nulla (`scan0001.pdf`, `Documento (2).pdf`), che si rinominano con quella, insieme allo spostamento.
