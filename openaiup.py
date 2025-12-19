from pathlib import Path
import os
import requests
from dotenv import load_dotenv

# === API-Key aus .env-Datei laden (wie in openaiconnect.py) ===
# ENV-Datei im gleichen Verzeichnis wie dieses Skript suchen
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / "OPENAI_API_KEY.env"

if not ENV_FILE.exists():
    raise RuntimeError(f"ENV-Datei fehlt: {ENV_FILE}")

load_dotenv(dotenv_path=ENV_FILE)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY nicht gesetzt")


def upload_pdf_to_openai(pdf_path: Path) -> str:
    """
    Lädt eine PDF-Datei zu OpenAI hoch und gibt die file_id zurück.
    
    Args:
        pdf_path: Pfad zur PDF-Datei
        
    Returns:
        file_id: Die ID der hochgeladenen Datei bei OpenAI
    """
    resp = requests.post(
        "https://api.openai.com/v1/files",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        files={
            "file": (pdf_path.name, pdf_path.open("rb"), "application/pdf")
        },
        data={
            "purpose": "assistants"
        },
        timeout=30
    )
    
    resp.raise_for_status()
    file_id = resp.json()["id"]
    
    print("✅ Upload OK, file_id:", file_id)
    return file_id
