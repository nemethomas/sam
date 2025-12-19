import json
import os
import requests
from pathlib import Path 
from dotenv import load_dotenv

# === .env für API-Key (wie in openaiconnect.py) ===
# ENV-Datei im gleichen Verzeichnis wie dieses Skript suchen
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / "OPENAI_API_KEY.env"

if not ENV_FILE.exists():
    raise RuntimeError(f"ENV-Datei fehlt: {ENV_FILE}")

load_dotenv(dotenv_path=ENV_FILE)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY nicht gesetzt")

# === Pfad zum Prompt-Text ===
PROMPT_FILE = BASE_DIR / "promt.txt"


def run_prompt_with_file(file_id: str, model: str = "gpt-4.1-mini") -> str:
    """
    Ruft den OpenAI Responses-Endpunkt mit Prompt und einem File Attachment auf.
    
    Args:
        file_id: ID der zuvor hochgeladenen Datei
        model: zu nutzendes Modell (Standard: gpt-4.1-mini)
    
    Returns:
        out_text: Extrahierter Antworttext; wird zusätzlich als result.json gespeichert
    """    
    if not PROMPT_FILE.exists():
        raise RuntimeError(f"Prompt-Datei fehlt: {PROMPT_FILE}")

    prompt_text = PROMPT_FILE.read_text(encoding="utf-8").strip()

    resp = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt_text},
                        {"type": "input_file", "file_id": file_id}
                    ]
                }
            ]
        }),
        timeout=60
    )
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        print("❌ OpenAI-Fehler:", resp.status_code, resp.text)
        raise

    resp.raise_for_status()
    print("✅ Verarbeitung OK")

    data = resp.json()

    # === output_text extrahieren ===
    out_text = ""
    for item in data.get("output", []):
        for c in item.get("content", []):
            if c.get("type") in ("output_text", "text"):
                out_text += c.get("text", "")

    out_text = out_text.strip()

    # === JSON lokal speichern ===
    #Path("result.json").write_text(out_text, encoding="utf-8")
    #print("✅ result.json gespeichert")

    return out_text
