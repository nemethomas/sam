# sam

Erstellt Arbeitsblätter aufgrund von Schulunterlagen und korrigiert Prüfungen mit Hilfe von AI


---

## 🎯 Project Overview

Meine Kinder sind in der Mittelstufe lernen von Hand schreiben. Das Erstellen von Arebeitsblättern und korrigieren von Prüfungen erfordert viel Zeit. schreiben von Hand. Wir haben zuhause einen Scanner sowie einen Drucker als Kopiergerät Kombi. 

Mensch Maschine Interface Scanner Drucker

Selbständigkeit

### Key Features

✅ **Arbeitsblätter aus Wortlisten** - Als Input eignen sich Wortlisten oder Schulstoff im allgemeinen.
✅ **Arbeitsblätter korriergieren** - Berten von ausgefüllten Arbeitsbättern

---

## 🧠 AI Anbidung
Der Prototyp spricht über API mit OpenAi, grundätzlich soll das LLM wählbar sein. 

Ziel ist es das LLM direkt auf der Hardwarekomponente zu installieren und ohne Internet auskommen

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Brew ([brew.sh](https://brew.sh))
- Miniconda ([brew.sh](https://formulae.brew.sh/cask/miniconda#default))
- Open AI API Key ([plattform.openai.com](https://platform.openai.com/api-keys))

### Installation

1. **Install dependencies:**
```bash
conda env create -f environment.yml

```

2. **Create `.env` file:**
```bash
cp .env.example .env
```

3. **Add your secrets to `.env`:**
```
OPENAI_API_KEY=sk-XXX
```


## 📁 Project Structure

```


sam/               
├── config/                  
│   ├── config.toml              # Netzwerkdrucker  
│   ├── OPENAI_API_KEY.env
│   ├── envoronment.yml          # Estellt die Conda Umgebung
├── files/
│   ├── in/                      # Zielverzeichnis für Scanning ins Netzwerkverzeichnis
│   ├── proc/
│   ├── out/
├── pipline/
│   ├── classyfiy.py             # Kalassifizierung 
│   ├── openai.py                # OpenAi Handler 
│   ├── process.py               # Workflow
│   ├── registry.py              # Verbindung von Promt und Render
├── prompts
│   ├── voci.txt
│   ├── ...
├── renderers
│   ├── voci.py
│   ├── ...
main.py
settings.py
readme.md

```
---


### Data Format

```json
{
  "exam": {
    "type": "voci_pruefung",
    "title": "<<TITLE>>",
    "unit": "<<UNIT>>",
    "language_pair": {
      "from": "<<FROM_LANGUAGE>>",
      "to": "<<TO_LANGUAGE>>"
    },
    "max_points": <<MAX_POINTS>>
  },
  "parts": [
    {
      "id": 1,
      "title": "Übersetze die Wörter",
      "max_points": <<PART1_MAX>>,
      "achieved_points": null,
      "tasks": [
        {
          "id": 1,
          "prompt": "<<DE_WORD>>",
          "answer": "<<STUDENT_ANSWER>>",
          "expected": [<<EXPECTED_SOLUTIONS>>],
          "assessment": "",
          "points": { "achieved": null, "max": 2 },
          "comment": ""
        }
      ]
    
  }
}    

```

---
