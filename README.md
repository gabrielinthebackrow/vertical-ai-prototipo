# Vertical AI — prototipo

Prototipo di vertical AI (assistente con ricerca su fonti verificate, analisi documentale,
redazione assistita). Caso di studio: dominio commercialisti italiani.

## Setup

```bash
# Python 3.12+ consigliato
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # poi compilare le chiavi
```

## Struttura

```
data/
  SOURCES.md        # registro delle fonti del corpus (URL, data, licenza) — obbligatorio
  raw/              # documenti scaricati, mai modificati a mano
  clean/            # output del parsing/pulizia
src/
  ingest/           # fase 0: download, parsing, pulizia corpus
  index/            # chunking + embedding + caricamento vector DB
  pipeline/         # online: retrieval ibrido, rerank, generazione con citazioni
  api/              # FastAPI
  eval/             # eval set + script di valutazione
docs/
  WORKFLOW.md       # workflow osservati sul campo → requisiti tecnici
```

## Regole di casa

- Niente dati reali di clienti: solo documenti pubblici o casi fittizi.
- Ogni fonte del corpus va registrata in `data/SOURCES.md` con licenza prima dell'uso.
- Ogni modifica a prompt/chunking/retrieval → rieseguire `src/eval/` e annotare i punteggi.
- I prompt di sistema vivono in file versionati, non sparsi nel codice.
