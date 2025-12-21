
from pathlib import Path
import os
import tomllib

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"

def load_settings() -> dict:
    env_path = CONFIG_DIR / "openai_api_key.env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.strip() and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    if "OPENAI_API_KEY" not in os.environ:
        raise RuntimeError("OPENAI_API_KEY fehlt")

    config_path = CONFIG_DIR / "config.toml"
    if not config_path.exists():
        raise RuntimeError("config.toml fehlt")

    with open(config_path, "rb") as f:
        return tomllib.load(f)
