# Enrichment

okf-generator supports two enrichment layers that enhance an existing OKF bundle
without re-scanning the source:

1. **LSP enrichment** (`okf enrich --lsp`) — deterministic, free, uses local language servers to resolve precise caller/callee edges, interface implementations, and external dependency traces.
2. **LLM enrichment** (`okf enrich --llm`) — optional, configurable model, adds human-readable descriptions, usage examples, security notes, and semantic cross-links.

They compose: run `okf enrich --lsp --llm` to get compiler-accurate call graphs
*plus* AI-generated summaries (see LSP → LLM below).

!!! tip "Privacy first"
    In the LLM layer, the default mode is `base` — it never sends source code to an LLM, only improves existing descriptions and docstrings. Modes `deep`, `security` send source code and require explicit opt-in via `--mode`.

---

# LSP Enrichment

Language Server Protocol (LSP) enrichment uses the language servers already
installed on the developer's machine (e.g. `pyright-langserver`, `gopls`,
`rust-analyzer`) to resolve **compiler-accurate** call graphs.  It runs
alongside — never instead of — the tree-sitter linker.

## Quick start

```bash
# LSP enrichment only (fast, free, deterministic)
okf enrich --lsp

# Or combined with LLM for full depth
okf enrich --lsp --llm --mode deep
```

## How it works

1. `okf enrich --lsp` scans the bundle for source file extensions
2. For each language, it checks `$PATH` for the corresponding LSP server
3. If found, it spawns the server as a headless stdio subprocess
4. It queries `textDocument/references` and `textDocument/definition` for every
   Function / Class / Method concept
5. LSP results are mapped back to concept IDs via the concept's `source_lines`
   range and written into the bundle

## Requirements

The LSP binary for each language must be on `$PATH`:

| Language | Server | Status | Install |
|----------|--------|--------|---------|
| Python | `pyright-langserver` | ✅ Verified | `pip install pyright` |
| Go | `gopls` | ✅ Verified | `go install golang.org/x/tools/gopls@latest` (needs `$GOPATH/bin` on `$PATH`) |
| Rust | `rust-analyzer` | ✅ Verified | `rustup component add rust-analyzer` |
| TypeScript / JS | `typescript-language-server` | ✅ Verified | `npm install -g typescript-language-server` + `typescript` in workspace |

All 4 servers have been verified against real source files using `okf lsp resolve`. New servers can be added by extending `okf/enrich/_lsp_map.py`.

New language servers are added by extending `okf/enrich/_lsp_map.py` — one entry per extension. The mapping convention mirrors the parser plugin system.

## What gets enriched

LSP enrichment updates the **Relationship table** in each concept's bundle file:

- `called_by` — precise list of callers, resolved via LSP references
- `calls` — precise list of callees (existing tree-sitter linker data is
  preserved where LSP cannot resolve)

Unlike LLM enrichment, LSP enrichment is **deterministic** — same code →
same output, every run.  Zero token cost.

## Inspecting available servers

```bash
okf lsp status
```

Shows which LSP binaries are found on `$PATH`:

```
  Lang           Ext    Status     Binary
  ----           ---    ------     ------
  python         .py    ✓ installed pyright-langserver
  go             .go    ✗ missing  gopls
  rust           .rs    ✓ installed rust-analyzer
  typescript     .ts    ✗ missing  typescript-language-server
```

## Testing a single resolution

```bash
okf lsp resolve src/server/handler.py:42:5
```

Initiates a one-shot LSP session, connects to the appropriate server, and
returns the definition and references for the symbol at that location.

## LSP → LLM enrichment order

When both `--lsp` and `--llm` are enabled, LSP always runs first.  The compiler
facts it resolves (exact callers, interface implementations, external dependency
paths) are written into the bundle before the LLM pass starts, so the LLM
prompts receive precise structural context — reducing hallucination and
token waste.

---

# LLM Enrichment

Optional LLM-powered enrichment to enhance concept descriptions, add usage
examples, audit security, and find semantic cross-links.

## Quick start

```bash
# LLM enrichment only (base mode, no source code sent)
okf enrich --llm

# Or with a specific mode
okf enrich --llm --mode deep

# Combined with LSP for maximum accuracy
okf enrich --full
```

