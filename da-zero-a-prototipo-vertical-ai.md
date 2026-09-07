# Da zero a prototipo: le fondamenta per costruire una Vertical AI

> Guida pratica per due founder tecnici alle prime armi. Esempio ricorrente: una vertical AI per commercialisti italiani, ma ogni concetto è scritto in forma generalizzabile a qualunque dominio professionale (legal, sanità, HR, logistica, edilizia...).

---

## Assunzioni dichiarate

Prima di tutto, le carte in tavola. Tutto ciò che segue assume che:

1. **Team**: due persone, ~35 ore/settimana complessive dedicate al progetto (non 35 a testa: il prompt dice "~35 ore/settimana dedicate a questo progetto (full-time per due persone)" — interpreto come impegno full-time complessivo, quindi ~17-18 ore a testa; se in realtà sono 35 a testa, la roadmap in sezione 5 si comprime di circa il 30-40%).
2. **Livello di partenza**: basi di programmazione (non necessariamente Python avanzato), dimestichezza con Linux e terminale, zero esperienza di prodotto, zero esperienza di AI applicata, zero conoscenza del dominio.
3. **Budget**: 20.000–30.000 € di capitale proprio, da non bruciare subito. Le stime di costo in sezione 6 puntano a spendere meno di 5.000 € nei primi 4 mesi, hardware escluso.
4. **Obiettivo**: un prototipo funzionante (proof of concept), non un MVP commerciale. Il criterio di successo è "gira davvero, un professionista del dominio lo prova e ci dice se è utile", non "è pronto per essere venduto".
5. **Infrastruttura**: cloud-first, managed-first. Niente server in casa, niente GPU locali, niente on-premise. Locale solo il codice e l'ambiente di sviluppo.
6. **Tempistica**: orizzonte 3–4 mesi per il prototipo, preceduti da un periodo di osservazione sul campo che può correre in parallelo all'apprendimento tecnico.
7. **Scenario temporale**: la guida è scritta a settembre 2026. Il mondo LLM si muove velocemente: nomi di modelli, prezzi e classifiche di riferimento **cambiano ogni 3–6 mesi**. Le architetture e i pattern (RAG, citazioni, eval, guardrail) invece sono stabili: concentrate l'apprendimento su quelli, e trattate i nomi specifici degli strumenti come "la migliore opzione che conosco oggi, da riverificare quando la adottate".

Se una di queste assunzioni non corrisponde alla realtà, le sezioni da riadattare sono soprattutto la 5 (roadmap) e la 6 (costi).

---

## 1. Che cos'è una vertical AI

### 1.1 Definizione

Una **vertical AI** è un assistente basato su modelli linguistici (LLM) specializzato su **un singolo dominio professionale**: non "un chatbot che sa tutto", ma uno strumento che risponde a domande di un mestiere specifico usando le fonti di quel mestiere, nel formato che quel mestiere si aspetta, dentro i workflow di quel mestiere.

La differenza con un modello generalista (ChatGPT, Claude, Gemini usati "nudi") non sta nel modello — spesso sotto il cofano c'è lo stesso identico modello — ma in tutto ciò che gli sta intorno:

| Aspetto | Modello generalista (ChatGPT nudo) | Vertical AI |
|---|---|---|
| Conoscenza | Quella del training (generica, datata, non verificabile) | Corpus documentale del dominio, aggiornato, indicizzato |
| Risposte | Plausibili, senza fonti | Con citazione puntuale delle fonti (documento, sezione, articolo) |
| Workflow | Chat libera | Operazioni tipiche del mestiere (analisi di un documento, redazione di una bozza, confronto tra versioni) |
| Formato output | Testo generico | I formati che il professionista usa davvero (parere, nota, checklist, bozza di atto) |
| Affidabilità | "Di solito giusto" | "Verificabile": ogni affermazione è tracciabile a una fonte |
| Dati del cliente | Inseriti in un servizio consumer | Gestiti con vincoli di riservatezza professionale (GDPR, segreto professionale) |

Esempio commercialisti: ChatGPT può spiegarti in generale come funziona la fatturazione elettronica. Una vertical AI per commercialisti risponde a "posso detrarre l'IVA su questa fattura di acquisto auto?" citando l'articolo preciso del TUIR o il documento di prassi dell'Agenzia delle Entrate, ragiona sul documento che il cliente ha caricato, e produce una bozza di nota per il cliente nel formato che lo studio usa. **Lo stesso modello LLM sotto, un prodotto completamente diverso sopra.**

### 1.2 Dove sta davvero il valore

Il modello LLM è una commodity: lo affittate via API, costa sempre meno, e i vostri concorrenti hanno accesso agli stessi modelli. Il valore di una vertical AI sta in tre cose che il modello non vi dà:

1. **Dati proprietari (o curati) del dominio.** Il corpus di documenti che indicizzate, come lo pulite, come lo tenete aggiornato, come lo organizzate. Nel caso dei commercialisti: normativa, prassi, giurisprudenza tributaria, guide operative — ma la stessa cosa vale ovunque: in sanità saranno linee guida e letteratura, in edilizia norme tecniche e capitolati, in HR contratti collettivi e giurisprudenza del lavoro. Chi ha il corpus migliore, meglio indicizzato, vince — non chi ha il modello più grande.
2. **Workflow di dominio.** Il professionista non vuole "chattare": vuole fare le 5–10 operazioni che ripete ogni settimana, più velocemente. Analizzare un documento ricevuto, preparare una risposta a un cliente, verificare una posizione, redigere una bozza. Il prodotto è l'incarnazione di quel workflow, e lo capite solo osservando il mestiere da vicino (sezione 5, fase di osservazione).
3. **Fiducia e affidabilità.** Un professionista mette la propria firma (e la propria responsabilità) su ciò che lo strumento produce. Il valore non è "risponde quasi sempre bene" ma "quando non sa, lo dice; quando risponde, posso verificare". La citazione delle fonti non è una feature estetica: è il meccanismo che rende il sistema **verificabile** e quindi usabile in un contesto professionale.

Conseguenza pratica per voi: il vostro vantaggio competitivo in fase di prototipo non sarà mai la bravura con il modello, ma la qualità del corpus, la fedeltà al workflow e la verificabilità delle risposte. Allocate tempo e budget di conseguenza.

### 1.3 Il pattern di riferimento (Lexroom / Harvey)

Prodotti come Lexroom (legal, Italia) e Harvey (legal, internazionale) hanno reso esplicito un pattern che si ripete identico in ogni verticale professionale. Tre capacità fondamentali:

1. **Ricerca in linguaggio naturale con fonti verificate.** Domanda in italiano corrente → risposta sintetica + citazioni puntuali cliccabili. È il sostituto AI della "ricerca in banca dati" che oggi il professionista fa con parole chiave su portali specializzati.
2. **Analisi documentale.** Carichi un documento (un contratto, un accertamento, una perizia, una cartella clinica) → il sistema lo legge, lo classifica, estrae gli elementi rilevanti, segnala criticità, lo confronta con il corpus.
3. **Redazione assistita.** Il sistema produce bozze (pareri, note, atti, email al cliente) partendo dal contesto e dalle fonti, che il professionista revisiona e firma. Mai "invio automatico": sempre umano-che-revisiona.

Perché questo pattern si ripete identico ovunque? Perché **ogni professionista della conoscenza fa fondamentalmente tre cose**: cerca informazioni in un corpus specialistico, legge e interpreta documenti, produce documenti. Cambia il corpus, cambia il lessico, cambia il formato delle bozze — non cambia la struttura del lavoro. Se imparate a costruire queste tre capacità per i commercialisti, sapete costruirle per qualunque verticale.

Una quarta capacità, trasversale e non negoziabile: la **protezione dei dati dei clienti del professionista** (sezione 2.7). Non è una feature, è la licenza per esistere.

---

## 2. Fondamenti tecnici

Questa sezione spiega i concetti da zero ma senza banalizzarli: per costruire il prototipo dovete capire *perché* le cose funzionano, non solo copiare tutorial.

### 2.1 LLM e prompt engineering

Un **LLM (Large Language Model)** è un modello che, data una sequenza di testo (il *prompt*), genera la continuazione più probabile. Tutto ciò che farete — risposte, analisi, bozze, classificazioni — è, sotto, una chiamata API a cui passate testo e da cui ricevete testo.

Cosa dovete padroneggiare davvero:

