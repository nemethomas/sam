from pathlib import Path
import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors


def json_to_pdf_voki_correction(json_path: Path, pdf_path: Path) -> None:
    data = json.loads(json_path.read_text(encoding="utf-8"))

    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    W, H = A4

    margin = 50
    x = margin
    y = H - margin
    line = 22

    def new_page():
        nonlocal y
        c.showPage()
        c.setFont("Helvetica", 12)
        y = H - margin

    def ensure_space(h=line):
        nonlocal y
        if y - h < margin:
            new_page()

    # Fonts
    c.setFont("Helvetica-Bold", 18)
    c.drawString(x, y, data["exam"]["title"])
    y -= 30

    # Parts
    for p in data.get("parts", []):
        ensure_space(40)

        c.setFont("Helvetica-Bold", 14)
        c.drawString(
            x,
            y,
            f"{p['title']} ({p['max_points']} Punkte)"
        )
        y -= 26

        c.setFont("Helvetica", 12)

        for t in p.get("tasks", []):
            ensure_space()

            tid = t.get("id")
            prompt = t.get("prompt")
            answer = t.get("answer")
            expected = t.get("expected")
            assessment = (t.get("assessment") or "").lower()
            pts = t["points"]

            # Base text
            line_text = f"{tid}. "
            if prompt:
                line_text += f"{prompt} → {answer}"
            else:
                line_text += f"{answer}"

            c.drawString(x, y, line_text)

            tx = x + c.stringWidth(line_text, "Helvetica", 12) + 6

            # correctness markers (plain text)
            if assessment in {"korrekt", "richtig"}:
                c.drawString(tx, y, "✓")
                tx += 14
            else:
                c.drawString(tx, y, "✗")
                tx += 14

            # expected solution if wrong / partial
            if assessment not in {"korrekt", "richtig"} and expected:
                exp = expected[0] if isinstance(expected, list) else expected
                c.drawString(tx, y, f"→ {exp}")
                tx += c.stringWidth(f"→ {exp}", "Helvetica", 12) + 6
                c.drawString(tx, y, "✓")
                tx += 14

            # points
            c.drawString(tx, y, f"→ {pts['achieved']} / {pts['max']}")

            y -= line

        # Part summary
        ensure_space(20)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(
            x,
            y,
            f"Teil gesamt: {p['achieved_points']} / {p['max_points']}"
        )
        y -= 28

        # divider
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.5)
        c.line(x, y, W - margin, y)
        y -= 24
        c.setStrokeColor(colors.black)

    # Result
    result = data.get("result")
    if result:
        ensure_space(40)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x, y, "Gesamtergebnis")
        y -= 22

        c.setFont("Helvetica", 12)
        tp = result["total_points"]
        c.drawString(
            x,
            y,
            f"Punkte: {tp['achieved']} / {tp['max']}"
        )
        y -= 18

        if result.get("grade_ch") is not None:
            c.drawString(x, y, f"Note (CH): {result['grade_ch']}")

    c.save()


# Pipeline wrapper
def render(json_path: Path, output_pdf: Path) -> None:
    json_to_pdf_voki_correction(json_path, output_pdf)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python voki_correction_renderer.py INPUT.json OUTPUT.pdf")

    render(Path(sys.argv[1]), Path(sys.argv[2]))
    print("OK:", sys.argv[2])
