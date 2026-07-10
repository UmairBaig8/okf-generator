---
name: okf-generator
description: >
  Generate OKF (Open Knowledge Format) v0.1 knowledge bundles from codebases,
  and look up exact concepts for AI agent context injection. Use this skill
  whenever the user wants to: index a codebase, generate OKF bundles, extract
  code knowledge into structured markdown, convert codebases into training data,
  look up functions/classes/modules by name, prime an AI agent with codebase
  context, integrate codebase knowledge with OpenCode or other AI coding agents,
  or run okf_generator.py / okf_lookup.py / okf_to_pairs.py. Also trigger for
  phrases like "index my code", "generate knowledge bundle", "extract codebase
  concepts", "what does X class do", or "look up X in OKF".
---

# OKF Generator & Lookup Skill

Generates structured OKF v0.2 knowledge bundles from codebases (Python, JS/TS,
Go, Java, Rust, Ruby via tree-sitter AST), and provides fast concept lookup for
AI agents like OpenCode.

## Pipeline Overview

```
codebase
   |
   v
okf generate  -->  okf_bundle/          (domain/resource-path layout)
                       |
                okf lookup               (zero-LLM concept search)
                       |
                okf pairs          -->  okf_pairs.jsonl  (training data)
```

## CLI Reference

All features via single `okf` CLI (installed from PyPI).

| Command | Purpose |
|---------|---------|
| `okf generate` | Scan codebase and write OKF bundle |
| `okf lookup` | Search bundle and return exact concept |
| `okf pairs` | Convert bundle to JSONL training pairs |
| `okf summarize` | Regenerate SUMMARY.md from existing bundle |

## Dependencies

```bash
pip install okf-generator
# With LLM enrichment:
pip install "okf-generator[llm]"
```

---

## Task: Generate OKF Bundle

**When**: user says "index my codebase", "generate OKF bundle", "extract knowledge from code"

### Static extraction (no LLM — always run this first)
```bash
okf generate <source_dir> <output_dir>
```

### With LLM enrichment (fills missing docstrings and descriptions)
```bash
OKF_ENRICH=1 \
OKF_BASE_URL="http://localhost:8080/v1" \
OKF_API_KEY="llamabarn" \
OKF_MODEL="ggml-org/gemma-3-4b-it-qat-GGUF:Q4_0" \
OKF_MAX_WORKERS=2 \
okf generate <source_dir> <output_dir>
```

Enrichment is **resumable** — rerun safely if interrupted. Already-enriched
concepts are skipped automatically (checks disk on every run).

### Key env vars (enrichment only)

| Var | Default | Purpose |
|-----|---------|---------|
| `OKF_ENRICH` | `0` | Set `1` to enable LLM enrichment |
| `OKF_BASE_URL` | `https://api.anthropic.com/v1` | OpenAI-compat endpoint |
| `OKF_API_KEY` | `` | API key |
| `OKF_MODEL` | `claude-sonnet-4-6` | Enrichment model |
| `OKF_MAX_WORKERS` | `2` | Parallel workers (keep low for local LLMs) |

### Output layout (mirrors source tree)
```
okf_bundle/
├── SUMMARY.md              <- bird's-eye view for AI agents
├── index.md                <- root index
├── log.md                  <- generation history
└── <domain>/
    └── <module>/
        ├── index.md        <- lists all concepts in folder
        ├── <module>.md     <- Module concept
        └── <ClassName>.md  <- Class / Function concepts
```

---

## Task: Look Up a Concept

**When**: user asks "what does X do", "find class X", "look up X", or needs to
prime OpenCode with exact concept context before editing code.

```bash
# Full detail — signature, docstring, params, returns, related
okf lookup WorldBankConnector

# All concepts from one source file
okf lookup --file StockAI/RnD/python/connectors/economic_data.py

# Filter by type
okf lookup --type Class connector

# Filter by tag
okf lookup --tag lang:python --tag type:Function fetch

# Compact list (many results)
okf lookup --compact connector

# JSON output (programmatic / agent use)
okf lookup --json WorldBankConnector

# Custom bundle path
okf lookup --bundle ./Knowlege/okf_bundle WorldBankConnector
```

Default bundle path: `./okf_bundle`. Also auto-tries `./Knowlege/okf_bundle`
and `./knowledge/okf_bundle`.

---

## Task: Generate Training Pairs

**When**: user wants JSONL training data from the OKF bundle.

```bash
# Static only (instant, no LLM)
SKIP_SYNTH=1 okf pairs <bundle_dir> output.jsonl

# With LLM (QA, doc, summarize pairs)
SYNTH_BASE_URL="http://localhost:8080/v1" \
SYNTH_API_KEY="llamabarn" \
SYNTH_MODEL="ggml-org/gemma-3-4b-it-qat-GGUF:Q4_0" \
MAX_WORKERS=2 \
QA_PER_CONCEPT=3 \
okf pairs <bundle_dir> output.jsonl

# Specific pair types only
PAIR_TYPES="codegen,qa" okf pairs <bundle_dir> output.jsonl
```

### Pair types

| Type | Static | LLM | Covers |
|------|--------|-----|--------|
| `codegen` | yes | yes | Functions, Classes |
| `qa` | no | yes | All (purpose/params/return/edge) |
| `doc` | no | yes | Functions, Classes |
| `summarize` | yes | yes | Modules, Classes |
| `crosslink` | yes | no | All with related concepts |

---

## Task: Regenerate SUMMARY.md Only

```bash
okf summarize <bundle_dir>
```

Use after enrichment finishes to refresh the summary without re-scanning.

---

## OpenCode Integration

See `references/opencode-integration.md` for full setup.

Quick setup:
```bash
# 1. Add to AGENTS.md (auto-loaded by OpenCode)
echo "OKF bundle at ./okf_bundle — use: okf lookup <Name>" >> AGENTS.md

# 2. Add lookup command
mkdir -p .opencode/commands
echo "RUN okf lookup --bundle ./okf_bundle \$NAME" \
  > .opencode/commands/lookup.md
```

---

## Supported Languages

| Language | Parser | Extracts |
|----------|--------|---------|
| Python | stdlib ast | functions, classes, params, return types, docstrings |
| JS / TS | tree-sitter | functions, arrow fns, classes, JSDoc |
| Go | tree-sitter | funcs, methods, structs, interfaces, GoDoc |
| Java | tree-sitter | classes, methods, constructors, Javadoc |
| Rust | tree-sitter | fns, structs, enums, traits, impl blocks, doc comments |
| Ruby | tree-sitter | defs, classes, modules, hash comments |

---

## Troubleshooting

**No concepts found**: Check that source dir is not inside a SKIP_DIRS name
(node_modules, .venv, dist, etc). Leading path components like `/tmp` are
no longer skipped (fixed in v0.1.3).

**Enrichment slow**: Use `OKF_MAX_WORKERS=1`. Local models process ~1 request
at a time. At 32 tok/sec expect ~3-5s per concept.

**Enrichment interrupted**: Rerun same command. Enriched files are skipped.

**JS/TS concepts missing**: Ensure tree-sitter-typescript is installed.
TypeScript uses a separate grammar from JavaScript.

**Lookup wrong result**: Add --type or --file to narrow the search scope.
