"""Prima ricerca semantica sul corpus (pipeline ONLINE, embrione).

Data una domanda in linguaggio naturale, trova i chunk piu' simili per
significato: la domanda diventa un embedding con lo stesso modello usato
per l'indice, e Postgres restituisce i chunk con distanza coseno minore.

Uso:
    python src/pipeline/search.py "qual e' il limite di ricavi del forfettario?"
    python src/pipeline/search.py "posso avere un lavoro dipendente?" --k 5
"""

import os
import sys

import psycopg
from dotenv import load_dotenv
from google import genai
from pgvector.psycopg import register_vector

load_dotenv(".env")

EMBEDDING_MODEL = "gemini-embedding-001"


def search(query: str, k: int = 3) -> list[tuple]:
    client = genai.Client()
    r = client.models.embed_content(model=EMBEDDING_MODEL, contents=query)
    qvec = r.embeddings[0].values

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        register_vector(conn)
        return conn.execute(
            """SELECT doc, section, text, embedding <=> %s::vector AS distance
               FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s""",
            (qvec, qvec, k),
        ).fetchall()


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit('Uso: python src/pipeline/search.py "domanda" [--k N]')
    query = sys.argv[1]
    k = int(sys.argv[sys.argv.index("--k") + 1]) if "--k" in sys.argv else 3

    for i, (doc, section, text, dist) in enumerate(search(query, k), 1):
        print(f"\n===== #{i}  (distanza {dist:.3f})  {doc}")
        print(f"      {section}")
        print(text[:500].replace("\n", " ") + ("..." if len(text) > 500 else ""))


if __name__ == "__main__":
    main()
