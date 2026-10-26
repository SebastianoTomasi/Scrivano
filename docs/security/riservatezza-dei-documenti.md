# Riservatezza dei documenti in Scrivano

**Status:** proposed

## Scope

Fissa i controlli che proteggono i documenti dell'utente e i dati che Scrivano ne ricava: cosa non si apre, cosa non esce dal PC, cosa non si copia nelle note e quanto restano registro e giornali. Le classi di dati e i loro vincoli stanno in [Dati e obblighi](../product/dati-e-obblighi.md); dove passano i confini e chi li fa rispettare in [Dati e fiducia](../architecture/dati-e-fiducia.md). Identità e permessi non servono: un'istanza ha un solo utente e gira con il suo account del PC.

## Dependencies

- [Classi di dati](../product/dati-e-obblighi.md#classi-di-dati) — ogni controllo protegge una classe elencata lì.
- [Confini di fiducia](../architecture/dati-e-fiducia.md#confini-di-fiducia) — i controlli si applicano ai confini tra documenti, agente, rete e repository.

## Protezione dei dati

Risponde a `security-data-protection`.

**Segreti.** Un file con un nome da segreto (`.env`, chiavi, certificati, archivi di password, nomi che contengono "password" o "credenziali") non si apre, non si sposta e non si copia: l'agente lo segnala all'utente. L'inventario li elenca in `segreti` senza leggerli, salvo i primi quattro byte di un `.key` locale per riconoscere una presentazione Keynote; il rilevatore li esclude con le esclusioni della configurazione. Il riconoscimento è per nome e non garantisce di trovare ogni segreto.

**Identificativi.** IBAN, numeri di carta, codici, documenti d'identità e firme restano negli originali: le note li collegano senza trascriverli e non li mandano a servizi esterni.

**Dati sanitari ed economici.** Seguono le regole locali delle guide di Salute e Finanze, che il catalogo dei domini porta già.

**In transito.** Gli script non usano la rete. Ciò che l'agente legge arriva al fornitore del modello: l'agente legge solo ciò che serve alla richiesta e il README lo dice all'utente.

**A riposo.** Scrivano non cifra nulla: documenti, note, registro e giornali sono protetti dall'account dell'utente sul PC. Il registro contiene percorsi, dimensioni, date, impronte e note di revisione, mai copie dei contenuti.

**Note private.** Le note dell'archivio non si esportano nei repository o nei servizi condivisi, anche quando riguardano il lavoro.

**Repository.** Nessun dato di un'istanza entra nel repository: `config.json` e `.stato/` sono ignorati da git e i modelli sono anonimi.

**Conservazione.** Gli eventi del registro, con le loro note, si conservano senza scadenza; anche i giornali dei piani restano nello strumento. Disinstallare cancella strumento e registro; riordino e note restano.

## Punti aperti

- Gli eventi e i giornali si conservano senza scadenza, o serve un modo per sfoltirli?
