from pipeline.openai import run_prompt_with_file
from pathlib import Path

CLASSIFY_PROMPT_FILE = Path("prompts") / "classify.txt"

def classify_file_id(file_id: str) -> str:
    result = run_prompt_with_file(
        file_id=file_id,
        prompt_file=CLASSIFY_PROMPT_FILE
    ).strip().lower()

    # harte Validierung (deterministisch!)
    if result not in {"worksheet", "voci", "unknown"}:
        return "unknown"
    return result
