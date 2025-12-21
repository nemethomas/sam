import time
import shutil
from pathlib import Path
from infra.printing import print_pdf
from infra.watcher import start_pdf_watcher
from pipeline.process import process
from settings import load_settings, BASE_DIR


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def unique_path(target: Path) -> Path:
    """Falls target existiert, hänge _1, _2, ... an."""
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    i = 1
    while True:
        candidate = target.with_name(f"{stem}_{i}{suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def on_new_pdf(pdf_path: Path, cfg: dict) -> None:
    # Pfade (aus cfg, fallback auf BASE_DIR)
    paths = cfg.get("paths", {})
    in_dir = Path(paths.get("watch_dir", BASE_DIR / "files" / "in"))
    processing_dir = Path(paths.get("processing_dir", BASE_DIR / "files" / "proc"))
    out_dir = Path(paths.get("output_dir", BASE_DIR / "files" / "out"))

    ensure_dir(in_dir)
    ensure_dir(processing_dir)
    ensure_dir(out_dir)

    print(f"📥 Neu: {pdf_path}")

    # In → Processing verschieben
    processing_pdf_path = unique_path(processing_dir / pdf_path.name)
    shutil.move(str(pdf_path), str(processing_pdf_path))
    print(f"📦 Processing: {processing_pdf_path}")

    # Pipeline starten
    try:
        out_pdf_path = process(
            pdf_path=processing_pdf_path,
            output_dir=out_dir,
        )
        print(f"✅ Fertig: {out_pdf_path}")

        printer = cfg.get("printer", {}).get("name")
        auto_print = bool(cfg.get("printer", {}).get("auto_print", True))

        if auto_print and printer:
            print_pdf(out_pdf_path, printer=printer)
        else:
            print("ℹ️ Auto-Print aus oder kein Printer konfiguriert – PDF bleibt im Out-Ordner.")

    except Exception as e:
        print(f"❌ Fehler: {e}")


def main() -> None:
    cfg = load_settings()

    paths = cfg.get("paths", {})
    watch_dir = Path(paths.get("watch_dir", BASE_DIR / "In"))
    ensure_dir(watch_dir)

    wait_seconds = int(cfg.get("watcher", {}).get("wait_seconds", 10))

    observer = start_pdf_watcher(
        watch_dir=watch_dir,
        wait_seconds=wait_seconds,
        on_pdf=lambda p: on_new_pdf(p, cfg),
    )

    print(f"👀 Watcher läuft: {watch_dir} (wait_seconds={wait_seconds})")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Stop")
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
