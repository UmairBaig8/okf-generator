# Configuration

okf-generator runs out of the box with zero config. This page covers everything you can tune.

Precedence (highest to lowest): **CLI flags > `.okfconfig` > built-in defaults**.

## `.okfconfig` file

Place a `.okfconfig` file (JSON) at your project root. okf-generator auto-detects it from the current directory, walking up to parent directories.

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
    "bundle": "./okf_bundle",
    "limit": 10
  }
}
```

None of these sections are required — omit anything to leave it at default.

## All config keys

### `llm.*` — LLM enrichment

| Key | Default | Description |
|-----|---------|-------------|
| `llm.enabled` | `false` | Enable enrichment |
| `llm.provider` | `"local"` | Provider name (`local`, `openai`, `anthropic`, `deepseek`, `gemini`, `ollama`, `lmstudio`, `openrouter`, `dashscope`, `minimax`) |
| `llm.base_url` | `"http://localhost:8080/v1"` | OpenAI-compatible endpoint |
| `llm.model` | `"local-model"` | Model name |
| `llm.api_key` | `""` | API key |
| `llm.max_workers` | `2` | Parallel enrichment workers |
`llm.max_tokens` | `2000` | Max tokens per LLM call (covers cost, shorter = cheaper) |

### `providers.*` — Named provider presets

Built-in providers with default `base_url` values:

```json
{
  "providers": {
    "anthropic": { "base_url": "https://api.anthropic.com/v1" },
    "openai": { "base_url": "https://api.openai.com/v1" },
    "deepseek": { "base_url": "https://api.deepseek.com/v1" },
    "gemini": { "base_url": "https://generativelanguage.googleapis.com/v1" },
    "ollama": { "base_url": "http://localhost:11434/v1" },
    "lmstudio": { "base_url": "http://localhost:1234/v1" },
    "openrouter": { "base_url": "https://openrouter.ai/api/v1" },
    "dashscope": { "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1" },
    "minimax": { "base_url": "https://api.minimax.chat/v1" },
    "local": { "base_url": "http://localhost:8080/v1" }
  }
}
```

### `enrich.*` — Per-mode provider routing

Each enrichment mode resolves its own provider independently. Cascade: `enrich.{mode}.{key}` → `providers.{name}.{key}` → `llm.{key}`.

| Key | Default | Description |
|-----|---------|-------------|
| `enrich.description.model` | `""` | Model for description enrichment (inherits `llm.model`) |
| `enrich.description.max_workers` | `2` | Workers for description pass |
| `enrich.deep.enabled` | `false` | Enable deep enrichment (usage examples, side effects) |
| `enrich.deep.model` | `""` | Model for deep enrichment |
| `enrich.deep.max_workers` | `2` | Workers for deep pass |
| `enrich.security.enabled` | `false` | Enable security audit |
| `enrich.security.model` | `""` | Model for security audit |
| `enrich.security.max_workers` | `2` | Workers for security pass |
| `enrich.semantic_related.enabled` | `false` | Enable semantic related-link discovery |
| `enrich.semantic_related.max_workers` | `2` | Workers for related-link pass |

### `serve.*` — Dashboard / viz server

| Key | Default | Description |
|-----|---------|-------------|
| `serve.port` | `8000` | HTTP port |
| `serve.host` | `"127.0.0.1"` | Bind address |

### `lookup.*` — Search defaults

| Key | Default | Description |
|-----|---------|-------------|
| `lookup.bundle` | `"./okf_bundle"` | Default bundle path |
| `lookup.limit` | `10` | Default max results |
| `lookup.min_score` | `0.1` | Minimum relevance score |

### `mcp.*` — MCP server

| Key | Default | Description |
|-----|---------|-------------|
| `mcp.port` | `0` | Port (0 = stdio mode) |

### `pairs.*` — Training data export

| Key | Default | Description |
|-----|---------|-------------|
| `pairs.output_file` | `"./okf_pairs.jsonl"` | Output path |
| `pairs.qa_per_concept` | `3` | QA pairs per concept |
| `pairs.max_workers` | `3` | Parallel workers |
| `pairs.pair_types` | `"codegen,qa,doc,summarize,crosslink"` | Enabled pair types |

### Global defaults

| Key | Default | Description |
|-----|---------|-------------|
| `bundle_dir` | `"./okf_bundle"` | Default output directory |

## Using the CLI

```bash
# View current config (merged)
okf config

# Set a value
okf config llm.base_url=http://localhost:8080/v1

# Run setup wizard
okf init
```

## Example: multi-provider routing

Route cheap description work to a local model and security audits to a cloud model:

```json
{
  "llm": { "provider": "local", "base_url": "http://localhost:8080/v1" },
  "enrich": {
    "description": { "provider": "local", "model": "gemma-3-4b-it-qat:Q4_0" },
    "deep": { "enabled": true, "provider": "deepseek", "model": "deepseek-chat" },
    "security": { "enabled": true, "provider": "anthropic" }
  }
}
```

## Config file locations

okf-generator checks these paths in order (later files override earlier ones):

1. Built-in defaults
2. `.okfconfig` in current directory (walks up to parent dirs)
3. `~/.config/okf/config.json` (user-level global defaults)

## Validating config

```bash
okf config
```
