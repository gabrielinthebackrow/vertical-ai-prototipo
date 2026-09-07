"""Parsing del corpus: PDF in data/raw/ -> testo pulito in data/clean/.

Primo blocco della pipeline OFFLINE: estrae il testo dai PDF in perimetro
(regime forfettario), fa pulizia minima e salva un .txt per documento.

Uso:
    python src/ingest/parse_pdfs.py

I file fuori perimetro (v. SKIP) restano in data/raw/ ma non vengono processati.
Se un PDF risulta scannerizzato (poco o nessun testo estraibile) viene segnalato.
"""

import re
from pathlib import Path

from pypdf import PdfReader

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")

# File fuori perimetro per il primo giro: restano nel corpus grezzo ma non si indicizzano.
SKIP = {
    "730_istruzioni_2026.pdf",
    "La_Dichiarazione_Precompilata_2026.pdf",
    "PF1_istruzioni_2026.pdf",
    "PF2_istruzioni_2026.pdf",
    "PF3_istruzioni_2026.pdf",
}

# Soglia euristica: sotto i ~40 caratteri di testo a pagina il PDF è probabilmente
# una scansione (immagine) e andrà trattato con OCR.
MIN_CHARS_PER_PAGE = 40


def clean_text(text: str) -> str:
    """Pulizia minima e conservativa: meglio poco intervento che testo rotto."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Righe vuote multiple -> una sola
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Spazi multipli -> uno solo (non tocchiamo i newline: la struttura serve al chunking)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def main() -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(RAW_DIR.glob("*.pdf"))
    scanned, done, skipped = [], 0, 0

    for pdf in pdfs:
        if pdf.name in SKIP:
            skipped += 1
            continue

        reader = PdfReader(pdf)
        pages_text = []
        total_chars = 0
        for page in reader.pages:
            t = page.extract_text() or ""
            total_chars += len(t.strip())
            pages_text.append(t)

        chars_per_page = total_chars / max(len(reader.pages), 1)
        if chars_per_page < MIN_CHARS_PER_PAGE:
            scanned.append((pdf.name, len(reader.pages), int(chars_per_page)))
            continue

        out = CLEAN_DIR / (pdf.stem + ".txt")
        out.write_text(clean_text("\n\n".join(pages_text)), encoding="utf-8")
        done += 1
        print(f"OK   {pdf.name} -> {out.name} "
              f"({len(reader.pages)} pag., {total_chars:,} caratteri)")

    print(f"\nProcessati: {done} | Saltati (fuori perimetro): {skipped}")
    if scanned:
        print("PROBABILI SCANSIONI (serve OCR, da gestire a parte):")
        for name, pages, cpp in scanned:
            print(f"  - {name}: {pages} pag., ~{cpp} caratteri/pagina")
    else:
        print("Nessun PDF scannerizzato rilevato.")


if __name__ == "__main__":
    main()
