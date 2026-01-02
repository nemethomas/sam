# Sam

**Sam** ist ein lokales Automatisierungssystem, das aus Schulunterlagen **Arbeitsblätter generiert** und **ausgefüllte Prüfungen korrigiert** – unterstützt durch KI, aber vollständig **On-Prem steuerbar**.

Der typische Workflow:
1. Ein Dokument wird eingescannt
2. Sam erkennt den Dokumenttyp
3. Die passende KI-Auswertung wird ausgeführt
4. Das Resultat wird als PDF gerendert
5. Optional wird das Ergebnis automatisch gedruckt

---

## ✨ Key Features

✅ **Arbeitsblätter aus Wortlisten & Schulunterlagen**  
Erzeugt strukturierte Arbeitsblätter (z. B. Vokabelprüfungen) aus einfachen Wortlisten oder PDFs.

✅ **Automatische Korrektur von Prüfungen**  
Bewertet ausgefüllte Arbeitsblätter inklusive Punktevergabe und Feedback.

✅ **Deterministische Pipeline**  
Klassifikation → Prompt → JSON → PDF – vollständig nachvollziehbar und erweiterbar.

✅ **Lokaler Betrieb**  
Keine Cloud-Abhängigkeit ausser dem LLM-API. Ideal für Schule & Zuhause.

✅ **Optionaler Netzwerkdruck**  
Fertige PDFs können automatisch auf einem Netzwerkdrucker ausgegeben werden.

---

## 🚀 Quick Start

### Prerequisites

- Python **3.13+**
- Homebrew – https://brew.sh
- Miniconda – https://formulae.brew.sh/cask/miniconda
- OpenAI API Key – https://platform.openai.com/api-keys
- Netzwerkdrucker (optional)

---

## 🔧 Installation

### 1. Conda-Umgebung erstellen

```bash
conda env create -f environment.yml
conda activate sam
```

---

### 2. OpenAI API Key hinterlegen

Erstelle die Datei:

```
sam/config/OPENAI_API_KEY.env
```

Inhalt:

```env
OPENAI_API_KEY=sk-XXX
```

---

### 3. Konfiguration erstellen

Erstelle:

```
sam/config/config.toml
```

Beispiel:

```toml
[printer]
# Name deines Netzwerkdruckers
# Unter macOS z.B.: lpstat -p
name = "HP_Color_LaserJet_Pro_MFP_3302__A195A7_"

# Falls kein automatischer Druck gewünscht ist
auto_print = true


[paths]
# Ordner, in den dein Scanner PDFs ablegt
# Dieser Ordner wird von Sam überwacht
watch_dir = "/Users/family/sam/files/in"


[watcher]
# Wartezeit (Sekunden), bis eine neue PDF als stabil gilt
wait_seconds = 7
```

---

## ▶️ Starten

```bash
python main.py
```

Sobald ein neues PDF im `watch_dir` erscheint, wird es automatisch verarbeitet.

---

## 📁 Project Structure

```text
sam/
├── config/
│   ├── config.toml              # Zentrale Konfiguration
│   ├── OPENAI_API_KEY.env       # API Key
│   └── environment.yml          # Conda Environment
│
├── files/
│   ├── in/                      # Scan-Eingang
│   ├── proc/                    # Verarbeitung
│   └── out/                     # Resultierende PDFs
│
├── pipeline/
│   ├── classify.py              # Dokument-Klassifikation
│   ├── openai.py                # OpenAI Schnittstelle
│   ├── process.py               # Workflow-Orchestrierung
│   └── registry.py              # Prompt ↔ Renderer Mapping
│
├── prompts/
│   ├── voci.txt                 # Prompt für Vokabelprüfungen
│   └── ...
│
├── renderers/
│   ├── voci.py                  # JSON → PDF Renderer
│   └── ...
│
├── main.py                      # Einstiegspunkt
├── settings.py                  # Konfig-Lader
└── README.md
```
---

## 🧩 Erweiterbarkeit

- Neue Dokumenttypen → **neue Klassifikation**
- Neue Aufgabenformate → **neuer Prompt**
- Neue Darstellung → **neuer Renderer**

Alles ist bewusst **modular** gehalten.
