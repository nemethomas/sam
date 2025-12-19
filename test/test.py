import time
import sys
import shutil
from pathlib import Path

# Projekt-Root (sam/)
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from input_watcher import start_pdf_watcher  # noqa


WATCH_DIR = ROOT_DIR / "In"
WAIT_SECONDS = 5

TEST_PDF = Path(__file__).parent / "test_1.pdf"


def on_new_pdf(pdf_path: Path) -> None:
    print(f"📄 PDF erkannt: {pdf_path}")


def main():
    observer = start_pdf_watcher(
        watch_dir=WATCH_DIR,
        wait_seconds=WAIT_SECONDS,
        on_pdf=on_new_pdf,
    )

    # --- Test-PDF nach In kopieren ---
    if not TEST_PDF.exists():
        raise FileNotFoundError(f"Test-PDF nicht gefunden: {TEST_PDF}")

    target = WATCH_DIR / TEST_PDF.name
    shutil.copy2(TEST_PDF, target)
    print(f"📎 Kopiert: {TEST_PDF} → {target}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Stop")
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()