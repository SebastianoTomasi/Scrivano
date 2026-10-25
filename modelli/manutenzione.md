# Manutenzione della conoscenza

Usa questa pagina quando scrivi o aggiorni note e pagine, e quando lavori sulla coda dei cambiamenti. Le autorizzazioni e le regole comuni sono in [AGENTS.md](./AGENTS.md).

## Scrivere e aggiornare una nota

Prima di scrivere, trova il dominio e leggi la nota canonica del tema, se c'è: un duplicato invecchia per conto suo. Confronta l'informazione nuova con quella registrata, per fonte, data dei fatti, certezza e decisioni coinvolte; poi aggiorna lo stato nella nota e conserva nel changelog locale solo le transizioni che spiegano una decisione. Collega la nota dalla guida del dominio e dagli altri temi quando la relazione aiuta a ritrovarla, e sistema i riferimenti ai percorsi che hai cambiato.

Una nota rende chiari **tema, stato noto, fonte e data, questioni aperte**, dove applicabili. Basta testo leggibile: niente campi vuoti o frontmatter obbligatorio, salvo standard locali. Per un lavoro in corso annota il punto di ripresa.

## Note, fonti e archivio

- **Nota canonica.** Prende il nome del tema in maiuscolo, con trattini bassi (`BOLLETTE_CASA.md`). Una forma che regge bene: sintesi in apertura, stato corrente con la data, decisioni prese, provvisorie e aperte, questioni da chiarire, collegamenti, fonti. Usa solo le sezioni che servono.
- **Fonti.** I materiali usati per una nota (ricerche, preventivi, estratti) stanno in `FONTI/` accanto alla nota, con nomi `TIPO_TEMA_AAAA-MM-GG` (`PREVENTIVO_CUCINA_2026-03-02.pdf`). Una fonte trascritta in Markdown apre con provenienza e data. Gli originali (contratti, referti, documenti d'identità) restano nelle loro cartelle e la nota li collega senza copiarli.
- **Archivio.** Ciò che è superato va in `Archivio/` dentro lo stesso dominio, con una riga in testa che lo dichiara storico. `links` non controlla le cartelle `Archivio`.

## Scrivere le pagine del sistema

| Pagina | Contiene | Quando aggiungerla |
| --- | --- | --- |
| `AGENTS.md` | Regole comuni, come lavorare e specificità dell'istanza | Solo nella radice del Desktop |
| `GUIDA.md` | Confine, rimandi ai domini vicini, regole locali, dove vanno i documenti nuovi, ingressi utili con una riga sul loro scopo, copertura | In ogni dominio; in una sottocartella quando ha regole proprie o è cresciuta tanto che la guida del genitore non basta più a orientarcisi |
| `MAPPA.md` | Link agli ingressi utili, una riga sul loro scopo, copertura | Nella radice; in un dominio solo se le domande attraversano molte sottocartelle e le guide, da sole, non bastano a orientare |
| Nota canonica | Fatti, decisioni, motivazioni e fonti del tema | Il tema è cercabile e aggiornabile da solo |
| `CHANGELOG.md` | Transizioni che spiegano lo stato corrente | La storia aiuta a capire una decisione |
| `README.md` | Uso, configurazione e limiti di uno strumento | Esiste uno strumento da usare o mantenere |

L'`AGENTS.md` della radice è l'unico: Claude Code e Codex lo leggono direttamente. Le guide sono file normali raggiunti dai link, perché Codex non carica gli `AGENTS.md` sotto la cartella di avvio e Claude Code li caricherebbe solo leggendo file lì dentro, mentre un link funziona per entrambi. Niente `CLAUDE.md`, `CLAUDE.local.md` o `.claude\CLAUDE.md` nel Desktop o più in alto: Claude Code leggerebbe quelli al posto di `AGENTS.md`. Con Codex, `.codex-root` nella radice (`project_root_markers` in `~/.codex/config.toml`) fa leggere l'`AGENTS.md` del Desktop anche a una sessione aperta in una sottocartella, tranne dentro un repository, che ha le sue istruzioni.

- Scrivi la regola una volta, nella sede competente; altrove rimanda. Usa verbi operativi e specifica quando un'azione serve.
- Mantieni selettivi gli ingressi di guide e mappe: collegamenti utili, non inventari completi né copie dello stato corrente.
- Le guide seguono le cartelle: una guida annidata ha la forma di quella di dominio, con in testa il rimando alla guida del genitore invece che alla mappa, e vale dentro la sua cartella. Il genitore la collega come ingresso e smette di elencarne l'interno. Registrala in «Verifiche e registro».
- Riusa ingressi esistenti, come un README o un indice già presenti. Non creare una serie di file vuoti per ogni cartella.
- Dichiarazione di copertura: **censito** = percorso individuato; **parzialmente esaminato** = specifica la parte letta; **interpretato** = sintesi collegata alle fonti. La scansione tecnica non promuove la copertura.
- `Verificato: AAAA-MM-GG` chiude guide e mappe dopo un controllo effettivo di percorsi e coerenza. Non aggiorna la data dei fatti nelle note.

## Revisionare i cambiamenti

La coda di `controlla.py` elenca ciò che è cambiato dall'ultima scansione: la traccia di quello che l'utente ha fatto a mano, più quello che hai scritto tu. Revisionarla vuol dire leggere i file cambiati, aggiornare note e link che li riguardano e chiudere gli eventi con una nota che dice cosa hai verificato. All'avvio segui [AGENTS.md](./AGENTS.md#come-lavorare). I comandi usano il percorso completo dello strumento, così funzionano da qualsiasi cartella senza cambiarla:

```
{{python}} "{{strumento}}/controlla.py" pending --root Desktop --prefix Finanze --limit 30
```

**Leggere la coda.** Parte dal cambiamento più recente. `--prefix` è il percorso relativo alla radice; `--depth 1` mostra solo la radice, dove arrivano i file nuovi. Il limite tronca l'output: confronta `matched` con gli elementi mostrati e aumenta il limite se serve; gli altri eventi restano in coda. `summary` guarda tutti gli eventi filtrati: le cartelle con più eventi dicono dove sta il grosso della coda, e ogni voce di `folder_renames` è una cartella rinominata o spostata.

**Riconciliare e chiudere.** Leggi i file pertinenti e riconciliali con note e collegamenti; lascia aperti conflitti e cambiamenti non esaminati. Dopo le modifiche esegui `{{python}} "{{strumento}}/controlla.py" scan --root Desktop` (o le radici coinvolte) e rileggi `pending`: anche le note che hai scritto generano eventi, e gli ID possono cambiare. Chiudi soltanto gli eventi riconciliati, indicando cosa hai verificato; gli ID sono un esempio:

```
{{python}} "{{strumento}}/controlla.py" review 12 13 --note 'Verificate le fonti; aggiornata la nota Finanze/BOLLETTE_CASA.md'
```

**Chiudere in blocco.** Quando la coda si allunga, chiudi per filtro gli eventi che non toccano note né fonti, per esempio foto o documenti aggiunti in cartelle senza note da aggiornare. `review` ricontrolla ogni file e, se uno è cambiato, non chiude nulla:

```
{{python}} "{{strumento}}/controlla.py" review --root Desktop --prefix Personale/Foto --note 'Foto aggiunte; nessuna nota da aggiornare'
```

Una rinomina di cartella si chiude allo stesso modo, con `review --prefix` sulla vecchia e sulla nuova cartella, dopo aver controllato che i file `changed` o `only_from` di `folder_renames` non tocchino note o fonti.

**Spostare file.** Dopo il sì dell'utente, per esempio per i file nuovi della radice, scrivi un piano piccolo in `{{strumento}}/.stato/`, con un nome nuovo, ed eseguilo con `{{python}} "{{strumento}}/riordina.py" esegui`: non sovrascrive, annota le mosse e permette di annullarle. Lì piano e giornale restano fuori dalla coda. Uno spostamento compare poi come una cancellazione più un'aggiunta: chiudile insieme, dopo aver aggiornato i link.

**Errori.** Se la radice ha errori o il file è cambiato, correggi il problema, ripeti la scansione e riesamina. Un errore che non si risolve, come un file sempre bloccato, si esclude in `config.json`; gli eventi di un percorso escluso si chiudono con una nota, senza ricontrollo. Non svuotare il registro per aggirare un conflitto. Una scansione parziale va dichiarata; una interrotta non dimostra assenza di modifiche. Comandi e limiti nel [README dello strumento](<{{strumento}}/README.md>).

## Copertura del rilevatore

{{radici osservate, profondità ed esclusioni scelte, con il motivo}}

Quando cambi radici, profondità o esclusioni in `config.json`, aggiorna questa sezione: un cambio di copertura non produce false cancellazioni, ma va spiegato.

## Verifiche e registro

Esegui `{{python}} "{{strumento}}/controlla.py" links`. Correggi link e ancore rotti; controlla anche che le nuove note siano raggiungibili dalla guida pertinente. Il comando non verifica significato, URL remoti, riferimenti testuali o link dentro PDF/DOCX.

Le guide dei domini sono registrate nella [mappa generale](./MAPPA.md). Le guide annidate, con una riga sul loro ambito, si registrano qui:

- {{guida annidata, se ce ne sono}}

Le istruzioni dei repository restano nei repository.

Verificato: {{data}}
