"""Primo test: verifica che la chiave API Google (Gemini) funzioni.

Uso:
    source .venv/bin/activate
    python scripts/test_llm.py

Se risponde, la connessione al provider LLM è a posto e potete passare alla fase 0.

Nota: sul piano GRATUITO di Google AI Studio i contenuti inviati possono essere
usati da Google per migliorare i prodotti. OK per documenti pubblici (fase 0),
MAI per dati di clienti reali — per quelli serve il piano a pagamento.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("GOOGLE_API_KEY"):
    sys.exit(
        "GOOGLE_API_KEY mancante: apri .env, incolla la chiave "
        "(aistudio.google.com → Get API key) e riprova."
    )

from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=(
        "Sei un assistente che risponde in italiano, in modo conciso. "
        "Spiega in due frasi cosa fa un commercialista, "
        "come se lo spiegassi a uno studente di informatica."
    ),
)

print(response.text)
print()
usage = response.usage_metadata
print(f"OK — modello: gemini-2.5-flash, token usati: "
      f"{usage.prompt_token_count} in / {usage.candidates_token_count} out")
