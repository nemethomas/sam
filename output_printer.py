import subprocess
from pathlib import Path


def print_pdf(pdf_path: Path, printer: str) -> None:
    """
    Druckt ein PDF über macOS CUPS (lp).
    """
    if not pdf_path.exists():
        print(f"❌ Datei nicht gefunden: {pdf_path}")
        return

    print(f"🖨️ Drucken: {pdf_path}")
    subprocess.run(
        ["/usr/bin/lp", "-d", printer, str(pdf_path)],
        check=False
    )
