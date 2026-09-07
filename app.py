"""Demo UI del prototipo (Streamlit): la pagina che useranno i commercialisti.

Avvio:
    streamlit run app.py

Per la prova in studio: gira in locale sul portatile, niente deploy necessario.

Gestione quota free tier: se il modello principale esaurisce le richieste
giornaliere gratuite, si passa automaticamente al modello di riserva (quota
separata); se finiscono entrambe, messaggio gentile invece dell'errore.
"""

import os
import sys
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(".env")

# In locale le chiavi arrivano da .env; su Streamlit Cloud dai "secrets" dell'app.
try:
    for _k in ("GOOGLE_API_KEY", "DATABASE_URL"):
        if _k in st.secrets:
            os.environ[_k] = st.secrets[_k]
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).parent / "src" / "pipeline"))
from answer import GENERATION_MODEL, SYSTEM_PROMPT, build_prompt, check_citations
from search import search

from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

FALLBACK_MODEL = "gemini-3.5-flash-lite"  # quota gratuita separata dal modello principale

st.set_page_config(page_title="ContAI — prototipo", page_icon="📄")
st.title("ContAI — assistente di ricerca sul regime forfettario")
st.caption("Prototipo v0.1 — risponde SOLO sul regime forfettario, "
           "usando documenti pubblici dell'Agenzia delle Entrate e la normativa di riferimento.")

st.warning(
    "**Bozza dimostrativa.** Le risposte sono generate da AI su fonti pubbliche e "
    "vanno sempre verificate con un professionista prima di qualsiasi decisione.",
    icon="⚠️",
)


def generate_with_fallback(client: genai.Client, prompt: str) -> tuple[str, str | None]:
    """Genera la risposta; ritorna (testo, modello_usato o None se non ce l'ha fatta).

    Si riprova sia su quota esaurita (429) sia su errori temporanei di Google (5xx),
    poi si passa al modello di riserva.
    """
    for model in (GENERATION_MODEL, FALLBACK_MODEL):
        for attesa in (0, 45, 90):  # fino a 3 tentativi per modello
            try:
                if attesa:
                    time.sleep(attesa)
                r = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.1,
                    ),
                )
                return r.text, model
            except ClientError as e:
                if e.code == 429:
                    continue  # quota: riprova/passa al modello di riserva
                # Errore di configurazione (es. chiave non valida): inutile riprovare,
                # lo mostriamo subito per poterlo diagnosticare
                return f"__ERRORE_CONFIG__{e.code}: {e.message}", None
            except ServerError:
                continue  # errore temporaneo lato Google: si riprova
    return "", None


query = st.text_input(
    "La tua domanda",
    placeholder="es. Posso essere forfettario se ho anche un lavoro dipendente?",
)

if query:
    with st.spinner("Cerco nelle fonti e scrivo la risposta..."):
        results = search(query, k=5)
        client = genai.Client()
        answer, model_used = generate_with_fallback(client, build_prompt(query, results))

    if model_used is None:
        if answer.startswith("__ERRORE_CONFIG__"):
            st.error("Errore di configurazione della chiave Google. Dettaglio: "
                     + answer.removeprefix("__ERRORE_CONFIG__"))
        else:
            st.error("Il servizio di generazione non è disponibile in questo momento "
                     "(quota esaurita o problema temporaneo di Google). "
                     "Riprova tra un paio di minuti — intanto puoi guardare le fonti qui sotto.")
    else:
        st.markdown("### Risposta")
        st.markdown(answer)
        if model_used != GENERATION_MODEL:
            st.caption(f"(risposta generata col modello di riserva {model_used})")

        invalid = check_citations(answer, len(results))
        if invalid:
            st.error(f"Attenzione: citazioni non valide rilevate {invalid} — risposta da scartare.")

    st.markdown("### Fonti utilizzate")
    for i, (doc, section, text, dist) in enumerate(results, 1):
        with st.expander(f"[{i}] {doc} — {section[:80]}"):
            st.caption(f"Rilevanza (distanza, più bassa = più pertinente): {dist:.3f}")
            st.markdown(text)
