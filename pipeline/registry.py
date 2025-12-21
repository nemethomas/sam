
from pathlib import Path
from renderers.voci import render as render_voci

BASE_DIR = Path(__file__).resolve().parents[1]

REGISTRY = {
    "voci": {
        "prompt": BASE_DIR / "prompts" / "voci.txt",
        "renderer": render_voci,
    }
}
