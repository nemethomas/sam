from pathlib import Path
import os
import tomllib

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"


def _load_env_file(env_path: Path) -> None:
    """
    Lädt einfache KEY=VALUE Paare in os.environ (ohne dotenv-Abhängigkeit)
    """
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def load_settings() -> dict:
    # ------------------------------------------------------------------
    # 1) LLM API Keys laden
    # ------------------------------------------------------------------
    env_path = CONFIG_DIR / "llm_api_keys.env"
    if env_path.exists():
        _load_env_file(env_path)
    else:
        raise RuntimeError("llm_api_keys.env fehlt in config/")

    # ------------------------------------------------------------------
    # 2) config.toml laden
    # ------------------------------------------------------------------
    config_path = CONFIG_DIR / "config.toml"
    if not config_path.exists():
        raise RuntimeError("config.toml fehlt")

    with open(config_path, "rb") as f:
        cfg = tomllib.load(f)

    # ------------------------------------------------------------------
    # 3) LLM Provider validieren
    # ------------------------------------------------------------------
    llm_cfg = cfg.get("llm", {})
    provider = llm_cfg.get("provider")

    if provider not in ("openai", "google"):
        raise RuntimeError(
            'Ungültiger llm.provider – erlaubt sind "openai" oder "google"'
        )

    # ------------------------------------------------------------------
    # 4) Provider-spezifische Keys prüfen
    # ------------------------------------------------------------------
    if provider == "openai":
        if "OPENAI_API_KEY" not in os.environ:
            raise RuntimeError("OPENAI_API_KEY fehlt für Provider=openai")

    if provider == "google":
        if "GOOGLE_API_KEY" not in os.environ:
            raise RuntimeError("GOOGLE_API_KEY fehlt für Provider=google")

    return cfg
