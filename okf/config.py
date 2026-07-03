"""OKF configuration loader — env vars first, then config file fallback.

Config file locations (loaded in order, later overrides earlier):
  - .okfconfig                    project-level (cwd)
  - ~/.config/okf/config.json     user-level

Format (JSON):
  {
    "api_key": "sk-...",
    "base_url": "https://api.anthropic.com/v1",
    "model": "claude-sonnet-4-6",
    "max_workers": 2
  }

Env vars take precedence over config file:
  OKF_API_KEY, OKF_BASE_URL, OKF_MODEL, OKF_MAX_WORKERS
"""

import json
import os
from pathlib import Path

CONFIG_FILES = [
    Path.cwd() / ".okfconfig",
    Path.home() / ".config" / "okf" / "config.json",
]

DEFAULTS = {
    "base_url": "https://api.anthropic.com/v1",
    "model": "claude-sonnet-4-6",
    "max_workers": 2,
}

ENV_MAP = {
    "api_key": "OKF_API_KEY",
    "base_url": "OKF_BASE_URL",
    "model": "OKF_MODEL",
    "max_workers": "OKF_MAX_WORKERS",
}


def _load_file(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load() -> dict:
    cfg = dict(DEFAULTS)

    for cf in CONFIG_FILES:
        if cf.exists():
            data = _load_file(cf)
            if isinstance(data, dict):
                cfg.update(data)

    # Env vars override everything
    for key, env in ENV_MAP.items():
        val = os.environ.get(env)
        if val:
            if key == "max_workers":
                try:
                    cfg[key] = int(val)
                except ValueError:
                    pass
            else:
                cfg[key] = val

    return cfg


def dump(cfg: dict, path: Path | None = None) -> str:
    """Write config to file (or return JSON string)."""
    out = json.dumps(cfg, indent=2, ensure_ascii=False)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(out, encoding="utf-8")
    return out
