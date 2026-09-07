"""Hello RAG completo: domanda -> ricerca -> risposta con citazioni.

Unisce i due stadi visti finora:
1. RETRIEVAL: i top-k chunk piu' pertinenti dal DB vettoriale (search.py)
2. GENERAZIONE: Gemini risponde usando SOLO quei chunk, citandoli

Include la post-verifica minima: le citazioni [N] nella risposta devono
puntare a fonti effettivamente recuperate (guardrail anti-allucinazione).

Uso:
    python src/pipeline/answer.py "qual e' il limite di ricavi del forfettario?"
    python src/pipeline/answer.py "posso detrarre l'IVA sugli acquisti?" --k 6
"""

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(".env")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import search  # il retrieval che abbiamo gia' costruito

GENERATION_MODEL = "gemini-2.5-flash"
SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "system_rag.txt").read_text(encoding="utf-8")


def build_prompt(query: str, results: list[tuple]) -> str:
    """Assembla il prompt: fonti numerate + domanda."""
    fonti = []
    for i, (doc, section, text, _dist) in enumerate(results, 1):
        fonti.append(f"[{i}] FONTE: {doc} — {section}\n{text}")
    return (
        "FONTI A DISPOSIZIONE:\n\n" + "\n\n---\n\n".join(fonti)
        + f"\n\n===\n\nDOMANDA DEL PROFESSIONISTA: {query}"
    )


def check_citations(answer: str, n_sources: int) -> list[int]:
    """Post-verifica: le citazioni devono riferirsi a fonti che esistono."""
    cited = {int(n) for n in re.findall(r"\[(\d+)\]", answer)}
    return sorted(n for n in cited if n < 1 or n > n_sources)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit('Uso: python src/pipeline/answer.py "domanda" [--k N]')
    query = sys.argv[1]
    k = int(sys.argv[sys.argv.index("--k") + 1]) if "--k" in sys.argv else 5

    results = search(query, k)
    client = genai.Client()
    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=build_prompt(query, results),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1,  # risposte stabili e conservatrici, non creative
        ),
    )
    answer = response.text

    print(answer)
    print("\n" + "=" * 60)
    print("FONTI RECUPERATE:")
    for i, (doc, section, _text, dist) in enumerate(results, 1):
        print(f"  [{i}] {doc} — {section[:70]} (distanza {dist:.3f})")

    invalid = check_citations(answer, len(results))
    if invalid:
        print(f"\n⚠ POST-VERIFICA FALLITA: citazioni non valide {invalid}")
    else:
        print("\nPost-verifica citazioni: OK")


if __name__ == "__main__":
    main()
