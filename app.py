"""Demo UI del prototipo (Streamlit): la pagina che useranno i commercialisti.

Avvio:
    streamlit run app.py

Per la prova in studio: gira in locale sul portatile, niente deploy necessario.
"""

import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(".env")

sys.path.insert(0, str(Path(__file__).parent / "src" / "pipeline"))
from answer import GENERATION_MODEL, SYSTEM_PROMPT, build_prompt, check_citations
from search import search

from google import genai
from google.genai import types

st.set_page_config(page_title="ContAI — prototipo", page_icon="📄")
st.title("ContAI — assistente di ricerca sul regime forfettario")
st.caption("Prototipo v0.1 — risponde SOLO sul regime forfettario, "
           "usando documenti pubblici dell'Agenzia delle Entrate e la normativa di riferimento.")

st.warning(
    "**Bozza dimostrativa.** Le risposte sono generate da AI su fonti pubbliche e "
    "vanno sempre verificate con un professionista prima di qualsiasi decisione.",
    icon="⚠️",
)

query = st.text_input(
    "La tua domanda",
    placeholder="es. Posso essere forfettario se ho anche un lavoro dipendente?",
)

if query:
    with st.spinner("Cerco nelle fonti e scrivo la risposta..."):
        results = search(query, k=5)
        client = genai.Client()
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=build_prompt(query, results),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.1,
            ),
        )
        answer = response.text

    st.markdown("### Risposta")
    st.markdown(answer)

    invalid = check_citations(answer, len(results))
    if invalid:
        st.error(f"Attenzione: citazioni non valide rilevate {invalid} — risposta da scartare.")

    st.markdown("### Fonti utilizzate")
    for i, (doc, section, text, dist) in enumerate(results, 1):
        with st.expander(f"[{i}] {doc} — {section[:80]}"):
            st.caption(f"Rilevanza (distanza, più bassa = più pertinente): {dist:.3f}")
            st.markdown(text)
