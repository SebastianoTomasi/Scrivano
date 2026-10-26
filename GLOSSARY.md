# Scrivano

Scrivano fa del Desktop di una persona un archivio personale che il suo agente consulta e tiene aggiornato. Queste sono le parole del sistema, usate da procedure, modelli e pagine del Desktop.

## Istanza

**Istanza**:
Scrivano installato sul PC di una persona: lo strumento, la sua configurazione e le pagine del sistema sul Desktop.
_Evita_: installazione, per indicare il risultato

**Istanza di riferimento**:
L'istanza da cui sono stati ricavati i modelli anonimi.

**Strumento**:
La copia del repository dentro un'istanza, con script, modelli e procedure.
_Evita_: tool, programma

**Versione dei modelli**:
La data della voce del CHANGELOG a cui corrispondono le pagine di un'istanza.
_Evita_: numero di versione

**Azioni per l'istanza**:
I passi, ripetibili senza danni, che portano un'istanza già installata a una voce del CHANGELOG.

**Prova**:
Un'installazione su un Desktop finto, con cartelle di prova al posto di quelle vere.

## Archivio

**Archivio**:
Il Desktop organizzato da Scrivano: domini, pagine del sistema, note e documenti.
_Evita_: sistema di conoscenza, memoria

**Radice del Desktop**:
Il primo livello del Desktop, dove arrivano i file nuovi prima di andare in un dominio.

**Dominio**:
Una cartella di primo livello dell'archivio che risponde a una famiglia di domande, come Finanze o Salute.
_Evita_: categoria, area, cartella per tipo di file

**Cartella esterna**:
Una cartella fuori dal Desktop che l'archivio collega senza organizzarla, come Documenti o Download.

**Pagine del sistema**:
Le pagine che Scrivano mette sul Desktop: regole comuni, mappa, manutenzione e guide.

**Modello**:
La pagina del repository da cui nasce una pagina del sistema.
_Evita_: template

**Regole comuni**:
L'`AGENTS.md` della radice del Desktop, valido in tutto l'archivio.
_Evita_: istruzioni

**Mappa**:
La pagina che porta dalle parole di una domanda alla guida del dominio.

**Guida**:
La pagina di un dominio che ne dice confine, regole locali, dove va cosa, ingressi e copertura.

**Guida annidata**:
La guida di una sottocartella con regole proprie o troppe cose per capirsi dai nomi, collegata dalla guida del genitore.

**Ingresso**:
Un collegamento di una guida o della mappa a una cartella o a una nota da cui partire.

**Copertura di una guida**:
Quanto di un dominio è stato letto: censito, parzialmente esaminato o interpretato.

**Censito**:
Si sa dov'è, ma non è stato letto.

**Parzialmente esaminato**:
Ne è stata letta una parte, indicata dalla guida.

**Interpretato**:
Esiste una sintesi collegata alle fonti.

**Nota canonica**:
La sola nota che raccoglie ciò che si sa di un tema.
_Evita_: riassunto, appunto

**Fonte**:
Un materiale usato per scrivere una nota, conservato accanto a essa.

**Originale**:
Un documento dell'utente, come un contratto o un referto, che resta nella sua cartella e che la nota collega senza copiarlo.

**Cartella Archivio**:
La cartella di un dominio dove le istanze nate prima del 2026-10-26 mettevano ciò che era superato; `links` la salta ancora. Oggi il superato va nel Cestino, dopo il sì dell'utente.
_Evita_: archivio, da solo

## Rilevamento

**Rilevatore**:
Il componente che osserva le radici e dice cosa è cambiato dall'ultima scansione.

**Radice osservata**:
Una cartella che il rilevatore osserva, con un nome e una profondità.
_Evita_: radice, da sola

**Copertura del rilevatore**:
Le radici osservate, con profondità ed esclusioni.

**Base**:
Lo stato osservato alla prima scansione di una radice, che non dichiara letto nessun documento.
_Evita_: baseline

**Scansione**:
Il confronto delle radici osservate con l'ultimo stato registrato.

**Evento**:
Un cambiamento registrato di un percorso: aggiunta, modifica o cancellazione.

**Coda**:
Gli eventi pendenti, dal più recente.

**Pendente**:
Un evento non ancora revisionato e non superato.

**Superato**:
Un evento sostituito da un cambiamento più recente dello stesso percorso.

**Revisione**:
La chiusura di eventi riconciliati, con una nota che dice cosa è stato verificato.

**Impronta**:
Il riassunto del contenuto di un file che dice se è cambiato.

**Rinomina suggerita**:
Una coppia di cancellazione e aggiunta con lo stesso contenuto, che il rilevatore indica senza applicarla.

**Rumore**:
Eventi che si ripetono senza richiedere lavoro, candidati a un'esclusione.

**Registro**:
Dove il rilevatore conserva stato osservato ed eventi.

## Riordino

**Riordino**:
Lo spostamento di file e cartelle secondo un piano approvato dall'utente.

**Livello di riordino**:
Quanto si sposta all'installazione: completo, leggero o nessuno.

**Inventario**:
Il riassunto di una cartella da cui l'agente decide cosa proporre.

**Unità**:
Ciò che si sposta senza dividerlo: un file sparso, o una cartella con un'identità come un progetto, un corso, un viaggio o una pratica.

**Cartella-contenitore**:
Una cartella anonima, come "Nuova cartella", che si può svuotare collocandone il contenuto.

**Cartella-progetto**:
Una cartella di software o simile, che si sposta intera o resta dov'è.

**Pacchetto**:
Una cartella che macOS mostra come un solo documento o un'app.

**Piano**:
L'elenco delle mosse di un riordino, scritto dall'agente e approvato dall'utente.

**Mossa**:
Lo spostamento di un'unità da un percorso a un altro.

**Giornale**:
La traccia delle mosse di un piano, scritta prima di ciascuna.

**Annullamento**:
Il ritorno dei file dove stavano, ripercorrendo il giornale al contrario.

**Collegamento**:
Un file che apre un'applicazione o un sito, come `.lnk`, `.url`, un alias del Finder o un `.webloc`; si sposta come gli altri file.
_Evita_: link, scorciatoia

**Link simbolico**:
Un rimando del file system a un altro percorso, compresa la junction di Windows; non si segue e non si sposta.
_Evita_: collegamento

**Segreto**:
Un file con un nome da chiave o da password, segnalato senza aprirlo.

**File solo nel cloud**:
Un file che sul PC è solo un segnaposto e si scaricherebbe aprendolo.

**Metadati rigenerati**:
`.DS_Store` e `Thumbs.db`, che Finder ed Esplora risorse ricreano da soli.
