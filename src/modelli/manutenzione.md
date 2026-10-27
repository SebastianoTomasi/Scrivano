# Manutenzione della conoscenza

## Note, fonti e cartelle

Prima di scrivere, leggi la nota canonica del tema, se c'è: un duplicato invecchia per conto suo. Confronta l'informazione nuova con quella registrata per fonte, data dei fatti, certezza e decisioni coinvolte, poi aggiorna lo stato nella nota; nel `CHANGELOG.md` locale, se c'è, solo le transizioni che spiegano una decisione. Collega la nota dalla guida del dominio e dai temi vicini quando aiuta a ritrovarla, e sistema i riferimenti ai percorsi che hai cambiato. Per un lavoro in corso annota il punto di ripresa.

- **Nota canonica.** Nome del tema in maiuscolo, con trattini bassi (`BOLLETTE_CASA.md`). Testo leggibile, senza campi vuoti o frontmatter obbligatori: sintesi in apertura, stato corrente con la data, decisioni prese, provvisorie e aperte, questioni da chiarire, collegamenti, fonti; solo le sezioni che servono.
- **Fonti.** I materiali usati per una nota (ricerche, preventivi, estratti) stanno in `FONTI/` accanto alla nota, con nomi `TIPO_TEMA_AAAA-MM-GG` (`PREVENTIVO_CUCINA_2026-03-02.pdf`); una fonte trascritta in Markdown apre con provenienza e data. Gli originali (contratti, referti, documenti d'identità) restano nelle loro cartelle: la nota li collega senza copiarli.
- **Cartelle nuove.** In PascalCase ASCII, salvo convenzioni locali o dei repository; i nomi esistenti restano riconoscibili. Repository e progetti mantengono percorsi, nomi e istruzioni propri.

## Pagine del sistema

| Pagina | Contiene | Dove |
| --- | --- | --- |
| `AGENTS.md` | Regole comuni, come lavorare, specificità dell'istanza | Solo nella radice del Desktop |
| `MAPPA.md` | Una riga per dominio con le parole dell'utente, percorsi esterni, domande trasversali | Solo nella radice |
| `GUIDA.md` | Confine, regole locali, dove vanno i documenti nuovi, ingressi con una riga sul loro scopo, copertura | In ogni dominio; in una sottocartella con regole proprie o cresciuta tanto che la guida del genitore non basta più a orientarcisi |
| Nota canonica | Fatti, decisioni, motivazioni e fonti di un tema | Dove il tema si cerca e si aggiorna da solo |
| `CHANGELOG.md` | Transizioni che spiegano lo stato corrente | Dove la storia aiuta a capire una decisione |
| `README.md` | Uso, configurazione e limiti di uno strumento | Accanto a uno strumento da usare o mantenere |

- Scrivi la regola una volta, nella sede competente; altrove rimanda.
- Ingressi selettivi: collegamenti utili, non inventari né copie dello stato corrente. Riusa un README o un indice già presenti; niente file vuoti per ogni cartella.
- Una guida annidata ha la forma di quella di dominio, con in testa il rimando alla guida del genitore invece che alla mappa, e vale dentro la sua cartella; il genitore la collega come ingresso e smette di elencarne l'interno.
- Copertura: **censito** = percorso individuato; **parzialmente esaminato** = con la parte letta; **interpretato** = sintesi collegata alle fonti. La scansione tecnica non la promuove.
- `Verificato: AAAA-MM-GG` chiude guide e mappa dopo un controllo effettivo di percorsi e coerenza; non è la data dei fatti.

## Revisionare i cambiamenti

Quando e perché, in [AGENTS.md](./AGENTS.md#come-lavorare). I comandi usano il percorso completo dello strumento, così valgono da qualsiasi cartella:

```
{{python}} "{{strumento}}/src/controlla.py" pending --root Desktop --prefix Finanze --limit 30
```

**Leggere la coda.** Parte dal cambiamento più recente. `--prefix` è il percorso relativo alla radice; `--depth 1` mostra solo la radice, dove arrivano i file nuovi. Il limite tronca l'output: se `matched` supera gli elementi mostrati, alza il limite; gli altri eventi restano in coda. `summary` guarda tutti gli eventi filtrati: le cartelle con più eventi dicono dove sta il grosso della coda, e ogni voce di `folder_renames` è una cartella rinominata o spostata.

**Chiudere.** Leggi i file pertinenti e aggiorna note e collegamenti; lascia aperti conflitti e cambiamenti non esaminati. Poi `{{python}} "{{strumento}}/src/controlla.py" scan --root Desktop` (o le radici coinvolte) e rileggi `pending`: anche le note che hai scritto generano eventi, e gli ID possono cambiare. Chiudi con una nota che dice cosa hai verificato; gli ID sono un esempio:

```
{{python}} "{{strumento}}/src/controlla.py" review 12 13 --note 'Verificate le fonti; aggiornata la nota Finanze/BOLLETTE_CASA.md'
```

**Chiudere in blocco.** Per filtro, gli eventi che non toccano note né fonti, per esempio foto aggiunte in una cartella senza note. `review` ricontrolla ogni file e, se uno è cambiato, non chiude nulla:

```
{{python}} "{{strumento}}/src/controlla.py" review --root Desktop --prefix Personale/Foto --note 'Foto aggiunte; nessuna nota da aggiornare'
```

Una rinomina di cartella si chiude così, con `review --prefix` sulla vecchia e sulla nuova, dopo aver controllato che i file `changed` o `only_from` di `folder_renames` non tocchino note o fonti.

**Spostare.** Vale per ogni spostamento e ogni rinomina, anche di un solo file: una rinomina è una mossa con la stessa cartella e un nome nuovo, e una che cambia solo maiuscole passa da un nome intermedio, in due piani. Dopo il sì dell'utente, scrivi un piano piccolo in `{{strumento}}/src/.stato/`, con un nome nuovo, ed eseguilo con `{{python}} "{{strumento}}/src/riordina.py" esegui`: non sovrascrive, annota le mosse e permette di annullarle; lì piano e giornale restano fuori dalla coda. Lo spostamento compare poi come una cancellazione più un'aggiunta: aggiorna i link e chiudile insieme.

**Buttare.** Dopo il sì dell'utente, nel Cestino con questi comandi, così si recupera. Prima togli i link che portavano lì.

- Windows, da PowerShell: `Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile('C:\percorso\file', 'OnlyErrorDialogs', 'SendToRecycleBin')`, con `DeleteDirectory` per una cartella. Il Cestino di Windows può cancellare per sempre, senza avvisare, un elemento più grande del suo spazio o con un percorso troppo lungo: per un elemento grande chiedi prima all'utente, uno con un percorso lungo spostalo prima in un percorso corto con un piano.
- macOS: `osascript -e 'tell application "Finder" to delete POSIX file "/percorso/file"'`.

Poi controlla che sia arrivato. Windows: `(New-Object -ComObject Shell.Application).NameSpace(10).Items() | Where-Object { $_.ExtendedProperty('System.Recycle.DeletedFrom') -eq 'C:\cartella' } | ForEach-Object Name` elenca ciò che è arrivato dalla cartella che conteneva l'elemento, con il nome senza estensione se Esplora risorse le nasconde. macOS: `osascript -e 'tell application "Finder" to get name of every item of trash'`; se il Cestino aveva già un elemento con lo stesso nome, Finder aggiunge qualcosa al nome. Se non c'è, fermati e dillo all'utente.

Mai `Remove-Item`, `del`, `rmdir`, `rm`, `shutil.rmtree` o altri comandi che cancellano per sempre, salvo che l'utente chieda espressamente una cancellazione definitiva. La cancellazione compare in coda: chiudila con una nota.

**Errori.** Se la radice ha errori o il file è cambiato, correggi, ripeti la scansione e riesamina. Un errore che non si risolve, come un file sempre bloccato, si esclude in `config.json`; gli eventi di un percorso escluso si chiudono senza ricontrollo. Non svuotare il registro per aggirare un conflitto. Una scansione parziale va dichiarata; una interrotta non dimostra assenza di modifiche. Comandi e limiti nel [README dello strumento](<{{strumento}}/README.md>).

## Copertura del rilevatore

{{radici osservate, profondità ed esclusioni scelte, con il motivo}}

Quando cambi radici, profondità o esclusioni in `config.json`, aggiorna questa sezione: un cambio di copertura non produce false cancellazioni, ma va spiegato.

## Verifiche

`{{python}} "{{strumento}}/src/controlla.py" links` controlla link e ancore delle pagine Markdown a partire dalla radice: correggi quelli rotti e controlla che le note nuove siano raggiungibili dalla guida pertinente. Non verifica significato, URL remoti, riferimenti testuali o link dentro PDF e DOCX.

Verificato: {{data}}