## Targeting specific concepts

By default enrichment runs on all eligible concepts in the bundle. Use `--file`
or `--concept` to target specific ones:

```bash
# Enrich only concepts from a specific source file
okf enrich --file src/utils/helpers.py --mode deep

# Enrich a single concept by ID
okf enrich --concept utils/slugify --mode security
```

Both filters use substring matching against the concept's resource path or
concept ID.

## Enrichment modes

| Mode | What it does | Source body needed? | LLM call? |
|------|-------------|:---:|:---:|
| `base` | Improves descriptions + docstrings (Google-style) | ❌ | Yes |
| `deep` | Adds usage examples, side effects, security notes, complexity estimates | ✅ | Yes |
| `security` | Audits existing bundle for visible risk patterns only | ✅ | Yes |

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

## Token usage

Both `okf enrich` and `okf generate --enrich` log token consumption at completion:

```
# From okf enrich
Enrich complete: 11 done, 0 errors | Tokens: 4850 total (3200 prompt + 1650 completion) | 1200 reasoning

# From okf generate --enrich
Enrichment complete: 11 enriched, 0 errors, 0 skipped | Tokens: 4850 total ...
```

This shows total prompt tokens, completion tokens, and reasoning tokens (for reasoning models like DeepSeek). All concepts in a single run are aggregated into one report.

## Controlling token usage

Set `llm.max_tokens` in `.okfconfig` to cap tokens per LLM call:

```json
{
  "llm": {
    "max_tokens": 1000
  }
}
```

Default is 2000. Lower values reduce cost and speed up processing, but may truncate enriched fields. Per-mode overrides are also supported via `enrich.{mode}.max_tokens`.

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

## Time and cost estimates

Enrichment speed depends on your LLM provider and model. These are rough estimates per 100 concepts:

| Mode | Local LLM (gemma-3-4b) | Cloud API (DeepSeek) | Cloud API (GPT-4o) |
|------|----------------------|---------------------|-------------------|
| `base` | ~2–5 min | ~30 sec | ~1 min |
| `deep` | ~5–10 min | ~2–3 min | ~3–5 min |
| `security` | ~5–10 min | ~2–3 min | ~3–5 min |
| `full` | ~10–20 min | ~5–8 min | ~8–12 min |

**Cost notes:**
- **Local LLM** — free (runs on your machine via Ollama, llama.cpp, etc.)
- **DeepSeek** — ~$0.01–0.03 per 100 concepts (base mode)
- **Anthropic/GPT** — ~$0.05–0.15 per 100 concepts depending on mode
- `base` mode is cheapest (smaller prompts, no source body)
- `deep` and `security` include source body in prompts → ~3–5x more tokens per call

## FAQ

**Does enrichment send my code to a third party?**
`base` mode never reads source code — only metadata already in the bundle. `deep`, `security`, and `full` read the source body and send it to the configured LLM provider. Check your provider's data policy before using these modes on proprietary code.

**Can I run enrichment without an API key?**
`okf enrich` without a configured LLM silently skips all concepts. Core extraction (`okf generate`) never requires an API key.

**What happens if I interrupt enrichment mid-way?**
Enrichment is resumable — already-processed concepts are skipped on re-run. Use `--force` to re-process everything.

**Why is my local LLM slower than cloud?**
Local models run on your hardware. Gemma-3-4B on a MacBook processes ~5–15 concepts per minute. For production workloads, consider a cloud provider or a faster local model.

**Does deep enrichment modify my source code?**
No. Enrichment only modifies the bundle files (`.md` in the bundle directory). Your source code is never altered.

**How do I know which concepts have been enriched?**
Check the concept file — if it has `## Usage Example`, `## Side Effects`, `## Security`, or `## Complexity` sections, deep enrichment has run. The `description` field in frontmatter is also enhanced by base enrichment.

## How it works

1. Enrichment runs after initial scanning
2. Already-enriched concepts are skipped (resumable)
3. Each mode resolves its provider independently via the cascade
4. Fields are appended to concept files — original data is preserved
