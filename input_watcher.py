import time
from pathlib import Path
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class PdfHandler(FileSystemEventHandler):
    def __init__(self, wait_seconds: int, on_pdf: Callable[[Path], None]):
        self.wait_seconds = wait_seconds
        self.on_pdf = on_pdf

        # Dedupe, damit doppelte Events nicht doppelt verarbeitet werden
        self._in_progress: set[Path] = set()
        self._done: set[Path] = set()

        # Polling-Parameter (aus wait_seconds abgeleitet, damit du main nicht ändern musst)
        self._poll_interval = 0.2
        self._stable_checks = max(3, int(wait_seconds / self._poll_interval))
        self._timeout = max(10.0, float(wait_seconds) * 5)

    def _wait_until_ready(self, path: Path) -> bool:
        start = time.time()
        last = None
        same = 0

        while True:
            if not path.exists():
                return False

            st = path.stat()
            cur = (st.st_size, st.st_mtime)

            if cur == last:
                same += 1
                if same >= self._stable_checks:
                    return True
            else:
                last = cur
                same = 0

            if time.time() - start > self._timeout:
                return False

            time.sleep(self._poll_interval)

    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)
        if path.suffix.lower() != ".pdf":
            return

        # Dedupe
        if path in self._done or path in self._in_progress:
            return
        self._in_progress.add(path)

        try:
            print(f"📂 Neue PDF erkannt: {path}")

            if not self._wait_until_ready(path):
                print(f"⏭️  Datei nicht bereit/weg/timeout: {path}")
                return

            try:
                self.on_pdf(path)
                self._done.add(path)
            except Exception as e:
                print(f"❌ Fehler bei Verarbeitung von {path}: {e}")
                import traceback
                traceback.print_exc()
                # Datei NICHT zu _done hinzufügen, damit sie bei Bedarf erneut verarbeitet werden kann

        finally:
            self._in_progress.discard(path)


def start_pdf_watcher(
    watch_dir: Path,
    wait_seconds: int,
    on_pdf: Callable[[Path], None],
) -> Observer:
    """
    Startet watchdog Observer und gibt ihn zurück (damit man ihn später stoppen kann).
    """
    # (wie von dir gewünscht: hier keine Ordner erstellen; check kannst du drin lassen oder entfernen)
    if not watch_dir.exists():
        raise FileNotFoundError(f"Verzeichnis nicht gefunden: {watch_dir}")

    print(f"👀 Watcher läuft auf: {watch_dir.resolve()}")

    handler = PdfHandler(wait_seconds=wait_seconds, on_pdf=on_pdf)
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()
    return observer
