# LLM Enrichment

okf-generator supports optional LLM-powered enrichment to enhance concept descriptions, add usage examples, audit security, and find semantic cross-links.

!!! tip "Privacy first"
    The default mode is `base` — it never sends source code to an LLM, only improves existing descriptions and docstrings. Modes `deep`, `security`, and `full` send source code and require explicit opt-in via `--mode`.

## Quick start

```bash
# Enrich at generate time
okf generate ./my_project ./okf_bundle --enrich deep

# Or enrich an existing bundle (no re-scan needed)
okf enrich --mode full
```

## Enrichment modes

| Mode | What it does | Needs source body? |
|------|-------------|:---:|
| `base` | Improves descriptions + docstrings (Google-style) | ❌ |
| `deep` | Adds usage examples, side effects, security notes, complexity estimates | ✅ |
| `security` | Audits existing bundle for visible risk patterns only | ✅ |
| `full` | All of the above + semantic related-links | ✅ |

## Multi-provider routing

Each enrich mode can use a different provider:

```json
{
  "enrich": {
    "description": { "provider": "local", "model": "gemma-3-4b-it-qat:Q4_0" },
    "deep": { "enabled": true, "provider": "deepseek", "model": "deepseek-chat" },
    "security": { "enabled": true, "provider": "anthropic" }
  }
}
```

Built-in provider presets: `local`, `openai`, `anthropic`, `deepseek`, `gemini`, `glm`, `ollama`, `lmstudio`, `openrouter`, `dashscope`, `minimax`.

## Configuration

Set provider settings in `.okfconfig`:

```bash
okf config llm.base_url=http://localhost:8080/v1
okf config llm.api_key=sk-...
```

See [Configuration](../getting-started/configuration.md) for full details.

## How it works

1. The enrichment pass runs after initial scanning
2. Already-enriched concepts are skipped (resumable — interrupt and rerun freely)
3. Each mode resolves its provider independently via the cascade
4. `body_extra` fields are appended to concept files
