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

    "providers": {
      "anthropic": { "base_url": "https://api.anthropic.com/v1", "api_key": "" },
      "openai": { "base_url": "https://api.openai.com/v1", "api_key": "" },
      "deepseek": { "base_url": "https://api.deepseek.com/v1", "api_key": "" },
      "gemini": { "base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "api_key": "" },
      "glm": { "base_url": "https://open.bigmodel.cn/api/paas/v4", "api_key": "" },
      "openrouter": { "base_url": "https://openrouter.ai/api/v1", "api_key": "" },
      "dashscope": { "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "api_key": "" },
      "minimax": { "base_url": "https://api.minimax.io/v1", "api_key": "" },
      "ollama": { "base_url": "http://localhost:11434/v1", "api_key": "" },
      "lmstudio": { "base_url": "http://localhost:1234/v1", "api_key": "" },
      "local": { "base_url": "http://localhost:8080/v1", "api_key": "" }
    },

    "enrich": {
      "description": { "model": "", "max_workers": 2 },
      "deep": { "enabled": false, "model": "", "max_workers": 2 },
      "security": { "enabled": false, "model": "", "max_workers": 2 },
      "semantic_related": { "enabled": false, "max_workers": 2 }
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

Provider resolution (applied in order):
  1. enrich.{mode}.{key}          — per-mode override
  2. providers.{provider}.{key}   — named provider defaults
  3. llm.{key}                    — global fallback
  4. hardcoded default            — code-level fallback

Global keys (at root): bundle_dir
Sectional keys: llm.*, providers.*, enrich.*, serve.*, lookup.*, mcp.*, pairs.*
"""

import json
from pathlib import Path

CONFIG_FILES = [
    Path.home() / ".config" / "okf" / "config.json",
    Path.cwd() / ".okfconfig",
]

BUILTIN_PROVIDERS = {
    "anthropic": {"base_url": "https://api.anthropic.com/v1", "api_key": ""},
    "openai": {"base_url": "https://api.openai.com/v1", "api_key": ""},
    "deepseek": {"base_url": "https://api.deepseek.com/v1", "api_key": ""},
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "api_key": ""},
    "glm": {"base_url": "https://open.bigmodel.cn/api/paas/v4", "api_key": ""},
    "openrouter": {"base_url": "https://openrouter.ai/api/v1", "api_key": ""},
    "dashscope": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "api_key": ""},
    "minimax": {"base_url": "https://api.minimax.io/v1", "api_key": ""},
    "ollama": {"base_url": "http://localhost:11434/v1", "api_key": ""},
    "lmstudio": {"base_url": "http://localhost:1234/v1", "api_key": ""},
    "local": {"base_url": "http://localhost:8080/v1", "api_key": ""},
}

DEFAULTS = {
    "bundle_dir": "./okf_bundle",
    "llm": {
        "enabled": False,
        "provider": "local",
        "base_url": "http://localhost:8080/v1",
        "model": "local-model",
        "api_key": "",
        "max_workers": 2,
        "max_tokens": 2000,
    },
    "providers": dict(BUILTIN_PROVIDERS),
    "enrich": {
        "description": {"model": "", "max_workers": 2},
        "deep": {"enabled": False, "model": "", "max_workers": 2},
        "security": {"enabled": False, "model": "", "max_workers": 2},
        "semantic_related": {"enabled": False, "max_workers": 2},
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
    import copy
    cfg = copy.deepcopy(DEFAULTS)

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
    """Dot-notation get: cfg['llm.base_url'] → cfg['llm']['base_url'].
    Supports arbitrary depth: cfg['enrich.deep.provider'] → cfg['enrich']['deep']['provider']."""
    parts = key.split(".")
    current = cfg
    for part in parts:
        if not isinstance(current, dict):
            return default
        current = current.get(part)
        if current is None:
            return default
    return current


def resolve_provider(cfg: dict, mode: str) -> dict:
    """Resolve provider config for an enrich mode.

    Resolution cascade:
      1. enrich.{mode}.provider      — per-mode provider override
      2. llm.provider                — global provider
      3. "local"                     — fallback

    Returns dict with keys: provider, base_url, model, api_key, max_workers, max_tokens
    """
    provider = _get(cfg, f"enrich.{mode}.provider") or _get(cfg, "llm.provider", "local")
    prov_cfg = _get(cfg, f"providers.{provider}", {})
    return {
        "provider": provider,
        "base_url": (
            _get(cfg, f"enrich.{mode}.base_url")
            or prov_cfg.get("base_url")
            or _get(cfg, "llm.base_url", "http://localhost:8080/v1")
        ),
        "model": (
            _get(cfg, f"enrich.{mode}.model")
            or prov_cfg.get("model")
            or _get(cfg, "llm.model", "local-model")
        ),
        "api_key": (
            _get(cfg, f"enrich.{mode}.api_key")
            or prov_cfg.get("api_key")
            or _get(cfg, "llm.api_key", "")
        ),
        "max_workers": int(
            _get(cfg, f"enrich.{mode}.max_workers")
            or _get(cfg, "llm.max_workers", 2)
        ),
        "max_tokens": int(
            _get(cfg, f"enrich.{mode}.max_tokens")
            or _get(cfg, "llm.max_tokens", 2000)
        ),
    }


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
