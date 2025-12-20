import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def _wrap_text(c: canvas.Canvas, text: str, x: float, y: float, max_width: float, font_name: str, font_size: int):
    """Draw text with simple word-wrap. Returns the new y position."""
    words = (text or "").split()
    if not words:
        c.drawString(x, y, "")
        return y

    line = ""
    leading = font_size * 1.4

    for w in words:
        test = (line + " " + w).strip()
        if c.stringWidth(test, font_name, font_size) <= max_width:
            line = test
        else:
            c.drawString(x, y, line)
            y -= leading
            line = w

    if line:
        c.drawString(x, y, line)
        y -= leading

    return y


def json_to_pdf(json_path: Path, pdf_path: Path) -> None:
    data = json.loads(json_path.read_text(encoding="utf-8"))

    page_w, page_h = A4
    margin = 50
    x = margin
    y = page_h - margin
    max_width = page_w - 2 * margin

    font_name = "Helvetica"
    font_size = 14
    leading = font_size * 1.4

    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    c.setFont(font_name, font_size)
    c.setTitle(str(data.get("title", "Arbeitsblatt")))

    def new_page():
        nonlocal y
        c.showPage()
        c.setFont(font_name, font_size)
        y = page_h - margin

    def ensure_space(height_needed: float):
        nonlocal y
        if y - height_needed < margin:
            new_page()

    def draw_line(text: str, extra_gap: float = 0.0):
        nonlocal y
        ensure_space(leading + extra_gap)
        c.drawString(x, y, text)
        y -= leading + extra_gap

    def draw_paragraph(text: str, extra_gap: float = 0.0):
        nonlocal y
        ensure_space(leading)
        y = _wrap_text(c, text, x, y, max_width, font_name, font_size)
        y -= extra_gap

    # Title
    title = str(data.get("title", "Arbeitsblatt"))
    draw_line(title, extra_gap=10)

    chapters = data.get("chapters", [])
    for idx, ch in enumerate(chapters, start=1):
        ch_title = str(ch.get("title", f"Kapitel {idx}"))
        ch_instr = str(ch.get("instruction", ""))

        draw_line(f"{idx}. {ch_title}", extra_gap=4)
        if ch_instr:
            draw_paragraph(ch_instr, extra_gap=6)

        ch_id = ch.get("id")

        # 1) Übersetze die Wörter
        if ch_id == "translate_words":
            items = ch.get("items", [])
            for i, it in enumerate(items, start=1):
                word_de = str(it.get("word_de", "")).strip()
                ensure_space(leading * 1.5)
                c.drawString(x, y, f"{i}) {word_de}")
                # Writing line
                line_x1 = x + 220
                line_x2 = x + max_width
                c.line(line_x1, y - 3, line_x2, y - 3)
                y -= leading

        # 2) Lückentext (NEU: Text enthält bereits ______ (Hinweis) -> keine extra Lücken-Liste drucken)
        elif ch_id == "fill_gaps":
            word_bank = ch.get("word_bank", [])
            if isinstance(word_bank, list) and word_bank:
                draw_paragraph("Wortliste: " + ", ".join(str(w) for w in word_bank), extra_gap=8)

            cloze = str(ch.get("cloze_text_foreign", "")).strip()
            if cloze:
                draw_paragraph(cloze, extra_gap=0)

            # Optional: Falls du trotzdem einen kleinen Hinweis-Block willst, kannst du das aktivieren:
            # (Standard: AUS, damit es genau so aussieht wie du willst.)
            # gaps = ch.get("gaps", [])
            # if isinstance(gaps, list) and gaps:
            #     y -= 6
            #     draw_line("Hinweise (Deutsch):", extra_gap=4)
            #     for i, g in enumerate(gaps, start=1):
            #         hint = str(g.get("hint_de", "")).strip()
            #         draw_line(f"{i}) {hint}")

        # 3) Übersetze die Sätze
        elif ch_id == "translate_sentences":
            items = ch.get("items", [])
            for i, it in enumerate(items, start=1):
                sentence_de = str(it.get("sentence_de", "")).strip()
                if sentence_de:
                    draw_paragraph(f"{i}) {sentence_de}", extra_gap=2)

                # Two writing lines for the translation
                y -= leading * 2


        else:
            draw_line("(Unbekanntes Kapitel-Format)", extra_gap=8)

        y -= 12  # chapter spacing

    c.save()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        raise SystemExit("Usage: python json2pdf.py INPUT.json OUTPUT.pdf")

    input_json = Path(sys.argv[1]).expanduser().resolve()
    output_pdf = Path(sys.argv[2]).expanduser().resolve()

    json_to_pdf(input_json, output_pdf)
    print(f"OK: {output_pdf}")