- **System prompt.** Le istruzioni permanenti del sistema: ruolo, vincoli, tono, formato, cosa fare e cosa non fare mai. In una vertical AI il system prompt è una parte del "prodotto": contiene le regole del dominio ("rispondi solo basandoti sulle fonti fornite", "se la norma citata è stata abrogata, segnalalo", "non dare mai consulenza definitiva, produci bozze da revisionare"). Itererete sul system prompt decine di volte: tenetelo in un file versionato, non sparso nel codice.
- **Contesto (context window).** Ogni modello ha una finestra massima di token (parole/sub-parole) che può vedere per singola chiamata — oggi tipicamente da 128k a 1M token. Il trucco del mestiere non è "buttarci dentro tutto" ma **metterci la cosa giusta**: il contesto pertinente selezionato dal retrieval (vedi 2.2) batte sempre un contesto enorme e rumoroso. Più contesto irrilevante = risposte peggiori, costi maggiori, latenza maggiore.
- **Few-shot prompting.** Invece di spiegare al modello il formato che volete, gli mostrate 2–5 esempi di input/output. Per output di dominio (es. il formato di una nota per il cliente) i few-shot battono quasi sempre le istruzioni verbali. Gli esempi migliori li ricaverete dall'osservazione sul campo: come i professionisti scrivono davvero.
- **Output strutturati.** Quando la risposta deve essere processata dal codice (classificazioni, estrazioni, routing), chiedete JSON validato. Le API principali offrono modalità "structured output" / "tool use" che garantiscono output conforme a uno schema JSON (in Python si definisce tipicamente con **Pydantic**). Regola d'oro: **mai parsare output libero con regex** quando potete vincolare lo schema lato API.
- **Temperatura e parametri.** Per compiti professionali usate temperatura bassa (0–0.3): volete risposte stabili e conservatrici, non creative.
- **Gestione delle chiamate.** Retry con backoff, timeout, fallback tra modelli, tracciamento di token e costi per chiamata. Sembra noioso: è ciò che distingue un demo script da un prototipo che regge una prova con utenti veri.

### 2.2 RAG in profondità

**RAG (Retrieval-Augmented Generation)** è il pattern centrale di ogni vertical AI: invece di chiedere al modello di rispondere "a memoria", prima **recuperate** dal vostro corpus i passaggi pertinenti alla domanda, poi li **iniettate nel prompt** come fonti, e chiedete al modello di rispondere basandosi su quelli, citandoli.

Il RAG risolve tre problemi insieme: il modello non conosce il vostro dominio aggiornato, il modello allucina meno se ha le fonti davanti, ogni affermazione diventa tracciabile a un documento. È il motivo per cui esistono Lexroom e Harvey.

#### Pipeline di indicizzazione (offline)

Accade una volta per documento, prima di qualunque domanda:

1. **Acquisizione**: scaricare/caricare i documenti (PDF, HTML, DOCX, XML...).
2. **Parsing**: estrarre testo pulito preservando la struttura (titoli, articoli, commi, tabelle). È la parte più sottovalutata: un PDF legale con note a piè di pagina e tabelle, parsato male, avvelena tutto il resto. Strumenti: `pypdf`/`pdfplumber` per casi semplici, parser specializzati (es. Docling, Unstructured, o API di parsing) per quelli duri.
3. **Chunking**: spezzare il documento in frammenti ("chunk") della dimensione giusta. Troppo grandi → il retrieval diventa impreciso e sprecate contesto; troppo piccoli → i frammenti perdono senso ("il comma 3 si applica..." — a cosa?). Strategie:
   - **Chunking strutturale**: spezzare sui confini naturali del dominio (articolo, comma, clausola, sezione). *Nei domini professionali è quasi sempre la scelta giusta*: un articolo di legge, una voce di prassi, una clausola contrattuale sono unità di senso complete e citabili.
   - **Chunking a dimensione fissa con overlap** (es. 500–1000 token, 10–15% di sovrapposizione): fallback quando non c'è struttura.
   - **Parent-child / small-to-big**: si cercano frammenti piccoli (precisi) ma si passa al modello il frammento genitore più ampio (contestuale). Ottimo compromesso, supportato nativamente da LlamaIndex.
   - Salvate per ogni chunk i **metadati**: documento sorgente, titolo, data, sezione/articolo, URL, tipo. Senza metadati non esistono citazioni né filtri.
