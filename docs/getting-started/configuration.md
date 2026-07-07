# Configuration

okf-generator uses a project-level `.okfconfig` file for settings. No environment variables are needed — everything goes through the config file.

## Quick start

```bash
# View current config
okf config

# Set a value
okf config llm.base_url=http://localhost:8080/v1

# Run the setup wizard
okf init
```

## Config file location

okf-generator looks for `.okfconfig` in the current directory, then walks up to the parent directories. The file uses JSON format:

```json
{
  "llm": {
    "base_url": "http://localhost:8080/v1",
    "model": "gemma-3-4b-it-qat:Q4_0",
    "max_workers": 2
  },
  "serve": {
    "port": 8000,
    "host": "127.0.0.1"
  },
  "lookup": {
    "bundle": "./okf_bundle"
  }
}
```

## Section reference

### `llm.*` — LLM enrichment settings

| Key | Default | Description |
|-----|---------|-------------|
| `llm.base_url` | `http://localhost:8080/v1` | OpenAI-compatible endpoint |
| `llm.model` | `gemma-3-4b-it-qat:Q4_0` | Model name |
| `llm.api_key` | — | API key (set via env `OKF_API_KEY` or here) |
| `llm.max_workers` | `2` | Parallel enrichment workers |

### `llm.providers.*` — Named provider presets

Built-in providers: `local`, `openai`, `anthropic`, `deepseek`, `gemini`, `ollama`, `lmstudio`, `openrouter`, `dashscope`, `minimax`.

```json
{
  "llm": {
    "providers": {
      "anthropic": { "base_url": "https://api.anthropic.com/v1" },
      "deepseek": { "base_url": "https://api.deepseek.com/v1" }
    }
  }
}
```

### `enrich.*` — Enrichment mode routing

Each mode resolves its own provider independently:

```json
{
  "enrich": {
    "description": { "provider": "local", "model": "gemma-3-4b-it-qat:Q4_0" },
    "deep": { "enabled": true, "provider": "deepseek", "model": "deepseek-chat" },
    "security": { "enabled": true, "provider": "anthropic" },
    "semantic_related": { "enabled": false }
  }
}
```

Resolution cascade: `enrich.{mode}.{key}` → `providers.{name}.{key}` → `llm.{key}`.

### `serve.*` — Dashboard / viz server

| Key | Default | Description |
|-----|---------|-------------|
| `serve.port` | `8000` | HTTP port |
| `serve.host` | `127.0.0.1` | Bind address |

### `lookup.*` — Concept lookup defaults

| Key | Default | Description |
|-----|---------|-------------|
| `lookup.bundle` | `./okf_bundle` | Default bundle path |

## Environment variables

For CI/CD or ephemeral environments, you can use `OKF_API_KEY` as a fallback — the config file takes precedence when set.

## Config file precedence

1. `.okfconfig` in current directory
2. `.okfconfig` in parent directories (walking up)
3. Built-in defaults
