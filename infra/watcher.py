from pathlib import Path
from typing import Callable
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class PdfHandler(FileSystemEventHandler):
    def __init__(self, wait_seconds: int, on_pdf: Callable[[Path], None]):
        self.wait_seconds = wait_seconds
        self.on_pdf = on_pdf
        self._in_progress: set[Path] = set()

    def _handle(self, path: Path):
        if path.suffix.lower() != ".pdf":
            return

        # Dedupe nur während Verarbeitung (nicht dauerhaft)
        if path in self._in_progress:
            return

        self._in_progress.add(path)
        try:
            # warten, bis Scanner fertig geschrieben hat
            time.sleep(self.wait_seconds)

            # wenn die Datei inzwischen weg ist (z.B. verschoben), abbrechen
            if not path.exists():
                return

            # niemals Exceptions aus dem Handler "rausfliegen" lassen,
            # sonst kann der Observer still sterben
            try:
                self.on_pdf(path)
            except Exception as e:
                print(f"❌ on_pdf Fehler: {e}")

        finally:
            self._in_progress.discard(path)

    def on_created(self, event):
        if event.is_directory:
            return
        self._handle(Path(event.src_path))

    def on_moved(self, event):
        if event.is_directory:
            return
        # Scanner macht oft create tmp -> move final
        self._handle(Path(event.dest_path))


def start_pdf_watcher(watch_dir: Path, wait_seconds: int, on_pdf: Callable[[Path], None]):
    handler = PdfHandler(wait_seconds, on_pdf)
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()
    return observer