4. **Embedding**: ogni chunk viene trasformato in un vettore numerico (es. 1024–3072 dimensioni) che ne cattura il significato semantico, tramite un modello di embedding via API (es. OpenAI `text-embedding-3-large`, Cohere, Voyage) o open-source (es. BGE-M3, E5, modelli multilingui — importante per l'italiano: verificate sempre le performance sulla lingua del dominio).
5. **Indicizzazione**: vettori + testo + metadati vanno in un **vector database** (sezione 4), che permette di trovare in millisecondi i chunk semanticamente più vicini a un vettore di query.

#### Pipeline di retrieval + generazione (online)

Accade a ogni domanda dell'utente:

1. **Query understanding** (opzionale ma potente): il modello riscrive/arricchisce la domanda (espansione con sinonimi del dominio, scomposizione in sotto-domande, traduzione in "linguaggio della fonte" — i professionisti parlano diverso dai documenti ufficiali; es. un commercialista dice "spese di rappresentanza", la norma usa un lessico diverso).
2. **Retrieval**: si recuperano i top-k chunk più simili (k tipico: 20–50 grezzi). Tecniche:
   - **Ricerca vettoriale (semantica)**: trova ciò che "significa lo stesso" anche con parole diverse.
   - **Ricerca lessicale (BM25 / full-text)**: trova le parole esatte — indispensabile nei domini professionali, dove numeri di articolo, codici, riferimenti precisi ("art. 19-bis1, comma 1, lett. c") devono matchare letteralmente. Il vettoriale da solo fallisce sui riferimenti esatti.
   - **Ricerca ibrida**: vettoriale + BM25 fuse (es. con Reciprocal Rank Fusion). **Nei domini professionali l'ibrido è lo standard, non un optional.**
   - **Filtri su metadati**: "solo normativa vigente", "solo giurisprudenza di Cassazione", "solo documenti successivi al 2024".
3. **Re-ranking**: un modello specializzato (es. Cohere Rerank, Voyage Rerank, o un cross-encoder open-source come bge-reranker) riordina i chunk recuperati valutando la pertinenza query-chunk in modo più accurato della sola similarità vettoriale. Si tengono i top 3–10. Costo basso, miglioramento tipicamente marcato: è una delle modifiche con miglior rapporto beneficio/sforzo.
4. **Generazione con citazioni**: il prompt al modello contiene: system prompt (regole del dominio) + domanda utente + i chunk selezionati con i loro identificativi. Istruzione chiave: *rispondi solo sulla base delle fonti fornite, cita ogni affermazione con l'identificativo della fonte; se le fonti non bastano, dillo*. L'output viene poi post-processato per rendere le citazioni cliccabili/verificabili.
5. **Post-verifica** (opzionale, consigliata appena il prototipo gira): controlli automatici — le fonti citate esistono davvero tra quelle recuperate? la risposta contiene affermazioni non coperte da fonti? Anche un controllo banale ("la citazione `[Fonte 3]` punta a un chunk effettivamente recuperato") elimina una classe intera di errori.

#### Gestione dei documenti lunghi

Un contratto di 80 pagine o una sentenza lunga non entrano comodamente in un chunk. Strategie standard:

- **Gerarchica**: indicizzare per sezioni; recuperare le sezioni pertinenti; passare al modello le sezioni + un sommario del documento per il contesto globale.
- **Map-reduce / refine**: per task come "riassumi tutto il documento": si processano le sezioni una alla volta e si combinano i risultati parziali.
- **Indice per documento**: due livelli — prima si trova *quale documento*, poi *quale parte del documento*. Scala bene quando il corpus cresce.
- Nota del 2026: con finestre di contesto enormi è tentante "buttare dentro tutto il documento". Funziona per l'analisi one-shot di un singolo documento, ma non scala come strategia di ricerca su un corpus (costo, latenza, e qualità che degrada con contesti enormi e rumorosi — fenomeno noto come "lost in the middle"). Il retrieval resta la strada.

### 2.3 Fine-tuning: quando serve e quando no

Il **fine-tuning** è l'addestramento ulteriore di un modello su vostri dati, per modificarne comportamento o stile.

La regola pratica, valida nel 2026 come negli anni precedenti: **all'inizio è quasi sempre uno spreco**. Motivi:

- Il vostro problema non è che il modello "non sa il dominio" — quello lo risolve il RAG, che è aggiornabile, citabile e correggibile. Il fine-tuning "inietta" conoscenza in modo opaco: non potete citarla, aggiornarla facilmente, né verificare da dove viene una risposta.
- Serve un dataset di qualità (centinaia–migliaia di esempi curati) che non avete e che costruireste solo dopo mesi di osservazione.
- Costa tempo e soldi, e vi lega a una versione del modello mentre i modelli base migliorano ogni pochi mesi.

Quando invece ha senso (più avanti): **stile e formato** molto specifici (il modello deve scrivere bozze esattamente "alla maniera dello studio", e i few-shot non bastano più), **classificazioni ad alto volume** dove un modello piccolo fine-tunato costa meno di uno grande in prompt, **latenza/costo** quando il prompt con esempi diventa enorme. Sono tutti problemi da fase post-validazione. Per il prototipo: RAG + prompt engineering, e tenete il fine-tuning come voce nel backlog.

### 2.4 Agenti e tool calling

Il **tool calling** (function calling) è la capacità del modello di decidere di invocare una funzione del vostro codice — ricerca nel corpus, calcolo, lettura di un documento caricato, consultazione del calendario normativo — riceverne il risultato e continuare il ragionamento. Un **agente** è un loop in cui il modello pianifica più passi, chiama tool, osserva i risultati, decide il passo successivo.

In una vertical AI i tool tipici sono: `cerca_nel_corpus(query, filtri)`, `leggi_documento(id)`, `calcola(...)` (es. scadenze, importi, interessi — **mai far fare aritmetica all'LLM a mente**: date sempre un tool di calcolo), `recupera_versione_vigente(articolo, data)`.

Quando servono nel prototipo: quando il task ha **più passi con decisioni intermedie** ("confronta questi due documenti e cerca la norma rilevante per ogni divergenza"). Quando **non** servono: per la Q&A con citazioni (una singola pipeline RAG lineare basta), per la redazione di bozze (un prompt ben fatto basta). Errore tipico dei principianti: costruire un'architettura agentica complessa quando una pipeline lineare deterministico-LLM farebbe lo stesso lavoro in modo più prevedibile, debuggabile ed economico. **Regola: aggiungete autonomia al modello solo quando una pipeline fissa si dimostra insufficiente su casi reali.**

### 2.5 Valutazione (eval): la parte più sottovalutata

Senza valutazione state "andando a sensazione": cambiate un prompt, vi sembra meglio, e in realtà avete migliorato 3 casi e peggiorato 20. La valutazione è ciò che trasforma il tuning del RAG da astrologia a ingegneria.

Fondamenta minime:

1. **Eval set**: una raccolta di **coppie domanda–risposta attesa** rappresentative dell'uso reale. Per il prototipo bastano **30–80 casi**, ma devono essere *veri*: li ricaverete dall'osservazione sul campo ("quali domande fate ogni settimana? quali vi fanno perdere tempo?"). Per ogni caso annotate: la domanda, la risposta ideale (o i punti che deve contenere), le fonti che *dovrebbero* essere recuperate.
2. **Cosa misurare** (metriche semplici, fatte a mano all'inizio):
   - *Retrieval*: la fonte corretta è nei top-k recuperati? (recall@k — basta un sì/no per caso)
   - *Correttezza*: la risposta è corretta secondo la risposta attesa? (scala sì/parziale/no)
   - *Fedeltà/grounding*: ogni affermazione è supportata dalle fonti citate, o il modello ha aggiunto cose sue? (**allucinazione**)
   - *Citazioni*: le fonti citate sono quelle giuste e puntano al passaggio rilevante?
   - *Onestà*: nei casi-trappola (domande a cui il corpus non sa rispondere), il sistema ammette di non saperlo invece di inventare? **In un dominio professionale questa è la metrica più importante di tutte.**
3. **LLM-as-judge**: per valutare decine di casi a ogni modifica, si usa un LLM (possibilmente diverso da quello del sistema) come giudice automatico con una griglia di valutazione precisa, confrontando risposta prodotta vs attesa. Non è perfetto, ma scala; campionate comunque a mano il 10–20% per verificare che il giudice non dica sciocchezze. Framework come **Ragas** offrono metriche RAG pronte (faithfulness, answer relevance, context precision/recall); strumenti come **Langfuse** o **LangSmith** permettono di registrare le run e valutarle.
4. **Regime di lavoro**: ogni modifica a prompt/chunking/modulo di retrieval → rieseguite l'eval set → confrontate. Tenete uno spreadsheet dei punteggi nel tempo. È noioso ed è esattamente ciò che vi permetterà di dire a un mentor "l'accuratezza è passata dal 55% all'85% in sei settimane" invece di "secondo me va meglio".

Errori da non fare: valutare solo su domande inventate da voi (troppo facili, non rappresentative); valutare solo l'ultimo passo (se il retrieval non trova la fonte, la generazione non può salvarvi: misurate i due stadi separatamente); inseguire il 100% (un professionista non si fida di un sistema perfetto, si fida di uno prevedibile e onesto sui propri limiti).

### 2.6 Guardrail e affidabilità: gestire il "non lo so"

In un contesto professionale, la risposta sbagliata con sicurezza è molto peggio del "non lo so". I guardrail sono i meccanismi che rendono il comportamento del sistema prevedibile:

- **Grounding vincolato**: system prompt che impone di rispondere solo dalle fonti fornite; più la post-verifica delle citazioni (sezione 2.2).
- **Soglie di pertinenza**: se il retrieval restituisce chunk con punteggio basso (o il re-ranker dice "poco pertinenti"), il sistema risponde "non ho fonti sufficienti per rispondere con affidabilità" invece di improvvisare. Una soglia tarata sull'eval set batte qualsiasi prompt creativo.
- **Casi-trappola nell'eval set**: domande fuori corpus, domande su norme abrogate, domande ambigue. Il sistema deve rifiutare o chiedere chiarimenti.
- **Vincoli di dominio**: es. "non dare mai un parere conclusivo; produci analisi e bozze che un professionista deve revisionare" — va nel system prompt *e* nell'interfaccia (disclaimer nel posto giusto, non seppellito).
- **Dati temporali**: nei domini regolamentati la domanda "è vigente?" è centrale. I metadati devono portare date di pubblicazione/efficacia, e il prompt deve istruire il modello a ragionare sulla data della domanda. Nel caso fiscale italiano: la stessa norma cambia con ogni legge di bilancio — un sistema che cita la versione sbagliata è peggio di uno che non cita affatto.
- **Human-in-the-loop by design**: l'interfaccia deve rendere ovvio che l'output è una bozza da verificare, con le fonti a un click di distanza. Questo non è solo UX: è il vostro scudo di responsabilità.

### 2.7 Privacy e GDPR: dati dei clienti di professionisti

Qui il dominio cambia poco: che siano avvocati, commercialisti, medici o consulenti HR, il pattern è lo stesso — **il vostro utente (il professionista) tratta dati personali dei propri clienti, spesso sensibili, sotto obblighi di riservatezza e segreto professionale**. Voi diventate, nel gergo GDPR, *responsabili del trattamento* per conto del professionista (titolare). Conseguenze pratiche per il prototipo:

1. **Minimizzazione**: nel prototipo, evitate del tutto dati reali di clienti se potete. Per le prove usate documenti pubblici o anonimizzati. La fase di validazione con i professionisti si può fare su casi fittizi costruiti insieme a loro.
2. **Scelta dei fornitori LLM**: verificate le condizioni d'uso delle API — zero retention / non uso dei dati per il training (offerta standard dei piani API a pagamento dei principali provider; le chat consumer sono un'altra cosa, non usatele con dati di clienti). Per i clienti più sensibili esistono opzioni con elaborazione nell'UE (es. endpoint europei dei grandi provider, o provider europei come Mistral) — segnerà la differenza in fase commerciale, ma sappiate già da ora che "dove vanno i dati" sarà la prima domanda che vi faranno.
3. **Architettura dei dati**: separate i dati per studio (multi-tenancy logica), cifrate in transito e a riposo (default dei servizi managed seri), definite retention e cancellazione. Per il prototipo basta non fare pasticci; per la fase successiva servirà un DPA (Data Processing Agreement) con ogni provider.
4. **Cosa NON fare**: caricare documenti di clienti reali su ChatGPT/Claude consumer "per provare"; loggare contenuti sensibili in chiaro nei tool di monitoring senza mascherarli; mandare a un mentor una demo piena di dati veri.
5. **Messa in prospettiva**: non serve un consulente GDPR per il prototipo (sarebbe prematuro), ma serve la disciplina di non toccare dati reali finché non avete le basi contrattuali e tecniche. Quando arriverà il momento di pilotare con dati veri, una consulenza puntuale di un legale privacy (qualche ora, poche centinaia di euro) è tra i soldi meglio spesi del budget.

---

## 3. Architettura di riferimento del prototipo

L'architettura di una vertical AI si divide in due metà con ritmi completamente diversi:

- **Offline (pipeline di indicizzazione)**: gira quando aggiungete/aggiornate documenti. Può essere lenta, batch, imperfetta nei tempi. Nessun utente la aspetta.
- **Online (pipeline di risposta)**: gira a ogni domanda dell'utente. Deve rispondere in pochi secondi, essere robusta, loggare tutto.

### 3.1 Schema a blocchi

```
============================  OFFLINE  ============================

[Fonti del dominio]        (norme, prassi, giurisprudenza, guide,
       │                    manuali, CCNL, linee guida... a seconda
       │                    della verticale)
       ▼
(1) INGESTIONE             download/upload, scheduling aggiornamenti,
       │                    deduplica, tracking versioni
       ▼
(2) PARSING & PULIZIA      PDF/HTML/DOCX → testo strutturato;
       │                    rimozione boilerplate; preservazione di
       │                    titoli/articoli/tabelle
       ▼
(3) CHUNKING               spezzatura su unità di senso del dominio
       │                    + metadati (fonte, data, articolo, URL)
       ▼
(4) EMBEDDING              testo → vettori (API embedding)
       │
       ▼
(5) VECTOR DB / INDICE     vettori + testo + metadati
           │               (indice vettoriale + indice BM25)
═══════════╪═══════════════════════════════════════════════════════
           │                ONLINE
           ▼
(6) QUERY UNDERSTANDING    riscrittura/espansione della domanda (LLM)
       ▼
(7) RETRIEVAL IBRIDO       vettoriale + BM25 + filtri metadati → top-k
       ▼
(8) RE-RANKING             cross-encoder/API rerank → top 3–10 chunk
       ▼
(9) GENERAZIONE            LLM con system prompt + fonti → risposta
       │                    con citazioni [ID fonte]
       ▼
(10) POST-VERIFICA         citazioni valide? soglie di pertinenza?
       │                    "non lo so" se serve
       ▼
(11) INTERFACCIA           chat + document upload + fonti cliccabili
       │                    + stato "bozza da revisionare"
       ▼
(12) LOGGING & EVAL        traccia di ogni run (Langfuse/simili),
                           feedback utente, eval set periodico
```

### 3.2 Componenti sostituibili, blocco per blocco

| Blocco | Sostituibile con | Note |
|---|---|---|
| (1) Ingestione | script Python + cron → queue (Celery, Temporal) → servizio managed di ingestion | Al prototipo basta uno script rilanciabile a mano |
| (2) Parsing | `pypdf`/`pdfplumber` → Docling/Unstructured → API di parsing commerciali (es. LlamaParse, Azure Document Intelligence) | Il blocco con più varianza di qualità; budgettate tempo qui |
| (3) Chunking | regole custom → splitter di LlamaIndex/LangChain | Il chunking strutturale custom sul vostro dominio è spesso *meglio* dei splitter generici |
| (4) Embedding | API (OpenAI, Voyage, Cohere) ↔ modelli open multilingui (BGE-M3, E5) self-hosted | Sostituire il modello di embedding richiede re-indicizzare tutto: scegliete bene al primo giro |
| (5) Vector DB | pgvector/Postgres ↔ Qdrant ↔ Pinecone/Weaviate Cloud | Tutti espongono primitive simili; la migrazione è fattibile ma seccante |
| (6) Query understanding | niente → singola chiamata LLM → pipeline più elaborata | Aggiungetelo quando l'eval mostra che il retrieval fallisce su domande reali |
| (7) Retrieval | solo vettoriale → ibrido vettoriale+BM25 | Passare all'ibrido è il singolo upgrade tipico più impattante nei domini professionali |
| (8) Re-ranking | niente → Cohere/Voyage Rerank API → cross-encoder open | Attivatelo presto: costo irrisorio, beneficio tipicamente evidente |
| (9) Generazione | qualunque LLM via API (OpenAI, Anthropic, Google, Mistral) | Il blocco **più** sostituibile di tutti: astraiamo la chiamata dietro un'interfaccia vostra fin dal primo giorno |
| (10) Post-verifica | controlli regolari custom → framework di guardrail | Partite custom: 30 righe di Python |
| (11) Interfaccia | Streamlit/Gradio → Next.js + FastAPI | Per il prototipo Streamlit basta e avanza |
| (12) Logging/Eval | file JSONL → Langfuse (cloud o self-host) / LangSmith | Non opzionale: è il vostro strumento di debug e di valutazione |

### 3.3 Perché la distinzione offline/online conta

1. **Costi**: l'offline paga embedding e parsing (una tantum per documento); l'online paga LLM e rerank (per ogni domanda). Quando stimate i costi, li tenete separati (sezione 6).
2. **Affidabilità**: potete rifare l'indicizzazione quante volte volete senza toccare ciò che l'utente vede — finché mantenete separati indice vecchio e nuovo e fate lo switch a indicizzazione completata.
3. **Iterazione**: il 90% del miglioramento di qualità nei primi mesi viene da parsing, chunking, retrieval e prompt — cioè da blocchi che potete cambiare indipendentemente l'uno dall'altro. Un'architettura a blocchi con interfacce chiare è ciò che vi permette di iterare in giorni invece che in settimane.

---

## 4. Stack consigliato (cloud-first)

Criteri usati per le raccomandazioni: due studenti senza esperienza pregressa; budget 20–30k ma mentalità frugale; preferenza managed; obiettivo prototipo in 3–4 mesi; ecosistema Python (la scelta ovvia per AI applicata nel 2026).

> Nota 2026: questa sezione invecchia più in fretta di tutte le altre. I pattern restano, i nomi e i prezzi vanno riverificati al momento dell'adozione.

### 4.1 Modello LLM

| Opzione | Pro | Contro |
|---|---|---|
| **OpenAI API** (famiglia GPT-5) | Qualità top, structured output maturo, ecosistema enorme, embeddings nello stesso vendor | Dati fuori UE (valutare endpoint UE dove disponibili); lock-in morbido |
| **Anthropic API** (famiglia Claude) | Eccellente su ragionamento lungo, analisi documentale e scrittura — storicamente forte proprio sui task da vertical AI professionale | Pricing simile ai pari livello; stesso discorso residenza dati |
| **Google Gemini API** | Finestre di contesto enormi, prezzi aggressivi, buono per analisi di documenti lunghi | Tooling e structured output storicamente un passo indietro (gap che si riduce) |
| **Mistral API** (UE) | Provider europeo: forte argomento GDPR; ottimo rapporto qualità/prezzo | Nei task di frontiera la qualità può essere un gradino sotto i top US |
| **Self-host di modelli open** (Llama, Qwen, Mistral open) su GPU cloud (RunPod, Together, Fireworks, vLLM) | Controllo totale, costi prevedibili ad alto volume, dati che non escono dal vostro perimetro | DevOps GPU, manutenzione, qualità inferiore ai frontier per ragionamento complesso: **sconsigliato per il vostro profilo ora** |

**Raccomandazione**: partite con **due provider API commerciali** (es. Anthropic o OpenAI come primario, l'altro o Gemini/Mistral come fallback e giudice delle eval), dietro un vostro layer di astrazione. Non fate self-hosting di LLM nel primo anno: è l'errore di spesa n. 1 dei principianti (sezione 8). L'opzione europea (Mistral o endpoint UE dei big) tenetela pronta come argomento per i pilot con studi veri.

### 4.2 Framework di orchestrazione

Nel 2026 la risposta "usa LangChain e basta" non è più automatica. Il panorama maturo:

| Opzione | Pro | Contro |
|---|---|---|
| **LlamaIndex** | Focalizzato su RAG: ingestion, chunking, indici, retriever, re-rank integrati; documentazione orientata ai casi d'uso | Meno flessibile fuori dal perimetro RAG; astrazioni a volte profonde da debuggare |
| **LangChain + LangGraph** | Ecosistema più vasto, LangGraph ottimo per workflow agentici a stati, LangSmith integrato | Curva di apprendimento, superficie API ampia e storicamente mutevole; rischio over-engineering |
| **SDK ufficiali + codice vostro** (OpenAI/Anthropic SDK, Pydantic, httpx) | Massima comprensione e controllo, zero magia, debug facile; nel 2026 le API native coprono già structured output e tool calling | Reinventate alcune utility (splitter, retriever) |
| **SDK agentici leggeri** (OpenAI Agents SDK, Pydantic AI) | Tool calling e agenti con poco codice, typed, moderni | Giovani rispetto ai due storici |

**Raccomandazione**: per il vostro caso — pipeline RAG lineare + poche tool-call — la combinazione più sana è **SDK ufficiali + LlamaIndex solo per le parti RAG (parsing/chunking/indici)**, oppure **LlamaIndex da solo** se volete un'unica dipendenza. Evitate di partire da LangGraph "perché è quello che usano tutti": ne riparlerete quando avrete un workflow genuinamente multi-step validato dagli utenti. Il criterio decisivo per due principianti: *meno astrazioni = bug che capite*.

### 4.3 Vector database

| Opzione | Pro | Contro |
|---|---|---|
| **pgvector su Postgres managed** (Supabase, Neon, RDS) | Un solo database per dati app + vettori; SQL che già conoscete; gratis/barato a scala prototipo; BM25/full-text nello stesso DB | Performance e feature (HNSW tuning, hybrid nativo) sotto i vector DB dedicati a grandi scale |
| **Qdrant Cloud** (managed) | Dedicato, API pulita, filtri su metadati eccellenti, hybrid search, free tier generoso; self-hostabile se un giorno serve | Un servizio in più da gestire/pagare |
| **Pinecone** | Il managed "senza pensieri" per eccellenza, serverless, maturo | Prezzi che crescono con la scala; meno trasparente su cosa succede dentro |
| **Weaviate Cloud** | Hybrid search integrato ben fatto, moduli per rerank | Simile a Qdrant come trade-off |

**Raccomandazione**: **pgvector su Postgres managed (Supabase o Neon)** per il prototipo. Motivo: a scala prototipo (decine di migliaia di chunk) è ampiamente sufficiente, vi dà nello stesso posto utenti, documenti, chunk, vettori e full-text search (quindi l'ibrido vettoriale+BM25 esce quasi gratis), e rimanda di mesi la gestione di un secondo datastore. Migrate a Qdrant/Pinecone solo quando l'eval o le performance vi dicono che serve — se servirà.

### 4.4 Backend e frontend/demo UI

| Componente | Opzioni | Raccomandazione |
|---|---|---|
| Backend API | **FastAPI** (Python) · Django · Node/NestJS | **FastAPI**: standard de facto dell'AI applicata in Python, async, OpenAPI automatico, si sposa con gli SDK LLM |
| Demo UI | **Streamlit** · Gradio · Next.js + Vercel | **Streamlit** per le settimane 1–8: chat + upload + citazioni in un pomeriggio, zero JavaScript. Passate a Next.js solo quando il prototipo deve *sembrare* un prodotto per i pilot — e non prima |
| Auth | Supabase Auth · Clerk · Auth0 | Se siete su Supabase: Supabase Auth, gratis a questa scala |
| Upload/storage documenti | S3 / Cloudflare R2 / Supabase Storage | Quello integrato col vostro DB (Supabase Storage) per non aggiungere servizi |

### 4.5 Hosting

| Opzione | Pro | Contro |
|---|---|---|
| **Railway / Render** | Deploy da Git in minuti, container managed, Postgres incluso, prezzi onesti a bassa scala | Costi che crescono se scalate; meno "enterprise" |
| **Fly.io** | Container ovunque, buon controllo | Un filo più DevOps |
| **Vercel (frontend) + Railway (backend)** | Combo comodissima quando passate a Next.js | Due piattaforme |
| **AWS/GCP/Azure "full"** (ECS, Cloud Run, managed k8s) | Scala infinita, tutto integrato | Complessità enorme per due principianti: trappola classica |

**Raccomandazione**: **Railway o Render** per backend + worker di indicizzazione; **Supabase/Neon** per DB; **Vercel** solo se/quando Next.js. Eccezione sensata: se uno dei due studia già un cloud provider all'università, usare **Cloud Run (GCP)** o equivalente è una valida alternativa — il criterio è "zero amministrazione di server". Niente Kubernetes: non vi serve, punto.

### 4.6 Monitoring, logging e osservabilità LLM

| Voce | Opzioni | Raccomandazione |
|---|---|---|
| Tracing LLM (prompt, risposte, token, costi, latenza per run) | **Langfuse** (open, cloud UE disponibile, self-hostabile) · LangSmith · Helicone | **Langfuse Cloud**: è lo strumento che userete ogni giorno per debuggare il RAG e raccogliere i casi per l'eval set. Self-host solo se un giorno la privacy dei log lo impone |
| Error tracking applicativo | Sentry | Sentry, free tier |
| Uptime/metriche base | quelle della piattaforma di hosting + Better Stack/UptimeRobot | Free tier bastano |

### 4.7 Il quadro d'insieme (stack raccomandato)

```
Supabase (Postgres + pgvector + Auth + Storage)
Railway  → FastAPI (API + pipeline online) + worker indicizzazione
Streamlit (demo UI, hostato su Railway/Streamlit Cloud)
LLM: Anthropic o OpenAI (primario) + secondo provider (fallback/judge)
Embeddings: API del primario (o Voyage) — multilingua, verificate l'italiano
Rerank: Cohere Rerank API (o Voyage)
Langfuse Cloud (tracing + eval) · Sentry (errori)
GitHub (repo + CI) · dominio .it/.com
```

Tutto managed, tutto con free tier o costi iniziali irrisori, tutto sostituibile. Quando ha senso considerare self-hosted — **solo in questi casi**: (a) un cliente pilota impone per contratto che i dati non escano da un perimetro controllato; (b) i volumi rendono le API LLM la voce di costo dominante e un modello open fine-tunato basterebbe; (c) requisiti di residenza dati non coperti dalle opzioni UE dei provider. Nessuna delle tre si applica al vostro prototipo.

---

## 5. Roadmap step-by-step: da zero al prototipo

Orizzonte: **16 settimane** (~4 mesi) con ~35 ore/settimana complessive. La roadmap assume apprendimento e costruzione in parallelo: non "prima studiamo 2 mesi poi costruiamo" — si impara il venerdì ciò che serve il lunedì. Ogni fase ha obiettivo, attività, deliverable verificabile e rischi tipici.

Nota sul parallelismo: siete in due. La divisione naturale per gran parte del percorso è **Persona A: pipeline dati (parsing, chunking, indicizzazione) — Persona B: pipeline online (retrieval, prompt, API, UI)**, con eval e osservazione sul campo fatte insieme. Ruotate a metà percorso: entrambi dovete capire tutto.

### Fase 0 — Dati di dominio da fonti pubbliche (settimane 1–2, e poi continuativa)

In qualunque verticale professionale esiste un corpus pubblico: è il punto di partenza, prima ancora di avere documenti privati dei clienti.

- **Dove si trovano tipicamente**: portali istituzionali e gazzette ufficiali (norme), banche dati pubbliche di giurisprudenza e prassi, siti di ordini professionali ed enti di regolazione (guide, circolari, FAQ), manuali e pubblicazioni open, newsletter di settore. Esempio commercialisti: Gazzetta Ufficiale e Normattiva per le norme, Agenzia delle Entrate per prassi e guide (risoluzioni, circolari, guide in PDF), giurisprudenza tributaria da portali pubblici, MEF, documentazione INPS. L'equivalente esiste in ogni verticale: in edilizia le NTC e le norme UNI (attenzione: le UNI sono a pagamento — vedi licenze), in HR i CCNL pubblici, in sanità le linee guida ISS/SNLG.
- **Problemi di formato**: PDF scannerizzati (serve OCR: Tesseract gratis, o API di parsing), HTML con boilerplate, tabelle rotte, documenti in più versioni nel tempo. Il 60% del lavoro della fase 0 è qui.
- **Pulizia**: rimozione di header/footer ripetuti, ricostruzione della struttura (articolo/comma), normalizzazione encoding, deduplica, estrazione metadati (data, numero, fonte, stato di vigenza).
- **Licenze**: le norme e gli atti ufficiali sono tipicamente liberi da copyright, ma banche dati, riviste e commenti specializzati **no**. Regola: per il prototipo usate solo fonti il cui riutilizzo è lecito, tenete un registro fonte-per-fonte (URL, data download, licenza), e prima di qualsiasi uso commerciale fate verificare il registro a un legale. Non scrape-ate banche dati a pagamento: è sia un problema legale sia la cosa più facile da farsi scoprire.
- **Deliverable verificabile**: un repository di almeno **500–2.000 documenti** puliti, con metadati, un `SOURCES.md` con licenze, e uno script rilanciabile che riproduce il corpus da zero.
- **Rischi tipici**: perfezionismo sul parsing (fissate un criterio "abbastanza pulito per il retrieval", non "perfetto"); corpus troppo ampio (meglio un sotto-dominio coperto bene — es. per i commercialisti: fiscalità d'impresa base, non "tutto il diritto tributario").

### Fase 1 — Fondamenta tecniche + osservazione sul campo, avvio (settimane 1–4)

Due binari paralleli.

**Binario tecnico:**
- Setup: Git/GitHub, Python (uv/poetry), ambiente condiviso, account cloud (Supabase, Railway, provider LLM), Langfuse.
- Python solido + API: completare le risorse della sezione 7 *mentre* si scrive codice vero.
- Primo "hello RAG": script che indicizza 50 documenti del corpus e risponde a 10 domande con citazioni, in notebook o script. Brutto ma vero.
- Deliverable: repo con pipeline RAG minimale end-to-end sul sotto-corpus; risposte con citazioni su 10 domande di prova.

**Binario dominio (osservazione sul campo, avvio):**
- Reclutare **3–5 commercialisti** disponibili a farsi osservare: partite dalla rete personale (famiglia, amici, professori, l'ordine locale, associazioni di categoria territoriali). Offrite in cambio accesso anticipato gratuito al prototipo.
- Come affiancarli: mezze giornate in studio, seduti accanto, **in silenzio**, osservando il lavoro vero (non interviste astratte). Domande-guida: "cosa stai facendo? da dove arriva questa informazione? quanto tempo ti prende? cosa faresti se avessi un assistente brillante che non conosce il mestiere?".
- Cosa osservare e registrare: le **domande ricorrenti** dei clienti e dei colleghi; dove cercano le risposte oggi (quali portali, quanti click, quanto tempo); i documenti che leggono e producono (raccoglietene i *formati*, non i contenuti sensibili); i punti in cui sbagliano o controllano due volte; il lessico esatto che usano.
- Come tradurre in requisiti tecnici: ogni osservazione diventa una riga in un documento `WORKFLOW.md`: *"Quando arriva X, il professionista fa A, B, C; ci mette N minuti; la parte B è cercare la norma giusta → candidato RAG; la parte C è una bozza standard → candidata redazione assistita"*. Da qui usciranno: il perimetro del prototipo (2–3 workflow, non dieci), le domande vere per l'eval set, i formati di output per i few-shot.
- Deliverable: `WORKFLOW.md` con almeno 5 workflow documentati e 30+ domande reali raccolte; scelta condivisa dei **2–3 workflow bersaglio** del prototipo.
- Rischi tipici: osservare troppo poco e costruire ciò che *voi* immaginate utile; intervistare invece di osservare (le persone descrivono il lavoro diverso da come lo fanno); promettere ai commercialisti feature e date — non promettete nulla oltre "ti faremo provare qualcosa".

### Fase 2 — Pipeline RAG seria (settimane 3–6)

- Parsing robusto del sotto-corpus scelto (incluso OCR se serve); chunking strutturale su articoli/commi con metadati completi.
- Indicizzazione su pgvector + full-text; retrieval ibrido; integrazione re-ranker; generazione con citazioni e post-verifica; gestione "non lo so" con soglia.
- API FastAPI `/chat` + UI Streamlit con fonti cliccabili. Deploy su Railway. Langfuse attivo su ogni chiamata.
- Prima versione dell'**eval set** (30–40 casi dalle domande raccolte sul campo) e primo giro di misurazione documentato.
- **Deliverable verificabile**: prototipo v0.1 online (URL accessibile ai due di voi), che risponde alle domande del sotto-dominio con citazioni cliccabili; report eval con recall@5 del retrieval, accuratezza e tasso di allucinazione misurati.
- **Rischi tipici**: inseguire feature invece di qualità (resistete: meglio 1 workflow all'80% che 3 al 40%); sottovalutare il parsing dei PDF; non misurare prima di ottimizzare (ogni modifica → eval).

### Fase 3 — Workflow di dominio (settimane 7–10)

- Implementare i 2–3 workflow scelti con i professionisti, oltre alla Q&A: tipicamente **analisi documentale** (upload di un documento → estrazione elementi rilevanti + criticità + riferimenti al corpus) e **redazione assistita** (bozza nel formato dello studio, con few-shot presi dai formati osservati).
- Tool calling dove serve davvero (es. calcoli, verifica vigenza); gestione dei documenti lunghi.
- Ampliamento eval set a 60–80 casi inclusi casi-trappola; LLM-as-judge; regime "ogni modifica → eval".
- Primo giro di **feedback strutturato**: fate provare v0.2 a 1–2 commercialisti (quelli della fase di osservazione), con protocollo della sezione 9, su casi fittizi — non dati reali.
- **Deliverable verificabile**: v0.2 con i workflow target funzionanti; report eval aggiornato con miglioramento misurato; verbale di feedback utenti con i 10 problemi principali trovati.
- **Rischi tipici**: scope creep ("aggiungiamo anche..."); tool calling/agenti dove basta un prompt; feedback raccolto in modo informale e quindi inutilizzabile.

### Fase 4 — Validazione con utenti reali (settimane 11–14)

- Indurire il prototipo per mani esterne: gestione errori, stati di caricamento onesti, limiti di input, disclaimer in UI, pagina "come verificare le fonti".
- Sessioni di prova con **5–10 commercialisti** (i 3–5 iniziali + passaparola), ciascuna: 20 min di uso libero su casi preparati, poi intervista strutturata. Registrate (con consenso) schermo e commenti.
- Cosa misurare: task completati con successo; tempo rispetto al metodo attuale; **tasso di risposte che il professionista giudica utilizzabili con revisione minore**; errori gravi per categoria (fonte sbagliata / allucinazione / formato sbagliato); la domanda secca: *"lo useresti domani se esistesse? pagheresti per questo? quanto?"*.
- Iterazione: 2 cicli di fix sulle categorie di errore dominanti, ognuno verificato sull'eval set prima di tornare dagli utenti.
- **Deliverable verificabile**: v0.3 + report di validazione con numeri per sessione e il verdetto per workflow (utile / utile-se / non utile), inclusa la disponibilità a pagare dichiarata.
- **Rischi tipici**: ascoltare i complimenti e ignorare i numeri; testare su casi troppo facili; cambiare il prototipo dopo ogni singolo commento invece di cercare pattern.

### Fase 5 — Consolidamento e demo per mentor (settimane 15–16)

- Pulizia del codice, README onesto (cosa fa, cosa non fa, architettura), demo script affidabile (mai improvvisare live su input a caso: preparate 5 domande "a effetto" che funzionano sempre + 1 in cui il sistema dice giustamente "non lo so").
- Documento di 2 pagine: architettura, metriche di eval prima/dopo, risultati di validazione, roadmap tecnica successiva.
- **Deliverable**: demo riproducibile + pacchetto per mentor/advisor.
- **Rischi**: nessuno tecnico; il rischio è non fermarsi e continuare ad aggiungere feature invece di consolidare.

---

## 6. Stima dei costi

### 6.1 Voci di costo mensili

| Voce | Scenario LEAN | Scenario COMFORT | Note |
|---|---|---|---|
| API LLM (generazione) | 30–80 € | 150–400 € | Dipende da n. domande e lunghezza contesti. In sviluppo, le run di eval contano: budgettatele |
| API embedding | 5–15 € | 20–50 € | Una tantum a re-indicizzazione; irrisorio a scala prototipo |
| Re-rank API | 0–10 € | 20–60 € | Cohere/Voyage Rerank |
| Vector DB / Postgres | 0 € (Supabase free) | 25–80 € (Supabase Pro / Neon) | Free tier ok finché il DB è piccolo |
| Hosting backend+worker | 0–20 € (Railway/Render hobby) | 40–100 € | Il worker di indicizzazione può spegnersi quando non gira |
| Demo UI hosting | 0 € (Streamlit Cloud) | 0–20 € | |
| Langfuse | 0 € (free tier) | 0–50 € | Free tier generoso |
| Sentry + uptime | 0 € | 0–30 € | |
| Dominio + email | ~2 €/mese | ~10 €/mese (Google Workspace base) | |
| Strumenti di sviluppo | 0 € (GitHub free, VS Code) | 40–80 € (GitHub Team, Copilot ×2, Cursor/Claude Code o simili) | **Gli assistenti di coding AI sono la voce con miglior ROI di tutta la tabella: non lesinate qui** |
| OCR/parsing API (se serve) | 0 € (Tesseract) | 20–80 € | Solo se avete molti PDF scannerizzati |
| **Totale mensile** | **~40–130 €** | **~350–900 €** | Entrambi sotto le soglie richieste (<500 / <2.000 €) |

### 6.2 Proiezione

| Orizzonte | LEAN | COMFORT |
|---|---|---|
| 6 mesi | 250–800 € | 2.100–5.400 € |
| 12 mesi | 500–1.600 € | 4.200–10.800 € |

A questi aggiungete una tantum: corsi/formazione (sezione 7: realisticamente 300–800 € totali), eventuale consulenza legale privacy puntuale prima dei pilot con dati veri (300–800 €), eventuali CCNL/banche dati/licenze documentali (0–500 €, solo se la fase 0 lo richiede).

### 6.3 Costi nascosti e cosa NON comprare

Costi nascosti che nessuno vi dice:
- **Le run di eval**: rieseguire 80 casi a ogni modifica costa più delle demo agli utenti. Usate modelli più economici per i giro di eval intermedi e quello buono per i gating finali.
- **Re-indicizzazioni**: ogni cambio di chunking o embedding = riprocessare tutto il corpus (parsing + embedding). A scala prototipo sono euro, ma il costo vero è il tempo.
- **Il "contesto grasso"**: prompt con 20 chunk lunghi moltiplicano il costo per chiamata. Il re-ranker che vi fa passare da 20 a 6 chunk si ripaga da solo.
- **Piano consumer vs API**: gli abbonamenti ChatGPT/Claude consumer NON si possono usare come backend del prodotto; serve la API con fatturazione a consumo. (Averli comunque per uso personale di studio: sì, 20–25 €/mese cad., soldi ben spesi.)

Cosa NON comprare all'inizio (errori di spesa tipici):
1. **GPU o istanze GPU cloud per self-hostare LLM** — la voce n. 1. Non ora.
2. **Vector DB dedicato a pagamento** prima che pgvector mostri il limite.
3. **Kubernetes, Terraform, architetture multi-regione** — state costruendo un prototipo per 10 utenti.
4. **Banche dati professionali a pagamento** (quelle che i commercialisti stessi usano) prima di aver validato che il corpus pubblico non basta per la demo.
5. **Licenze annuali** di qualunque cosa: tutto mensile, finché iterate.
6. **Consulenti** (legali, GDPR, commercialisti-consulenti) prima della fase di validazione.
7. **Un logo, un brand, biglietti da visita**: irrilevante per il prototipo.

### 6.4 Allocazione intelligente dei 20–30k

Su 12 mesi, allocazione consigliata (valori su budget di 25k):

| Destinazione | Quota | Importo |
|---|---|---|
| Costi cloud/API ricorrenti (scenario tra lean e comfort) | 15% | ~3.500 € |
| Formazione (corsi, libri, abbonamenti AI per studio) | 4% | ~1.000 € |
| Validazione (piccoli incentivi/gettoni per i professionisti che si fanno osservare e testano, se opportuni; trasferte) | 6% | ~1.500 € |
| Imprevisti tecnici (licenze dati, parsing, consulenza privacy puntuale) | 10% | ~2.500 € |
| **Riserva non allocata** (il vostro margine per iterare, sbagliare, e per la fase successiva al prototipo) | **65%** | **~16.500 €** |

Il messaggio chiave: **il prototipo costa poche migliaia di euro se fate le scelte giuste**. Il resto del capitale è runway per la fase dopo — quando saprete se c'è un prodotto. La tentazione di spendere di più "per andare più veloci" è quasi sempre sbagliata a questo stadio: il vostro vincolo è l'apprendimento, non i soldi.

---

## 7. Competenze necessarie e come acquisirle

Premessa onesta: non vi serve diventare esperti di tutto. Vi serve arrivare al livello "so cosa sto facendo e so dove cercare" su ognuna di queste voci. I prezzi indicati sono quelli noti a inizio 2026 — **riverificate sempre**: piattaforme come Udemy fanno sconti del 70–90% quasi permanenti (mai comprare a prezzo pieno lì), Coursera ha la formula audit gratuita per molti corsi.

### 7.1 Competenze tecniche

| Competenza | Livello | A cosa serve nel progetto | Dove acquisirla | Tempo | Costo |
|---|---|---|---|---|---|
| **Python** | Intermedio | Tutto il codice del progetto | *Gratis*: "Python Crash Course" (Matthes, libro ~35 € — vale come gratis+), tutorial ufficiale python.org, CS50P (Harvard, gratis su edX/OpenLearning). *A pagamento*: il corso Python di Angela Yu o Jose Portilla su Udemy (~15–20 € in sconto) | 3–5 settimane in parallelo al progetto | gratis / <100 € |
| **Lavorare con API** (HTTP, JSON, auth, retry) | Intermedio | Ogni chiamata a LLM, embedding, rerank, servizi | *Gratis*: documentazione ufficiale OpenAI/Anthropic (eccellente), "HTTP for Humans" (docs di `requests`/`httpx`). *A pagamento*: non serve — questa si impara gratis facendo | 1 settimana | gratis |
| **Git e GitHub** | Base+ | Collaborare in due senza disastri, CI, deploy | *Gratis*: "Pro Git" (libro ufficiale gratuito online), GitHub Skills (skills.github.com). *A pagamento*: non serve | 2–3 giorni + pratica continua | gratis |
| **Basi di sviluppo web** (API REST, FastAPI, un minimo di frontend) | Base | Backend del prototipo, demo UI | *Gratis*: documentazione FastAPI (tra le migliori doc mai scritte: fastapi.tiangolo.com), documentazione Streamlit. *A pagamento*: non serve per il livello richiesto | 1–2 settimane | gratis |
| **Fondamenti di ML/LLM** | Base+ | Capire cosa succede dentro, parlare con advisor, non cadere nei luoghi comuni | *Gratis*: corsi brevi di **DeepLearning.AI** (deeplearning.ai/short-courses — molti gratuiti, fatti coi vendor migliori), "What We've Learned From A Year of Building with LLMs" (serie di articoli O'Reilly, oro puro), blog di Anthropic/OpenAI. *A pagamento*: il libro **"AI Engineering" di Chip Huyen** (O'Reilly, 2025, ~50–60 €) — **raccomandato esplicitamente**: è il testo più allineato a ciò che state per fare, vi fa risparmiare settimane di tutorial sparsi | 2–3 settimane, poi continuo | <100 € (raccomandato spendere) |
| **RAG in pratica** | Intermedio | Il cuore del prodotto | *Gratis*: short course DeepLearning.AI su RAG/chunking/eval ("Building and Evaluating Advanced RAG", "Chunking for RAG" e simili), documentazione LlamaIndex, guide Pinecone Learn (pinecone.io/learn), documentazione Langfuse. *A pagamento*: "AI Engineering" (sopra) copre molto; non comprate corsi RAG dedicati costosi: le risorse gratuite dei vendor sono aggiornate e ottime | 2–3 settimane pratiche | gratis |
| **Deployment cloud** (container, Docker base, Railway/Render, Supabase) | Base | Mettere online il prototipo e tenerlo su | *Gratis*: guide ufficiali di Railway/Render/Supabase (tutorial-grade), "Docker Getting Started" ufficiale. *A pagamento*: non serve | 1 settimana | gratis |
| **Valutazione di sistemi LLM** (eval set, LLM-as-judge, Ragas) | Intermedio | La disciplina che vi distingue dal 90% dei prototipi amatoriali | *Gratis*: documentazione Ragas e Langfuse (sezioni evaluation), il già citato articolo "What We've Learned...", blog di Hamel Husain (hamel.dev) — il miglior blog esistente su eval e miglioramento iterativo di sistemi LLM, gratis. *A pagamento*: il corso di Husain & co. su evals ("AI Evals for Engineers & PMs", Maven, >500 €) è eccellente ma **prematuro ora**: tenetelo per dopo la validazione | continuo, dalla settimana 3 | gratis |

### 7.2 Competenze non tecniche

| Competenza | Livello | A cosa serve | Dove acquisirla | Tempo | Costo |
|---|---|---|---|---|---|
| **Parlare con i professionisti del dominio** (user discovery, interviste, osservazione) | Intermedio | La fase di osservazione e la validazione: senza questa costruite il prodotto sbagliato | *Gratis*: **"The Mom Test" di Rob Fitzpatrick** (libro, ~15 € — **raccomandato esplicitamente**: 100 pagine che vi impediscono di fare domande cui la gente mente per gentilezza); playbook YC su "how to talk to users" (gratis online). *A pagamento*: non serve altro | 1 settimana di lettura + pratica sul campo | <100 € (raccomandato) |
| **Validazione dell'idea** (formulare ipotesi, testare, misurare) | Base | Capire se il prototipo risolve un problema vero | *Gratis*: risorse YC Startup School (gratis). *A pagamento*: "The Mom Test" (sopra) basta per questa fase | continuo | gratis |
| **Lettura di documentazione tecnica in inglese** | Intermedio | Tutto il materiale che conta (doc API, paper, issue GitHub) è in inglese | *Gratis*: pratica deliberata — leggete le doc in inglese fin dall'inizio, niente tutorial italiani tradotti; dizionario/tecnologia di traduzione solo come stampella iniziale. È una competenza che si acquisisce solo per esposizione | continuo | gratis |
| **Scrittura tecnica minima** (README, report di validazione) | Base | Il pacchetto per i mentor; chiarezza interna | *Gratis*: leggere buoni README di progetti open source; documentazione di "Diátaxis" (diataxis.fr) | qualche ora | gratis |

**Sintesi spese formazione**: realisticamente 150–400 € totali (libro Huyen + Mom Test + un corso Udemy in sconto + eventualmente CS50 con certificato). Il resto delle risorse migliori per quello che fate è gratuito: in questo campo i vendor si fanno concorrenza sulla qualità della documentazione. L'unica spesa "premium" che ha senso da subito sono gli **assistenti di coding AI** (Cursor, Claude Code, GitHub Copilot — ~20–40 €/mese a testa): per due sviluppatori junior sono un moltiplicatore di velocità enorme *e* un tutor sempre disponibile. Raccomandati esplicitamente.

---

## 8. Errori tipici da evitare

1. **Costruire la demo prima dell'eval set.** Senza casi di test veri ogni modifica è una scommessa. Come evitarlo: le prime 30 domande dell'eval set esistono *prima* della prima ottimizzazione, e vengono dai professionisti osservati, non dalla vostra fantasia.
2. **Buttare tutto il corpus in contesto invece di fare retrieval.** "Il modello ha 1M di token di contesto, ci butto dentro tutto" → costi alti, latenza alta, qualità peggiore. Il retrieval esiste proprio perché meno contesto ma pertinente batte più contesto.
3. **Solo ricerca vettoriale, niente ricerca lessicale.** Nei domini professionali i riferimenti esatti (articoli, codici, numeri) devono matchare letteralmente: il solo embedding li manca. Ibrido vettoriale + BM25, sempre.
4. **Trascurare parsing e chunking per inseguire modelli e prompt.** Il 70% dei problemi di qualità RAG vive a monte: PDF parsati male, chunk che spezzano il senso, metadati assenti. Prima di toccare il prompt, guardate cosa il retrieval ha *effettivamente* recuperato (Langfuse serve a questo).
5. **Fine-tuning prematuro.** Costruire dataset, addestrare, valutare: settimane di lavoro per ottenere ciò che RAG + buon prompt davano già, in modo opaco e non aggiornabile. Rimandatelo a quando avrete un motivo misurato.
6. **Architettura agentica quando basta una pipeline.** Agenti = comportamento non deterministico, debug difficile, costi a cascata. Aggiungete autonomia solo quando una pipeline fissa fallisce su casi reali documentati.
7. **Self-hosting e "architettura da grande azienda" al giorno zero.** GPU, Kubernetes, microservizi, Terraform: mesi di lavoro per problemi che non avete. Il prototipo deve girare, non essere elegante. Il cloud managed esiste per voi.
8. **Ottimizzare il sistema perché "risponda sempre" invece di premiare l'onestà.** Un sistema che inventa pur di rispondere è tossico in un contesto professionale. Mettete casi-trappola nell'eval set e trattate il "non lo so" corretto come un successo, non un fallimento.
9. **Saltare l'osservazione sul campo ("tanto sappiamo già cosa serve").** Non lo sapete: non conoscete il mestiere. Ogni ora in studio con un commercialista vale dieci ore di feature immaginate. Le interviste non bastano: osservate il lavoro mentre accade.
10. **Confondere i complimenti con la validazione.** "Bello!" non paga le bollette. Le metriche che contano: task completati, errori per categoria, e la domanda "pagheresti per questo?". Registrate i numeri, non le sensazioni.
11. **Non tracciare costi e run fin dall'inizio.** Senza logging per-run non potete né debuggare né stimare i costi a scala né dimostrare i miglioramenti a un advisor. Langfuse si attiva la prima settimana, non "poi".
12. **Usare dati reali di clienti per le prove.** Prima dei DPA e delle basi privacy è un rischio legale e reputazionale enorme — basta uno screenshot girato male per bruciarvi la credibilità con la categoria. Casi fittizi costruiti coi professionisti, sempre.
13. **Nessuna delle due persone possiede il sistema intero.** Se A sa solo i dati e B sa solo l'online, al primo intoppo siete fermi. Ruotate i ruoli a metà percorso e fate code review reciproca.

---

## 9. Come capire se il prototipo "funziona"

### 9.1 Metriche semplici (dal vostro eval set)

Misurate a ogni iterazione e tenete lo storico:

| Metrica | Come si misura | Soglia "il prototipo funziona" |
|---|---|---|
| Recall del retrieval | La fonte corretta è nei top-5 recuperati? (% casi sì) | ≥ 85% |
| Accuratezza della risposta | Giudizio su eval set (sì/parziale/no, umano o LLM-as-judge verificato a campione) | ≥ 80% sì+parziali, e soprattutto in crescita tra versioni |
| Grounding / allucinazioni | % risposte con affermazioni non supportate dalle fonti citate | < 5%, tendente a zero sui casi-trappola |
| Onestà sui casi-trappola | % casi fuori corpus in cui ammette di non sapere | ≥ 90% |
| Qualità delle citazioni | % citazioni che puntano al passaggio davvero rilevante | ≥ 85% |
| Latenza percepita | Tempo a risposta completa | < 15–20 s per la Q&A (con streaming, molto meno alla prima parola) |

Le soglie non sono scienza: sono la linea sotto la quale un professionista smette di fidarsi. La metrica qualitativamente più importante è il **trend**: se a ogni iterazione i numeri salgono, il sistema "funziona" come processo — ed è quello che un mentor vuole vedere.

### 9.2 Il "test del professionista"

La prova decisiva non è numerica: è mettere il prototipo davanti a un esperto vero. Protocollo pratico, ripetibile con 5–10 professionisti anche senza avere clienti:

1. **Preparazione (30 min a sessione):** 5–8 task realistici presi dal suo lavoro vero, preparati *con lui* o dalla fase di osservazione — metà su cose che il corpus copre, almeno uno che il corpus non copre, uno su un documento da caricare. Casi fittizi, niente dati reali di clienti.
2. **Uso libero osservato (20 min):** il professionista lavora, voi tacete e annotate: dove esita, cosa clicca, cosa si aspettava, cosa lo delude, cosa lo sorprende. Non aiutatelo se non è bloccato.
3. **Intervista strutturata (15 min):** domande fisse per ogni sessione: "cosa rifaresti col tuo metodo attuale?"; "quale risposta ti avrebbe fatto perdere la fiducia e perché?"; "lo useresti domani se esistesse?"; "pagheresti per questo? quanto al mese, a spanne?"; "a chi lo consiglieresti?".
4. **Registrazione risultati:** scheda per sessione: task completati / errori gravi per categoria / verdetto per workflow (utile / utile-se / non utile) / disponibilità a pagare dichiarata / citazioni letterali memorabili.
5. **Sintesi ogni 3–4 sessioni:** cercate i pattern (stesso errore segnalato da 3 persone = priorità assoluta), ignorate i singoli desiderata ("sarebbe bello se..." → backlog, non roadmap).

### 9.3 Criterio finale del prototipo

Il prototipo ha "funzionato" — cioè ha raggiunto il suo scopo di proof of concept — se alla settimana 16 potete dire, con numeri alla mano:

- risponde correttamente e con fonti verificabili a **≥ 80%** delle domande reali del sotto-dominio scelto;
- dice "non lo so" invece di inventare, quasi sempre;
- almeno la **metà dei professionisti** che l'hanno provato dichiara che lo userebbe domani, e almeno qualcuno mette un numero sul "pagherei";
- voi due sapete spiegare ogni blocco dell'architettura, ogni metrica, e cosa fareste dopo.

Se invece i numeri dicono che non funziona — retrieval che non trova le fonti, professionisti perplessi — anche quello è un risultato prezioso: avete speso poche migliaia di euro e quattro mesi per imparare un mestiere e falsificare un'ipotesi, con 20k ancora in cassa. È esattamente per questo che la guida insiste su lean, managed, misurato.

---

## Appendice: azioni della prima settimana (per partire subito)

1. Account: GitHub org, Supabase, Railway, un provider LLM (API, con billing), Langfuse. Tutto free tier.
2. Repo monolitico: `README.md`, `.env.example`, `src/` (api, pipeline, eval), `data/` (corpus, con `SOURCES.md` per le licenze).
3. "The Mom Test" ordinato; "AI Engineering" di Huyen ordinato.
4. Lista dei primi 10 commercialisti da contattare per l'osservazione; prime 3 richieste inviate.
5. Primo corpus: 50 documenti pubblici del sotto-dominio scelto, scaricati e parsati.
6. "Hello RAG": 50 documenti → pgvector → 10 domande → risposte con citazioni, in un notebook. Brutto, vero, vostro.

Da lì in poi, la roadmap della sezione 5.
