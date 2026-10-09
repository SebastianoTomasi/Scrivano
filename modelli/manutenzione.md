# Manutenzione della conoscenza

Usa questa pagina quando aggiorni note o struttura. Le autorizzazioni e le regole comuni sono in [AGENTS.md](./AGENTS.md).

## Scrivere e aggiornare

1. Trova il dominio e leggi la nota canonica; cerca eventuali duplicati prima di crearne una.
2. Confronta informazione nuova e precedente: fonte, data dei fatti, certezza e decisioni coinvolte.
3. Rileggi il file se è cambiato dopo l'apertura. Aggiorna lo stato nella nota; conserva solo le transizioni utili nel changelog locale.
4. Collega la nota dalla guida del dominio e dagli altri temi quando la relazione aiuta a ritrovarla. Sistema i riferimenti ai percorsi modificati.
5. Verifica link, copertura dichiarata ed eventi pertinenti prima di concludere.

Una nota deve rendere chiari **tema, stato noto, fonte/data e questioni aperte**, dove applicabili. Basta testo leggibile: niente campi vuoti o frontmatter obbligatorio, salvo standard locali. Per un lavoro in corso annota il punto di ripresa quando serve.

## Note, fonti e archivio

- **Nota canonica.** Prende il nome del tema in maiuscolo, con trattini bassi (`BOLLETTE_CASA.md`). Una forma che regge bene: sintesi in apertura, stato corrente con la data, decisioni prese, provvisorie e aperte, questioni da chiarire, collegamenti, fonti. Usa solo le sezioni che servono.
- **Fonti.** I materiali usati per una nota (ricerche, preventivi, estratti) stanno in `FONTI/` accanto alla nota, con nomi `TIPO_TEMA_AAAA-MM-GG` (`PREVENTIVO_CUCINA_2026-03-02.pdf`). Una fonte trascritta in Markdown apre con provenienza e data. Gli originali (contratti, referti, documenti d'identità) restano nelle loro cartelle e la nota li collega senza copiarli.
- **Archivio.** Ciò che è superato va in `Archivio/` dentro lo stesso dominio, con una riga in testa che lo dichiara storico. `links` non controlla le cartelle `Archivio`.

## Scrivere le pagine del sistema

| Pagina | Contiene | Quando aggiungerla |
| --- | --- | --- |
| `AGENTS.md` | Regole comuni, avvio del lavoro e specificità dell'istanza | Solo nella radice del Desktop |
| `GUIDA.md` | Confine, rimandi ai domini vicini, regole locali, ingressi utili con una riga sul loro scopo, copertura | In ogni dominio; in una sottocartella quando servono regole diverse da quelle del dominio |
| `MAPPA.md` | Link agli ingressi utili, una riga sul loro scopo, copertura | Nella radice; in un dominio quando la guida non basta più a orientare |
| Nota canonica | Fatti, decisioni, motivazioni e fonti del tema | Il tema è cercabile e aggiornabile da solo |
| `CHANGELOG.md` | Transizioni che spiegano lo stato corrente | La storia aiuta a capire una decisione |
| `README.md` | Uso, configurazione e limiti di uno strumento | Esiste uno strumento da usare o mantenere |

Claude Code e Codex leggono `AGENTS.md` direttamente. Niente `CLAUDE.md` o `CLAUDE.local.md` nel Desktop o più in alto: Claude Code leggerebbe quelli al posto di `AGENTS.md`. Le guide sono file normali raggiunti dai link: Codex non carica gli `AGENTS.md` sotto la cartella di avvio e Claude li caricherebbe solo leggendo file lì dentro, mentre un link funziona allo stesso modo per entrambi. Con Codex, `.codex-root` segna il Desktop come radice di progetto (`project_root_markers` in `~/.codex/config.toml`): una sessione aperta in una sottocartella legge comunque l'`AGENTS.md` della radice, tranne dentro un repository, che ha le sue istruzioni.

- Scrivi la regola una volta, nella sede competente; altrove rimanda. Usa verbi operativi e specifica quando un'azione serve.
- Mantieni selettivi gli ingressi di guide e mappe: collegamenti utili, non inventari completi né copie dello stato corrente.
- Riusa ingressi esistenti, come un README o un indice già presenti. Non creare una serie di file vuoti per ogni cartella.
- Dichiarazione di copertura: **censito** = percorso individuato; **parzialmente esaminato** = specifica la parte letta; **interpretato** = sintesi collegata alle fonti. La scansione tecnica non promuove la copertura.
- `Verificato: AAAA-MM-GG` chiude guide e mappe dopo un controllo effettivo di percorsi e coerenza. Non aggiorna la data dei fatti nelle note.

## Revisionare i cambiamenti

All'avvio segui [AGENTS.md](./AGENTS.md#avvio-del-lavoro). I comandi usano il percorso completo dello strumento, così funzionano da qualsiasi cartella senza cambiarla:

```powershell
python "{{strumento}}/controlla.py" pending --root Desktop --prefix Finanze --limit 30
```

La coda parte dal cambiamento più recente. `--prefix` è il percorso relativo alla radice; `--depth 1` mostra solo la radice, dove arrivano i file nuovi. Il limite tronca l'output: confronta `matched` con gli elementi mostrati e aumenta il limite se serve. Gli altri eventi restano in coda.

1. Leggi i file pertinenti e riconciliali con note e collegamenti. Lascia aperti conflitti e cambiamenti non esaminati.
2. Dopo le modifiche, esegui `python "{{strumento}}/controlla.py" scan --root Desktop` (o le radici coinvolte), poi rileggi `pending`: gli ID possono cambiare.
3. Chiudi soltanto gli eventi riconciliati, indicando cosa hai verificato. Esempio, con ID da sostituire:

   ```powershell
   python "{{strumento}}/controlla.py" review 12 13 --note 'Verificate le fonti; aggiornata la nota Finanze/BOLLETTE_CASA.md'
   ```

Quando la coda si allunga, chiudi per filtro gli eventi che non toccano note né fonti, per esempio foto o documenti aggiunti in cartelle senza note da aggiornare. `review` ricontrolla ogni file e, se uno è cambiato, non chiude nulla:

```powershell
python "{{strumento}}/controlla.py" review --root Desktop --prefix Personale/Foto --note 'Foto aggiunte; nessuna nota da aggiornare'
```

Per spostare file dopo il sì dell'utente, per esempio quelli nuovi della radice, scrivi un piano piccolo in `{{strumento}}/.stato/`, con un nome nuovo, ed eseguilo con `python "{{strumento}}/riordina.py" esegui`: non sovrascrive, annota le mosse e permette di annullarle. Lì piano e giornale restano fuori dalla coda.

Se la radice ha errori o il file è cambiato, correggi il problema, ripeti la scansione e riesamina. Un errore che non si risolve, come un file sempre bloccato, si esclude in `config.json`. Non svuotare il registro per aggirare un conflitto. Una scansione parziale va dichiarata; una interrotta non dimostra assenza di modifiche. Comandi e limiti nel [README dello strumento](<{{strumento}}/README.md>).

## Copertura del rilevatore

{{radici osservate, profondità ed esclusioni scelte, con il motivo}}

Quando cambi radici, profondità o esclusioni in `config.json`, aggiorna questa sezione: un cambio di copertura non produce false cancellazioni, ma va spiegato.

## Verifiche e registro

Esegui `python "{{strumento}}/controlla.py" links`. Correggi link e ancore rotti; controlla anche che le nuove note siano raggiungibili dalla guida pertinente. Il comando non verifica significato, URL remoti, riferimenti testuali o link dentro PDF/DOCX.

Le guide dei domini sono registrate nella [mappa generale](./MAPPA.md). Le guide annidate, con una riga sul loro ambito, si registrano qui:

- {{guida annidata, se ce ne sono}}

Le istruzioni dei repository restano nei repository.

Verificato: {{data}}
