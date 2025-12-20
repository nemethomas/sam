import time
from pathlib import Path
import shutil
import tomllib 

from input_watcher import start_pdf_watcher
from output_printer import print_pdf
from openaiup import upload_pdf_to_openai
from openaipromt import run_prompt_with_file
from json2pdf import json_to_pdf  

# Basisverzeichnis = Ordner, in dem main.py liegt
BASE_DIR = Path(__file__).resolve().parent

# config.toml laden
with (BASE_DIR / "config.toml").open("rb") as f:
    cfg = tomllib.load(f)

# Werte aus der Config
WATCH_DIR = Path(cfg["paths"]["watch_dir"])    
PRINTER = cfg["printer"]["name"]
WAIT_SECONDS = int(cfg["watcher"]["wait_seconds"])
PROCESSING_DIR = BASE_DIR / "Processing"
OUTPUT_DIR = BASE_DIR / "Out"


def on_new_pdf(pdf_path: Path) -> None:
    """
    pdf_path ist DEINE zentrale Variable.
    Alles, was danach kommt, arbeitet mit diesem Path.
    """

    print(f"📄 Neue Datei erkannt: {pdf_path}")

    # ⏱️ Zusätzliche Sicherheit: 10 Sekunden warten
    # print(f"⏳ Warte 10 Sekunden zur Sicherheit...")
    # time.sleep(10)
    # print(f"✅ Wartezeit abgeschlossen, starte Verarbeitung")

    # 🔒 SOFORT aus In wegverschieben → verhindert Re-Trigger
    processing_pdf_path = PROCESSING_DIR / pdf_path.name
    shutil.move(str(pdf_path), str(processing_pdf_path))

    print(f"📦 In Processing verschoben: {processing_pdf_path}")

    # PDF zu OpenAI hochladen
    file_id = upload_pdf_to_openai(processing_pdf_path)

    # Prompt + File an OpenAI schicken
    result_text = run_prompt_with_file(file_id)
    # print("🧠 Ergebnis aus OpenAI:\n", result_text)

    # Ergebnis-JSON im Processing-Ordner speichern
    json_path = processing_pdf_path.with_suffix(".json")
    json_path.write_text(result_text, encoding="utf-8")
    print(f"🧠 JSON gespeichert: {json_path}")

    # JSON → Arbeitsblatt-PDF (nach Out, gleicher Dateiname)
    output_pdf_path = OUTPUT_DIR / processing_pdf_path.name
    json_to_pdf(json_path, output_pdf_path)
    print(f"✅ PDF erzeugt: {output_pdf_path}")

    # Ausgabe auf Drucker
    # print_pdf(output_pdf_path, printer=PRINTER)


def main():
    observer = start_pdf_watcher(
        watch_dir=WATCH_DIR,
        wait_seconds=WAIT_SECONDS,
        on_pdf=on_new_pdf,
    )

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Stop")
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
