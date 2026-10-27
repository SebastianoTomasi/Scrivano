# Dati e obblighi di Scrivano

**Status:** accepted

## Scope

Elenca le classi di dati che Scrivano tocca, dice quali non sono libere di muoversi e quali obblighi esterni valgono. I controlli che ne derivano stanno in [Riservatezza dei documenti](../security/riservatezza-dei-documenti.md); chi può scrivere ciascun dato sta in [Dati e fiducia](../architecture/dati-e-fiducia.md).

## Dependencies

- [Attori e soggetti](scopo-e-persone.md#attori-e-soggetti) — le classi distinguono i dati dell'utente da quelli di terzi e da ciò che arriva al fornitore del modello.

## Classi di dati

Risponde a `data-classes`.

| Classe | Esempi | Vincolo |
| --- | --- | --- |
| Documenti dell'utente | contratti, bollette, foto, CV | Personali. Si spostano solo con un piano approvato e gli script non li modificano. |
| Dati sanitari | referti, prescrizioni, anche di familiari | Restano negli originali; le note distinguono ciò che dice l'utente da ciò che dice il medico e non fanno diagnosi. |
| Dati economici | estratti conto, buste paga, tasse | Le note possono riportare importi durevoli; IBAN, numeri di carta e codici restano negli originali. |
| Identificativi | documenti d'identità, codice fiscale, firme | Restano negli originali, fuori dalle note e dai servizi esterni. |
| Segreti | chiavi, `.env`, file di password | Non si aprono, non si spostano e non si copiano: si segnalano all'utente. Il loro posto è il password manager. |
| Note e pagine dell'archivio | note canoniche, guide, mappa | Dell'utente e private: non si esportano nei repository o nei servizi condivisi. |
| Registro del rilevatore | percorsi, dimensioni, date, impronte, note di revisione | Metadati, senza copie dei contenuti; restano sul PC. |
| Piani e giornali del riordino | percorsi prima e dopo ogni mossa | Restano nello strumento dell'istanza. |
| Configurazione dell'istanza | percorsi delle radici, esclusioni | Personale: mai nel repository. |
| Repository | script, modelli, procedure, esempi | Pubblico: niente percorsi, nomi o dati di un'istanza, nemmeno nei messaggi di commit. |

Ciò che l'agente legge passa al fornitore del modello. È l'unico dato che lascia il PC per opera del sistema, e il README lo dice all'utente. Per questo l'agente legge solo ciò che serve alla richiesta.

## Obblighi esterni

Risponde a `legal-and-privacy-obligations`.

Nessun obbligo esterno lega il prodotto oltre la licenza MIT del repository. Scrivano gira sul PC dell'utente per uso personale e il progetto non raccoglie né riceve dati di nessuno. Ciò che l'agente legge segue i termini che l'utente ha accettato con il fornitore del modello. Le regole di riservatezza qui sopra sono scelte di prodotto, non obblighi.
