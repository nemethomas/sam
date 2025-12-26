from pathlib import Path

from renderers.voci import render as render_voci
from renderers.worksheet import render as render_worksheet

BASE_DIR = Path(__file__).resolve().parents[1]

REGISTRY = {
    "voci": {
        "prompt": BASE_DIR / "prompts" / "voci.txt",
        "renderer": render_voci,
    },
    "worksheet": {
        "prompt": BASE_DIR / "prompts" / "worksheet.txt",
        "renderer": render_worksheet,
    },
}
