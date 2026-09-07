"""Costruzione dell'indice vettoriale: chunks.jsonl -> Supabase (pgvector).

Quarto blocco della pipeline OFFLINE. Per ogni chunk calcola l'embedding
(vettore di 3072 numeri che ne rappresenta il significato) con il modello
Google e lo salva nel DB insieme a testo e metadati.

Uso:
    python src/index/build_index.py

Rilanciabile: i chunk gia' presenti nel DB vengono saltati, quindi se si
interrompe (es. rate limit) basta rilanciarlo e riprende da dove era.
Per ricostruire da zero: python src/index/build_index.py --reset

Costo: gratuito col piano free di Google AI Studio (con pazienza: il piano
free ha limiti di richieste al minuto, lo script rallenta da solo).
"""

import json
import os
import sys
import time
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError, ServerError
from pgvector.psycopg import register_vector
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

load_dotenv(".env")

CHUNKS_FILE = Path("data/clean/chunks.jsonl")
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMS = 3072
BATCH_SIZE = 10          # batch piccoli: il piano free ha quota al minuto limitata
PAUSE_BETWEEN_BATCH = 8  # secondi di pausa tra una chiamata e l'altra


def _retryable(exc: BaseException) -> bool:
    # 429 (quota al minuto esaurita) e 503 (servizio occupato): si riprova
    return isinstance(exc, (ClientError, ServerError)) and exc.code in (429, 503)


@retry(
    retry=retry_if_exception(_retryable),
    wait=wait_exponential(multiplier=2, min=10, max=120),
    stop=stop_after_attempt(6),
)
def embed_batch(client: genai.Client, texts: list[str]):
    return client.models.embed_content(model=EMBEDDING_MODEL, contents=texts)


def main() -> None:
    reset = "--reset" in sys.argv
    chunks = [json.loads(l) for l in CHUNKS_FILE.open(encoding="utf-8")]
    client = genai.Client()

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        if reset:
            conn.execute("DROP TABLE IF EXISTS chunks")
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS chunks (
                id        TEXT PRIMARY KEY,
                doc       TEXT NOT NULL,
                section   TEXT NOT NULL,
                text      TEXT NOT NULL,
                embedding vector({EMBEDDING_DIMS}) NOT NULL
            )
        """)
        register_vector(conn)

        done_ids = {r[0] for r in conn.execute("SELECT id FROM chunks")}
        todo = [c for c in chunks if c["id"] not in done_ids]
        print(f"{len(chunks)} chunk totali, {len(done_ids)} gia' indicizzati, {len(todo)} da fare")

        for i in range(0, len(todo), BATCH_SIZE):
            batch = todo[i:i + BATCH_SIZE]
            r = embed_batch(client, [c["text"] for c in batch])
            for c, e in zip(batch, r.embeddings):
                conn.execute(
                    "INSERT INTO chunks (id, doc, section, text, embedding)"
                    " VALUES (%s, %s, %s, %s, %s)"
                    " ON CONFLICT (id) DO NOTHING",
                    (c["id"], c["doc"], c["section"], c["text"], e.values),
                )
            print(f"  indicizzati {len(done_ids) + min(i + BATCH_SIZE, len(todo))}/{len(chunks)}")
            time.sleep(PAUSE_BETWEEN_BATCH)

        n = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    print(f"Fatto: {n} chunk nel DB.")


if __name__ == "__main__":
    main()
