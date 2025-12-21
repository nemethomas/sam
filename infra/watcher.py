
from pathlib import Path
from typing import Callable
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PdfHandler(FileSystemEventHandler):
    def __init__(self, wait_seconds: int, on_pdf: Callable[[Path], None]):
        self.wait_seconds = wait_seconds
        self.on_pdf = on_pdf
        self._in_progress = set()
        self._done = set()

    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() != ".pdf":
            return
        if path in self._done or path in self._in_progress:
            return

        self._in_progress.add(path)
        time.sleep(self.wait_seconds)
        self._in_progress.remove(path)
        self._done.add(path)
        self.on_pdf(path)

def start_pdf_watcher(watch_dir: Path, wait_seconds: int, on_pdf: Callable[[Path], None]):
    handler = PdfHandler(wait_seconds, on_pdf)
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()
    return observer
