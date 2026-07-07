# LLM Enrichment

okf-generator supports optional LLM-powered enrichment to enhance concept descriptions, add usage examples, audit security, and find semantic cross-links.

!!! tip "Privacy first"
    The default mode is `base` — it never sends source code to an LLM, only improves existing descriptions and docstrings. Modes `deep`, `security`, and `full` send source code and require explicit opt-in via `--mode`.

## Quick start

```bash
# Enrich at generate time
okf generate --enrich deep

# Or enrich an existing bundle (no re-scan needed)
okf enrich --mode full
```

---

## Enrichment modes

| Mode | What it does | Source body needed? | LLM call? |
|------|-------------|:---:|:---:|
| `base` | Improves descriptions + docstrings (Google-style) | ❌ | Yes |
| `deep` | Adds usage examples, side effects, security notes, complexity estimates | ✅ | Yes |
| `security` | Audits existing bundle for visible risk patterns only | ✅ | Yes |
| `full` | All of the above + semantic related-links | ✅ | Yes |

### `base` — Description improvement

Improves existing descriptions and docstrings to Google-style format. Does **not** read the source body — only improves what's already in the bundle.

**What gets enriched:**
- `description` — rewritten to be more concise and informative
- `docstring` — reformatted with consistent style
- `design_pattern` — pattern detected from signature (e.g., "Factory", "Singleton")
- `tags` — LLM-suggested semantic tags merged and deduplicated

**Example — before:**
```yaml
description: "A function to add two numbers."
```

**Example — after:**
```yaml
description: "Adds two integers and returns the sum."
tags:
  - lang:python
  - type:Function
  - domain:math
  - pattern:utility
```

### `deep` — Source-aware enrichment

Reads the actual source body via `source_lines` to produce detailed fields.

**What gets enriched:**
- `usage_example` — realistic code example showing how to call the function/class
- `side_effects` — describes any side effects (I/O, mutation, network calls)
- `security` — flags visible risk patterns
- `complexity` — estimated complexity (e.g., O(n), "moderate")

**Example — after deep enrichment:**
```yaml
usage_example: |
  connector = WorldBankConnector(api_key="sk-...")
  df = connector.fetch_series("NY.GDP.MKTP.CD", start_date, end_date)
side_effects:
  - "Makes HTTP request to api.worldbank.org"
  - "Raises requests.HTTPError on non-2xx response"
complexity: O(n) where n = number of days in the date range
```

### `security` — Risk audit

Audits concepts for visible risk patterns in the source body.

**What gets enriched:**
- `security` — risk assessment (e.g., "SQL injection risk: raw string concatenation detected")
- `deprecation_notes` — deprecation notices found in docstring or decorators (deterministic, no LLM needed)

**Example — after security audit:**
```markdown
## Security ⚠️ AI-estimated — verify manually
- SQL injection risk: raw string concatenation detected in `query` parameter
- No input validation on `user_id`

## Deprecation
Use `fetch_series_v2` instead — this method is deprecated.
```

### `full` — All passes

Runs `base` + `deep` + `security`, plus a semantic related-links pass:

- `related_semantic` — LLM-suggested cross-links beyond the call graph (e.g., conceptually similar functions in different modules)

---

## When to use which mode

| Use case | Recommended mode | Why |
|----------|-----------------|-----|
| You just want cleaner docs descriptions | `base` | No source code sent to LLM, fastest, resumable |
| You want usage examples and complexity estimates for a library you're documenting | `deep` | Reads source body — good for public docs where accuracy matters |
| You're auditing a codebase for visible risk patterns before a security review | `security` | Flags SQL injection, hardcoded secrets, unsafe `eval()` patterns |
| You're preparing a bundle for an AI agent and want the richest possible context | `full` | Runs all passes + semantic cross-links between related modules |
| You're in CI and want to enrich incrementally | `base` (CI safe) | `deep`/`security` need source body which may not be available in CI |

**Rule of thumb:** Start with `base`. Add `deep` or `security` only when you need the specific fields they provide and have verified the LLM provider is acceptable for your codebase.

---

## Fields reference

| Field | Appears in | Description |
|-------|-----------|-------------|
| `description` | Frontmatter | Improved short description |
| `docstring` | Body | Reformatted docstring |
| `design_pattern` | Body | Detected design pattern |
| `tags` | Frontmatter | Merged LLM-suggested tags |
| `usage_example` | Body | Code example from deep pass |
| `side_effects` | Body | Side effects from deep pass |
| `complexity` | Body | Complexity estimate from deep pass |
| `security` | Body | Risk patterns from security pass |
| `deprecation_notes` | Body | Deprecation detection (deterministic) |
| `related_semantic` | Body | AI-suggested cross-links from full pass |

---

## Resumable execution

All modes are resumable — already-enriched concepts are skipped on re-run:

```bash
# Run base enrichment
okf enrich --mode base

# Interrupt mid-way (Ctrl+C), then resume — already-done concepts are skipped
okf enrich --mode deep

# Force re-run all concepts
okf enrich --mode full --force
```

---

## Multi-provider routing

Each enrich mode resolves its own provider independently via:

```
enrich.{mode}.{key} → providers.{name}.{key} → llm.{key}
```

Example — route cheap description work to a local model, security audits to Anthropic:

```json
{
  "enrich": {
    "description": { "provider": "local", "model": "gemma-3-4b-it-qat:Q4_0" },
    "deep": { "enabled": true, "provider": "deepseek", "model": "deepseek-chat" },
    "security": { "enabled": true, "provider": "anthropic" }
  }
}
```

Built-in providers: `local`, `openai`, `anthropic`, `deepseek`, `gemini`, `ollama`, `lmstudio`, `openrouter`, `dashscope`, `minimax`.

## Configuration

```bash
okf config llm.base_url=http://localhost:8080/v1
okf config llm.api_key=sk-...
```

See [Configuration](../getting-started/configuration.md) for full details.

## How it works

1. Enrichment runs after initial scanning
2. Already-enriched concepts are skipped (resumable)
3. Each mode resolves its provider independently via the cascade
4. Fields are appended to concept files — original data is preserved
