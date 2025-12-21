import subprocess
from pathlib import Path

def print_pdf(pdf_path: Path, printer: str) -> None:
    if not pdf_path.exists():
        print(f"❌ Datei nicht gefunden: {pdf_path}")
        return

    print(f"🖨️ Drucken: {pdf_path} -> {printer}")
    subprocess.run(
        ["/usr/bin/lp", "-d", printer, str(pdf_path)],
        check=False,
    )
