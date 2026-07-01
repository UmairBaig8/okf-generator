[![okf-generator banner](https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/banner_v2.svg)](https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/banner_v2.svg)

[![PyPI version](https://img.shields.io/pypi/v/okf-generator?style=flat-square&label=PyPI)](https://pypi.org/project/okf-generator/)
[![Downloads](https://img.shields.io/pypi/dm/okf-generator?style=flat-square)](https://pypi.org/project/okf-generator/)
[![Python](https://img.shields.io/pypi/pyversions/okf-generator?style=flat-square)](https://pypi.org/project/okf-generator/)
[![Tests](https://img.shields.io/github/actions/workflow/status/UmairBaig8/okf-generator/ci.yml?style=flat-square&label=tests)](https://github.com/UmairBaig8/okf-generator/actions)
[![Last commit](https://img.shields.io/github/last-commit/UmairBaig8/okf-generator?style=flat-square)](https://github.com/UmairBaig8/okf-generator/commits/main)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](https://github.com/UmairBaig8/okf-generator/blob/main/LICENSE)
[![OKF v0.1](https://img.shields.io/badge/OKF-v0.1-7c3aed?style=flat-square)](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill-orange?style=flat-square&logo=anthropic)](https://github.com/UmairBaig8/okf-generator/blob/main/SKILL.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](https://github.com/UmairBaig8/okf-generator/blob/main/CONTRIBUTING.md)
[![Agents](https://img.shields.io/badge/okf_install-6_agents-4ade80?style=flat-square)](README.md#agent-installation)

**Index any codebase into a structured OKF v0.1 knowledge bundle — then look up exact concepts for any AI coding agent.**

[Why this exists](#why-this-exists) ·
[Demo](#demo) ·
[Installation](#installation) ·
[Quick Start](#quick-start) ·
[How it compares](#how-it-compares) ·
[CLI Reference](#cli-reference) ·
[AI Agent Integration](#ai-agent-integration) ·
[FAQ](#faq) ·
[Contributing](#contributing) ·
[Acknowledgments](#acknowledgments)

---

## Why this exists

[#why-this-exists](#why-this-exists)

AI coding agents waste enormous amounts of context re-reading entire files to find one function, class, or dependency version. Ask an agent *"what does `WorldBankConnector` do?"* and it either guesses from a stale memory of your codebase, or burns thousands of tokens reading the whole file to find a 12-line answer.

`okf-generator` solves this by converting your source code into the [Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) (OKF) v0.1 — a knowledge-representation spec [introduced by Google Cloud](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) in June 2026 ([full v0.1 spec](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)) — a directory of small, structured markdown files, one per concept (function, class, module, dependency). An agent then asks a surgical question and gets a surgical answer:

```
# Before touching WorldBankConnector, look it up
okf lookup WorldBankConnector

# CLASS: WorldBankConnector
# Source      : StockAI/RnD/python/connectors/economic_data.py  line 51
# Description : Fetches World Bank development indicators via wbdata API.
# Methods     : get_indicator, search
# Signature   : class WorldBankConnector
```

No re-reading the file. No guessing. No LLM call required to get the answer.

![Before and after comparison](https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/before_after.svg)

## Demo

[#demo](#demo)

<!--
  Record with vhs (https://github.com/charmbracelet/vhs) or terminalizer and
  drop the GIF here. A 10-15s loop showing:
    1. okf generate ./my_project ./okf_bundle
    2. okf lookup WorldBankConnector
    3. okf lookup --type Dependency --tag ecosystem:pip
  converts far better than static text — most visitors decide whether to
  keep reading based on whether they can SEE it work.
-->
![demo](https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/demo.gif)

## How it compares

[#how-it-compares](#how-it-compares)

The OKF ecosystem is moving fast — here's where `okf-generator` sits relative to other producers:

| | **okf-generator** | Other OKF producers |
| --- | --- | --- |
| Language coverage | 7 languages (Python, JS/TS, Go, Java, Rust, Ruby, SQL) | Usually 1 language or doc-only |
| Cross-reference linking | Imports → dependencies, function calls → caller/callee across all languages | Not typically supported |
| Dependency/manifest parsing | 12 formats (pip, npm, cargo, go, maven, gradle, composer, rubygems, swiftpm, clojars, hex, +1) | Not typically supported |
| Extraction | Zero-LLM, deterministic, offline | Often LLM-required for every concept |
| Optional enrichment | Any OpenAI-compatible endpoint (Claude, local llama.cpp, Ollama) | Often locked to one vendor |
| Training data export | Built-in JSONL pair generator (5 pair types) | Not typically included |
| Agent compatibility | Any agent that can run a CLI (Claude Code, Cursor, Windsurf, Copilot, OpenCode, Cline) | Often single-agent focused |

If you're choosing between OKF producers: pick `okf-generator` when you want broad language + dependency coverage with zero mandatory LLM cost, and you want the bundle to double as a fine-tuning data source.

## Used by / Built for

[#used-by--built-for](#used-by--built-for)

`okf-generator` was originally built to index a large, multi-domain codebase (`StockAI`/`TrainLLMs`) spanning Python data connectors, ML pipelines, and SQL schemas — the kind of project where giving an agent the *whole* repo as context is both slow and unaffordable in tokens. If you're working in a sprawling codebase and tired of re-explaining your own code to your AI agent every session, this is the tool that problem was built to solve.

## Installation

[#installation](#installation)

**One-liner — paste into any terminal:**

```bash
curl -fsSL https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/scripts/install.sh | bash
```

This installs `okf-generator[llm]` + the Claude Code skill in one shot.
*Requirements: Python 3.11+ with pip.*

Or manually:

```bash
# Core (extraction only — no LLM required)
pip install okf-generator

# With LLM enrichment + training pair generation
pip install "okf-generator[llm]"
```

## Quick Start

[#quick-start](#quick-start)

```bash
# 1. Generate a knowledge bundle from your codebase
okf generate ./my_project ./okf_bundle

# 2. Look up a concept (works instantly, zero LLM)
okf lookup WorldBankConnector

# 3. Find all concepts from one file
okf lookup --file src/connectors/economic_data.py

# 4. List all dependencies for a given ecosystem
okf lookup --type Dependency --tag ecosystem:pip

# 5. Generate training pairs from the bundle
okf pairs ./okf_bundle ./train.jsonl

# 6. Regenerate SUMMARY.md after enrichment
okf summarize ./okf_bundle
```

## How it works

[#how-it-works](#how-it-works)

<!--- Mermaid diagram — renders on GitHub, not on PyPI --->
```mermaid
flowchart LR
    A[Your codebase] -->|okf generate| B[Scanners: AST / tree-sitter / regex]
    B --> C[Concepts: Function / Class / Module / Dependency]
    C --> D[OKF Bundle: markdown + YAML frontmatter]
    D -->|okf lookup| E[AI Agent]
    D -->|okf pairs| F[JSONL training data]
```

> **Flowchart:** `okf generate` scans your codebase → produces concepts → writes an OKF bundle → consumed by AI agents via `okf lookup` or converted to training data via `okf pairs`.

Extraction is fully deterministic and offline-capable — no LLM call is required to produce a usable bundle. LLM enrichment is an optional second pass that improves descriptions, and it's resumable: interrupt it anytime and rerun without redoing work already done.

After scanning, a **cross-reference linker** runs across all concepts, building two edge types:
- **Imports → Dependencies** — module-level `import`/`require` statements are matched against the dependency index, showing which dependencies each module uses (and which modules use each dependency).
- **Calls → Callees** — function/method call sites are resolved to concept IDs, rendering **Calls** and **Called By** sections in each concept file.

All 7 code languages participate (Python AST + JS/TS/Go/Java/Rust/Ruby tree-sitter). The linker is a single fast pass — no LLM, no external service.

## Bundle Layout

[#bundle-layout](#bundle-layout)

The output mirrors your source tree — dependencies get their own organized namespace:

```
okf_bundle/
├── SUMMARY.md                        ← bird's-eye view for AI agents
├── index.md                          ← root navigation
├── log.md                            ← generation history
├── _dependencies/                    ← all dependency concepts
│   ├── index.md                      ← lists ecosystems: pip, npm, cargo, ...
│   ├── pip/
│   │   ├── index.md
│   │   ├── requests.md               ← Dependency concept
│   │   └── flask.md
│   └── npm/
│       ├── index.md
│       ├── express.md
│       └── react.md
└── StockAI/
    └── RnD/
        └── python/
            └── connectors/
                ├── index.md          ← lists all concepts in this folder
                ├── economic_data.md  ← Module concept
                └── economic_data/
                    ├── WorldBankConnector.md   ← Class
                    ├── get_indicator.md        ← Function
                    └── search.md               ← Function
```

Each file is OKF v0.1 conformant:

```yaml
---
type: Class
title: WorldBankConnector
description: Fetches World Bank development indicators via wbdata API.
resource: StockAI/RnD/python/connectors/economic_data.py
tags:
  - lang:python
  - type:Class
  - module:StockAI
  - domain:RnD
  - git:branch:main
  - git:repo:TrainLLMs
timestamp: '2026-05-23T09:01:21Z'
---

# WorldBankConnector

...signature, docstring, params, returns, methods, related concepts...
```

## CLI Reference

[#cli-reference](#cli-reference)

```
okf [command] --help    Show help for a specific command
okf --version           Show version and exit

```

### `okf generate`

[#okf-generate](#okf-generate)

```
okf generate <source_dir> [output_dir] [--exclude <dir> ...]

Options:
  --summarize <bundle_dir>   Regenerate SUMMARY.md only (no re-scan)
  --exclude <dir>            Skip directories matching this name (repeatable)

Environment variables (LLM enrichment):
  OKF_ENRICH=1               Enable LLM enrichment
  OKF_BASE_URL               OpenAI-compat base URL (default: https://api.anthropic.com/v1)
  OKF_API_KEY                API key
  OKF_MODEL                  Model name (default: claude-sonnet-4-6)
  OKF_MAX_WORKERS            Parallel workers (default: 2)
```

### `okf lookup`

[#okf-lookup](#okf-lookup)

```
okf lookup [query] [options]

Options:
  --bundle PATH     Bundle directory (default: ./okf_bundle)
  --file PATH       Filter by source file
  --type TYPE       Filter by concept type: Function | Class | Module | Dependency
  --tag TAG         Filter by tag, repeatable: --tag lang:python or --tag ecosystem:npm
  --limit N         Max results (default: 10)
  --compact         One-line output per result
  --json            JSON output for programmatic use
  --full            Raw .md file content
  --min-score N     Minimum relevance score 0-1 (default: 0.1)
  --no-cache        Bypass and skip writing the lookup cache
```

### `okf diff`

[#okf-diff](#okf-diff)

```
okf diff <old_bundle> <new_bundle>

Options:
  --compact     Compact one-line output per concept
  --json        JSON output for programmatic use
```

Compares two OKF bundles and shows added, removed, and changed concepts.
Changes are detected via content hash (description, signature, tags).
Useful for PR summaries: "this PR touched 3 classes and added 1 function."

```bash
# Compare current bundle against a checkpoint
okf diff ./okf_bundle.bak ./okf_bundle

# Compact view for CI summaries
okf diff ./old_bundle ./new_bundle --compact

# JSON for automated changelog generation
okf diff ./v1_bundle ./v2_bundle --json
```

### `okf pairs`

[#okf-pairs](#okf-pairs)

```
okf pairs <bundle_dir> [output_file]

Environment variables:
  SKIP_SYNTH=1          Static pairs only (no LLM)
  SYNTH_BASE_URL        API endpoint
  SYNTH_API_KEY         API key
  SYNTH_MODEL           Model name
  MAX_WORKERS           Parallel workers (default: 3)
  QA_PER_CONCEPT        Q&A pairs per concept (default: 3)
  PAIR_TYPES            Comma-separated: codegen,qa,doc,summarize,crosslink
```

## Supported Languages & Manifests

[#supported-languages--manifests](#supported-languages--manifests)

### Code Languages

[#code-languages](#code-languages)

| Language | Parser | Extracts |
| --- | --- | --- |
| Python | stdlib `ast` | Functions, classes, params, return types, docstrings |
| JavaScript / TypeScript | tree-sitter | Functions, arrow fns, classes, JSDoc |
| Go | tree-sitter | Funcs, methods, structs, interfaces, GoDoc |
| Java | tree-sitter | Classes, methods, constructors, Javadoc |
| Rust | tree-sitter | Fns, structs, enums, traits, impl blocks, `///` |
| Ruby | tree-sitter | Defs, classes, modules, `#` comments |
| SQL | tree-sitter | Tables, views, functions, indexes, types, triggers with preceding `--`/`/* */` comments |

### Manifest / Build Files

[#manifest--build-files](#manifest--build-files)

| Format | Parser | Extracts |
| --- | --- | --- |
| `requirements.txt` | regex | pip package names + version constraints |
| `pyproject.toml` | `tomllib` | PEP 621 deps + optional-dependencies + Poetry legacy |
| `package.json` | `json` | npm/Node dependencies + devDependencies |
| `Cargo.toml` | `tomllib` | Rust crate deps + dev/build-dependencies |
| `Cargo.lock` | `tomllib` | Rust lockfile — pinned versions from `[[package]]` entries |
| `go.mod` | regex | Go module deps + `// indirect` flag |
| `go.sum` | regex | Go checksum lockfile — deduplicated module versions |
| `poetry.lock` | `tomllib` | Python Poetry lockfile — `[[package]]` with dev category detection |
| `composer.json` | `json` | PHP packages (skips `php`/`ext-*` platform entries) |
| `pom.xml` | `xml.etree.ElementTree` | Maven dependencies + `test`/`provided` scope → dev |
| `Gemfile` | regex | Ruby gems + `group :test/:development` → dev |
| `build.gradle` / `.kts` | regex | Gradle deps (Groovy + Kotlin DSL) + `testImplementation` → dev |
| `Package.swift` | regex | SwiftPM packages from `.package(url:from:)` |
| `project.clj` | regex | Clojars deps + `:dev` profile |
| `mix.exs` | regex | Hex packages + `only: :dev/:test` → dev |

## LLM Enrichment

[#llm-enrichment](#llm-enrichment)

Works with any OpenAI-compatible endpoint — Claude, Ollama, llama.cpp, etc:

```bash
# Using a local llama.cpp server
OKF_ENRICH=1 \
OKF_BASE_URL="http://localhost:8080/v1" \
OKF_API_KEY="llamabarn" \
OKF_MODEL="ggml-org/gemma-3-4b-it-qat-GGUF:Q4_0" \
OKF_MAX_WORKERS=2 \
okf generate ./my_project ./okf_bundle
```

Enrichment is **resumable** — interrupt and rerun freely. Already-enriched concepts are skipped.

## AI Agent Integration

[#ai-agent-integration](#ai-agent-integration)

okf-generator works with **any AI coding agent** — the output is plain markdown files that every agent can read.

### OpenCode / Claude Code

[#opencode--claude-code](#opencode--claude-code)

```bash
# Tell your agent about the bundle
cat >> AGENTS.md << 'EOF'
## OKF Knowledge Bundle
Before working on any class or function, look it up:
  okf lookup --bundle ./okf_bundle <ConceptName>
EOF

# Add a custom command (OpenCode)
mkdir -p .opencode/commands
echo "RUN okf lookup --bundle ./okf_bundle \$NAME" > .opencode/commands/lookup.md
```

Then: `/lookup NAME=WorldBankConnector`

### Cursor / Windsurf / Cline

[#cursor--windsurf--cline](#cursor--windsurf--cline)

Add to `.cursorrules` or agent instructions:

```
Before editing a function or class, run:
  okf lookup --bundle ./okf_bundle <Name>
To see dependencies:
  okf lookup --bundle ./okf_bundle --type Dependency
```

### GitHub Copilot

[#github-copilot](#github-copilot)

Reference OKF bundle files in your `/.github/copilot-instructions.md`:

```
Project knowledge is indexed in ./okf_bundle/
  - okf lookup <Name> returns full concept context
  - okf lookup --type Dependency returns dependency info
```

### Any agent with RUN capability

[#any-agent-with-run-capability](#any-agent-with-run-capability)

```bash
# Prime full context
cat ./okf_bundle/SUMMARY.md

# Look up a specific concept
okf lookup --bundle ./okf_bundle WorldBankConnector

# List dependencies
okf lookup --bundle ./okf_bundle --type Dependency

# JSON for programmatic agent use
okf lookup --bundle ./okf_bundle --json WorldBankConnector
```

See [docs/opencode-integration.md](https://github.com/UmairBaig8/okf-generator/blob/main/references/opencode-integration.md) for full OpenCode setup.

## Python API

[#python-api](#python-api)

```python
from okf.generator import scan_codebase, write_bundle, write_summary
from okf.lookup import load_bundle, search

# Generate bundle
concepts = scan_codebase("./my_project")
write_bundle(concepts, "./okf_bundle", "my_project", ["initial generation"])
write_summary("my_project", concepts, "./okf_bundle", {})

# Search concepts
bundle = load_bundle("./okf_bundle")
results = search(bundle, tokens=["WorldBankConnector"])
print(results[0]["description"])
```

## Training Data

[#training-data](#training-data)

Convert your OKF bundle into JSONL training pairs for fine-tuning:

```bash
# 5 pair types: codegen, qa, doc, summarize, crosslink
okf pairs ./okf_bundle ./train.jsonl
```

Each pair is in chat format compatible with most fine-tuning pipelines.

## Agent Installation

[#agent-installation](#agent-installation)

Install integration for any AI agent in one command:

```bash
# Install for all detected agents
okf install all

# Or pick specific agents
okf install claude      # Claude Code skill
okf install opencode    # OpenCode /lookup command
okf install copilot     # GitHub Copilot instructions
okf install cursor      # Cursor rules
okf install windsurf    # Windsurf rules
okf install cline       # Cline rules
```

**What each install does:**

| Agent | Files created | Effect |
|-------|---------------|--------|
| Claude Code | `~/.config/opencode/skills/okf-generator/SKILL.md` | Auto-triggers on phrases like "index my codebase" |
| OpenCode | `.opencode/commands/lookup.md` | `/lookup NAME=<ConceptName>` |
| Copilot | `.github/copilot-instructions.md` | Auto-loaded in VS Code |
| Cursor | `.cursorrules` | Auto-loaded by Cursor |
| Windsurf | `.windsurfrules` | Auto-loaded by Windsurf |
| Cline | `.clinerules` | Auto-loaded by Cline |

Or via the one-liner installer:

```bash
curl -fsSL https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/scripts/install.sh | bash
```

## FAQ

[#faq](#faq)

**Does this require an API key or internet connection?**
No. Core extraction (`okf generate`) is fully offline and deterministic — no LLM call is made unless you explicitly enable `OKF_ENRICH=1`.

**How is this different from RAG / vector search?**
RAG retrieves chunks by semantic similarity, which is approximate and can miss exact symbols. `okf lookup` is exact: it indexes real functions, classes, modules, and dependencies by name and resolves to the precise concept, with zero embedding/vector infrastructure required.

**What happens if my language isn't supported?**
Unsupported files are skipped, not dropped silently from the bundle log — `log.md` records what was scanned. Adding a new language is a self-contained tree-sitter grammar mapping; see [CONTRIBUTING.md](CONTRIBUTING.md) for a starting point — it's a listed good-first-issue.

**Does this work on monorepos / very large codebases?**
Yes — the bundle mirrors your source tree, so scanning is linear in file count. For very large repos, scope `okf generate` to a subdirectory if you only need part of the codebase indexed.

**Can I use this without any LLM at all, ever?**
Yes. `okf generate` + `okf lookup` together form a complete, zero-LLM workflow. LLM enrichment and `okf pairs` synthesis are optional layers on top.

**Is the bundle safe to commit to git?**
Yes, and that's the intended workflow — bundles are plain markdown, diff cleanly, and version alongside the code they describe.

## Contributing

[#contributing](#contributing)

Contributions are welcome! See [CONTRIBUTING.md](https://github.com/UmairBaig8/okf-generator/blob/main/CONTRIBUTING.md) for guidelines.

```bash
git clone https://github.com/UmairBaig8/okf-generator
cd okf-generator
pip install -e ".[dev]"
pytest tests/
```

**Good first issues:** adding a new language parser, improving fuzzy search scoring, adding incremental/diff-based regeneration.

## Acknowledgments

[#acknowledgments](#acknowledgments)

`okf-generator` is an independent, third-party implementation of the [Open Knowledge Format (OKF) v0.1](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing), a knowledge-representation spec introduced by Google Cloud in June 2026. See the [full v0.1 specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) for the conformance rules this generator targets. This project is not built, maintained, or endorsed by Google.

## License

[#license](#license)

[MIT](https://github.com/UmairBaig8/okf-generator/blob/main/LICENSE) — Copyright © 2026 Umair Baig
