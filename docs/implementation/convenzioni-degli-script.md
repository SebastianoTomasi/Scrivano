# Convenzioni degli script di Scrivano

**Status:** proposed

## Scope

Fissa le convenzioni che `controlla.py` e `riordina.py` condividono: forma dei comandi, uscite ed errori, confronto dei percorsi e riconoscimento di link e file solo nel cloud. Le garanzie che queste convenzioni realizzano stanno in [Contratti e guasti](../architecture/contratti-e-guasti.md); registro e giornale in [Registro e giornale](registro-e-giornale.md).

## Dependencies

- [Flussi verso l'esterno](../architecture/contratti-e-guasti.md#flussi-verso-lesterno) — codici d'uscita e JSON sono il contratto con l'agente.
- [Dipendenze tra componenti](../architecture/sistema-e-componenti.md#dipendenze-tra-componenti) — senza import tra script, ogni convenzione è duplicata in entrambi.
- [Tecnologie](../stack/tecnologie.md#inventario) — solo libreria standard e API della 3.10.

## Convenzioni condivise

Risponde a `implementation-shared-conventions`. Valgono per i due script a riga di comando; i test seguono le stesse regole sui percorsi.

**Script autonomi.** Ogni script basta a se stesso: costanti e funzioni comuni (`stamp`, `digest`, `is_link`, `is_cloud`, `NOCASE`, il controllo della versione) sono copiate, non importate. Una correzione a una di queste funzioni va fatta in entrambi gli script.

**Solo API della 3.10.** Anche quando il Python in uso ne offre di più recenti. Per questo le junction si riconoscono dal reparse tag invece che con `DirEntry.is_junction` (3.12), e il flag dei file "dataless" di macOS è una costante scritta a mano invece di `stat.SF_DATALESS` (3.13).

**Uscite.** Un sottocomando `argparse` per azione. Il risultato è JSON su stdout, indentato e con `ensure_ascii=False`; stdout e stderr passano a UTF-8 all'avvio, perché PowerShell con un locale Windows vecchio rovinerebbe i percorsi con accenti. Le chiavi del JSON di `controlla.py` sono in inglese, quelle di `riordina.py` in italiano: fanno parte del contratto e non si traducono.

**Errori.** `OSError`, `ValueError` e, nel rilevatore, `sqlite3.Error` diventano `{"error": ...}` su stderr con codice 2. Un problema che il comando sa descrivere esce con codice 1 e il suo resoconto completo su stdout. I messaggi sono in italiano e dicono cosa fare ("rileggere la coda", "usare un nuovo ID radice"). Con Python più vecchio della 3.10 lo script si ferma prima di tutto, con lo stesso formato d'errore.

**Orari.** Gli istanti registrati sono UTC nel formato `AAAA-MM-GGTHH:MM:SSZ`; l'inventario mostra le date locali del giorno.

**Percorsi.** Nel registro e nei piani i percorsi sono relativi alla radice e separati da `/`. Due nomi si confrontano in forma NFC e, su Windows e macOS, senza maiuscole; le esclusioni non distinguono mai maiuscole e accenti. Un piano rifiuta percorsi assoluti, unità e `..`.

**Metadati aggiornati.** Il rilevatore legge dimensione e data con una `stat` nuova e non con quella di `os.scandir`, che per un file aperto in scrittura può essere vecchia.

**Link e junction.** Un elemento è un link se `stat` senza seguire link lo dice tale o se il suo reparse tag ha il bit "name surrogate" (`0x20000000`), lo stesso criterio di `os.lstat`. Gli altri reparse point, come i file di OneDrive, sono file normali.

**File solo nel cloud.** Su Windows lo dicono gli attributi offline, recall on open e recall on data access; su macOS il flag `0x40000000` dei file "dataless". Un file così non si apre: niente impronta, niente lettura dei primi byte.

**Comportamenti di piattaforma nei test.** Ciò che il sistema in uso non riproduce si simula: attributi del cloud, reparse tag, accenti scomposti, maiuscole che non contano.
