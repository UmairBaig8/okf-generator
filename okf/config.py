"""OKF configuration — extensible, env + file, local-first defaults.

Config file locations (loaded in order, later overrides earlier):
  .okfconfig                         project-level (cwd)
  ~/.config/okf/config.json          user-level

Extensible design: any key is allowed, grouped by section prefix.
Currently known sections: llm (future: serve, viz, mcp, ...).

Example .okfconfig:
  {
    "llm": {
      "base_url": "http://localhost:8080/v1",
      "model": "local-model",
      "api_key": "",
      "max_workers": 2
    }
  }

Both dotted ("llm.base_url") and nested ("llm": {"base_url": ...}) work.
Env vars take precedence: OKF_BASE_URL, OKF_MODEL, OKF_API_KEY, OKF_MAX_WORKERS
"""

import json
import os
from pathlib import Path

CONFIG_FILES = [
    Path.cwd() / ".okfconfig",
    Path.home() / ".config" / "okf" / "config.json",
]

DEFAULTS = {
    "llm.base_url": "http://localhost:8080/v1",
    "llm.model": "local-model",
    "llm.max_workers": 2,
}

ENV_TO_KEY = {
    "OKF_BASE_URL": "llm.base_url",
    "OKF_MODEL": "llm.model",
    "OKF_API_KEY": "llm.api_key",
    "OKF_MAX_WORKERS": "llm.max_workers",
}


def _load_file(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _get(cfg: dict, key: str, default=None):
    """Dot-notation get: cfg['llm.base_url'] → cfg['llm']['base_url']."""
    parts = key.split(".", 1)
    if len(parts) == 1:
        return cfg.get(key, default)
    section = cfg.get(parts[0], {})
    return section.get(parts[1], default) if isinstance(section, dict) else default


def _set(cfg: dict, key: str, value):
    """Dot-notation set."""
    parts = key.split(".", 1)
    if len(parts) == 1:
        cfg[key] = value
    else:
        cfg.setdefault(parts[0], {})[parts[1]] = value


def load() -> dict:
    """Load merged config: defaults ← file ← env vars."""
    cfg = {}

    # Start with defaults
    for k, v in DEFAULTS.items():
        _set(cfg, k, v)

    # Layer config files
    for cf in CONFIG_FILES:
        if cf.exists():
            data = _load_file(cf)
            if isinstance(data, dict):
                for k, v in data.items():
                    _set(cfg, k, v)

    # Env vars override
    for env_key, cfg_key in ENV_TO_KEY.items():
        val = os.environ.get(env_key)
        if val:
            if "max_workers" in env_key.lower():
                try:
                    val = int(val)
                except ValueError:
                    continue
            _set(cfg, cfg_key, val)

    return cfg


def dump(cfg: dict, path: Path | None = None) -> str:
    """Write config to file (or return JSON string)."""
    out = json.dumps(cfg, indent=2, ensure_ascii=False)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(out, encoding="utf-8")
    return out
