from pathlib import Path
import os
import requests
from dotenv import load_dotenv

# === .env Datei laden (explizit) ===
# ENV-Datei im gleichen Verzeichnis wie dieses Skript suchen
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / "OPENAI_API_KEY.env"

if not ENV_FILE.exists():
    raise RuntimeError(f"ENV-Datei fehlt: {ENV_FILE}")

load_dotenv(dotenv_path=ENV_FILE)

# === API-Key aus Environment ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY nicht gesetzt")

# === Einfachster möglicher API-Test ===
url = "https://api.openai.com/v1/models"
headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

response = requests.get(url, headers=headers, timeout=10)

if response.status_code == 200:
    print("✅ Verbindung zu OpenAI API erfolgreich")
    print(f"📦 {len(response.json().get('data', []))} Modelle gefunden")
else:
    print("❌ Verbindung fehlgeschlagen")
    print(response.status_code)
    print(response.text)
