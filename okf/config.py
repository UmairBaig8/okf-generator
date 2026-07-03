"""OKF configuration — global keys + feature sections, no env vars.

Config file locations:
  .okfconfig                      project-level (cwd)
  ~/.config/okf/config.json       user-level global defaults

Schema (both dotted and nested accepted):
  {
    "bundle_dir": "./okf_bundle",

    "llm": {
      "enabled": false,
      "provider": "openai-compatible",
      "base_url": "http://localhost:8080/v1",
      "model": "local-model",
      "api_key": "",
      "max_workers": 2
    },

    "serve": { "port": 8000, "host": "127.0.0.1" },
    "lookup": { "limit": 10, "min_score": 0.1 },
    "mcp": { "port": 0 },
    "pairs": {
      "output_file": "./okf_pairs.jsonl",
      "qa_per_concept": 3,
      "max_workers": 3,
      "pair_types": "codegen,qa,doc,summarize,crosslink"
    }
  }

Global keys (at root): bundle_dir
Sectional keys: llm.*, serve.*, lookup.*, mcp.*, pairs.*
"""

import json
from pathlib import Path

CONFIG_FILES = [
    Path.cwd() / ".okfconfig",
    Path.home() / ".config" / "okf" / "config.json",
]

DEFAULTS = {
    "bundle_dir": "./okf_bundle",
    "llm": {
        "enabled": False,
        "provider": "openai-compatible",
        "base_url": "http://localhost:8080/v1",
        "model": "local-model",
        "api_key": "",
        "max_workers": 2,
    },
    "serve": {"port": 8000, "host": "127.0.0.1"},
    "lookup": {"limit": 10, "min_score": 0.1},
    "mcp": {"port": 0},
    "pairs": {
        "output_file": "./okf_pairs.jsonl",
        "qa_per_concept": 3,
        "max_workers": 3,
        "pair_types": "codegen,qa,doc,summarize,crosslink",
    },
}


def _load_file(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load() -> dict:
    """Load merged config: DEFAULTS ← file ← user file."""
    cfg = {}
    _deep_merge(cfg, DEFAULTS)

    for cf in CONFIG_FILES:
        if cf.exists():
            data = _load_file(cf)
            if isinstance(data, dict):
                _deep_merge(cfg, data)
    return cfg


def _deep_merge(base: dict, overrides: dict):
    """Recursive dict merge."""
    for k, v in overrides.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def _get(cfg: dict, key: str, default=None):
    """Dot-notation get: cfg['llm.base_url'] → cfg['llm']['base_url']."""
    parts = key.split(".", 1)
    if len(parts) == 1:
        return cfg.get(key, default)
    section = cfg.get(parts[0], {})
    if isinstance(section, dict):
        return section.get(parts[1], default)
    return default


def _set(cfg: dict, key: str, value):
    """Dot-notation set (creates nested sections as needed)."""
    parts = key.split(".", 1)
    if len(parts) == 1:
        cfg[key] = value
    else:
        cfg.setdefault(parts[0], {})[parts[1]] = value


def dump(cfg: dict, path: Path | None = None) -> str:
    """Write config to file (or return JSON string)."""
    out = json.dumps(cfg, indent=2, ensure_ascii=False)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(out, encoding="utf-8")
    return out
