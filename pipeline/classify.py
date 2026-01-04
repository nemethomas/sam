from pathlib import Path
from pipeline.llm_handler import run_prompt_with_file
from settings import load_settings

CLASSIFY_PROMPT_FILE = Path("prompts") / "classify.txt"

_cfg = load_settings()   # einmal laden (kein Overhead)

def classify_file_id(file_id: str) -> str:
    result = run_prompt_with_file(
        file_id=file_id,
        cfg=_cfg,
        prompt_file=CLASSIFY_PROMPT_FILE,
    ).strip().lower()

    # harte Validierung (deterministisch!)
    if result not in {"worksheet", "voci", "unknown"}:
        return "unknown"
    return result
