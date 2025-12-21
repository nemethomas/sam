
from pathlib import Path

def classify(pdf_path: Path) -> str:
    name = pdf_path.name.lower()
    if "voci" in name or "vokabel" in name:
        return "voci"
    return "voci"
