"""Chunking strutturale del corpus: testi in data/clean/ -> data/clean/chunks.jsonl.

Terzo blocco della pipeline OFFLINE. Strategia per TIPO di documento (non uguale
per tutti: e' il punto del chunking strutturale, guida sez. 2.2):

- circolari AdE      -> un chunk per sezione numerata ("2.3. Cause ostative...")
- testi di legge     -> un chunk per comma ("Articolo 1 Comma 54")
- leggi di bilancio  -> PRIMA si estraggono solo i commi pertinenti (il resto e'
  complete          rumore fuori perimetro), POI chunking per comma/sezione
- schede/pagine brevi-> un chunk unico (sono gia' unita' di senso complete)

Ogni chunk porta i metadati che serviranno per citazioni e filtri:
doc (file sorgente), section (sezione/comma), text.
Se una sezione supera MAX_CHARS viene spezzata con overlap (fallback).

Uso:
    python src/index/chunk.py
"""

import json
import re
from pathlib import Path

CLEAN_DIR = Path("data/clean")
OUT_FILE = CLEAN_DIR / "chunks.jsonl"

MAX_CHARS = 6000      # oltre questa soglia una sezione viene spezzata
OVERLAP_CHARS = 600   # sovrapposizione tra sotto-chunk del fallback

# Legge di stabilita' 2015 completa: NON la chunkiamo — i commi che contano
# (54-89) li abbiamo gia' nel file dedicato, il resto e' rumore fuori perimetro.
SKIP = {"190_2014.txt"}

# Leggi di bilancio complete: estraiamo SOLO la finestra pertinente.
# start: regex sul primo comma rilevante; end: regex sul comma che chiude la finestra.
EXTRACT = {
    "Legge del 30_12_2018 n. 145 - .txt": {
        # commi 9-15 dell'art. 1: modifiche al forfettario del 2019
        "start": re.compile(r"^9\.\s", re.MULTILINE),
        "end": re.compile(r"\n\s*16\.\s"),
        "label": "Legge 145/2018, art. 1, commi 9-15",
    },
    "Legge del 29_12_2022 n. 197 - .txt": {
        # comma 454 dell'art. 1: innalzamento della soglia a 85.000 euro
        "start": re.compile(r"454\.\s"),
        "end": re.compile(r"455\.\s"),
        "label": "Legge 197/2022, art. 1, comma 454",
    },
}

SECTION_RE = re.compile(r"^(\d+(?:\.\d+)?)\.\s+(.{3,}?)\s*$")
COMMA_RE = re.compile(r"^Articolo\s+(\d+)\s+Comma\s+(\d+[\w-]*)", re.MULTILINE)

# Boilerplate delle stampe Normattiva/AdE: non porta significato, lo togliamo.
BOILERPLATE_RE = re.compile(r"^(Torna al sommario|Pagina \d+)\s*$", re.MULTILINE)

MIN_CHARS = 80  # sotto questa soglia un chunk e' un residuo (n. pagina, titolo orfano)


def split_with_overlap(text: str) -> list[str]:
    """Fallback per sezioni troppo lunghe: spezza su confini di paragrafo."""
    paragraphs = text.split("\n\n")
    chunks, current = [], ""
    for p in paragraphs:
        if current and len(current) + len(p) > MAX_CHARS:
            chunks.append(current.strip())
            current = current[-OVERLAP_CHARS:] + "\n\n" + p
        else:
            current = current + "\n\n" + p if current else p
    if current.strip():
        chunks.append(current.strip())
    return chunks


def chunk_by_sections(text: str) -> list[tuple[str, str]]:
    """Circolari: spezza sulle intestazioni numerate del corpo (non sull'indice)."""
    lines = text.split("\n")
    sections: list[tuple[str, list[str]]] = []
    current_title, current_lines = "premessa", []
    for line in lines:
        if "...." in line:  # riga dell'indice con i puntini di guida: non e' un titolo vero
            continue
        m = SECTION_RE.match(line)
        if m and len(line) < 120:
            if current_lines:
                sections.append((current_title, current_lines))
            current_title = f"{m.group(1)} {m.group(2).strip()}"
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((current_title, current_lines))
    return [(t, "\n".join(ls).strip()) for t, ls in sections if "\n".join(ls).strip()]


def chunk_by_commi(text: str) -> list[tuple[str, str]]:
    """Testi di legge: spezza sui marcatori 'Articolo X Comma Y'."""
    matches = list(COMMA_RE.finditer(text))
    out = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.start():end].strip()
        if body:
            out.append((f"art. {m.group(1)}, comma {m.group(2)}", body))
    return out


def main() -> None:
    chunks = []
    for txt in sorted(CLEAN_DIR.glob("*.txt")):
        if txt.name in SKIP:
            print(f"SKIP {txt.name} (sostituita dal file dei soli commi 54-89)")
            continue

        text = txt.read_text(encoding="utf-8")

        if txt.name in EXTRACT:
            cfg = EXTRACT[txt.name]
            s = cfg["start"].search(text)
            if not s:
                print(f"!!   {txt.name}: ancora di inizio NON trovata, file saltato")
                continue
            e = cfg["end"].search(text, s.end() + 500)
            text = text[s.start(): e.start() if e else s.start() + 40_000]
            print(f"OK   {txt.name}: estratta finestra '{cfg['label']}' ({len(text):,} caratteri)")

        if COMMA_RE.search(text):
            parts = chunk_by_commi(text)
        else:
            parts = chunk_by_sections(text)

        n = 0
        for title, body in parts:
            body = BOILERPLATE_RE.sub("", body).strip()
            for sub in split_with_overlap(body) if len(body) > MAX_CHARS else [body]:
                if len(sub) < MIN_CHARS:
                    continue
                chunks.append({
                    "id": f"{txt.stem}#{n}",
                    "doc": txt.name,
                    "section": title[:200],
                    "n_chars": len(sub),
                    "text": sub,
                })
                n += 1
        print(f"     {txt.name}: {n} chunk")

    with OUT_FILE.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    sizes = sorted(c["n_chars"] for c in chunks)
    print(f"\nTotale: {len(chunks)} chunk in {OUT_FILE}")
    if sizes:
        print(f"Dimensioni: min {sizes[0]} | mediana {sizes[len(sizes)//2]} | max {sizes[-1]}")


if __name__ == "__main__":
    main()
