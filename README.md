[![okf-generator banner](https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/banner.png)](https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/banner.png)

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

**Index any codebase into a structured knowledge bundle — then look up exact concepts for any AI coding agent.**

[Demo](#demo) ·
[Quick Start](#quick-start) ·
[Installation](#installation) ·
[Agent Integration](#ai-agent-integration) ·
[Supported Languages](#supported-languages--manifests) ·
[How it compares](#how-it-comparers) ·
[FAQ](#faq)

---

## Demo

[#demo](#demo)

![demo](https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/demo.gif)

## Features

🧠 **AI-agent ready** — Claude, Cursor, Copilot, Windsurf, Cline, OpenCode — any agent reads the bundle instantly.  
⚡ **Zero LLM extraction** — fully offline, deterministic, no API key needed.  
🌍 **10 languages + 17 manifest formats** — Python, JS/TS, Go, Java, Rust, Ruby, SQL, C, C++, C# + pip, npm, cargo, go, maven, gradle, yarn, pnpm, and more.  
🔗 **Cross-reference linker** — imports → dependencies, function calls → caller/callee across all languages.  
🔍 **Instant lookup** — `okf lookup` finds any class, function, or dependency in milliseconds.  
📊 **Interactive viz** — `okf visualize` generates an HTML explorer with tree nav, ego graphs, and dark/light theme.  
📦 **Training data** — `okf pairs` converts bundles to JSONL for fine-tuning.  
🔄 **Bundle diff** — `okf diff` compares two bundles (added/removed/changed).  
🌐 **Local server** — `okf serve` launches a local HTTP server for any bundle.  

## Quick Start

[#quick-start](#quick-start)

```bash
# Install
pip install okf-generator

# Generate a bundle from your project
okf generate ./my_project ./okf_bundle

# Look up a concept (zero LLM, instant)
okf lookup WorldBankConnector

# List all pip dependencies
okf lookup --type Dependency --tag ecosystem:pip
```

## Installation

[#installation](#installation)

**One-liner:**
```bash
curl -fsSL https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/scripts/install.sh | bash
```

**Or via pip:**
```bash
pip install okf-generator           # core (offline extraction)
pip install "okf-generator[llm]"   # with LLM enrichment + training pairs
```

## Why this exists

[#why-this-exists](#why-this-exists)

AI coding agents waste enormous amounts of context re-reading entire files to find one function, class, or dependency version. Ask an agent *"what does `WorldBankConnector` do?"* and it either guesses from a stale memory, or burns thousands of tokens reading the whole file to find a 12-line answer.

`okf-generator` solves this by converting your source code into the [Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) (OKF) v0.1 — a directory of small, structured markdown files, one per concept (function, class, module, dependency). An agent then asks a surgical question and gets a surgical answer:

```
# Before touching WorldBankConnector, look it up
okf lookup WorldBankConnector

# CLASS: WorldBankConnector
# Source      : StockAI/RnD/python/connectors/economic_data.py  line 51
# Description : Fetches World Bank development indicators via wbdata API.
# Methods     : get_indicator, search
# Signature   : class WorldBankConnector
```

No re-reading the file. No guessing. No LLM call required.

![Before and after comparison](https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/before_after.svg)

## How it compares

[#how-it-compares](#how-it-compares)

The OKF ecosystem is moving fast — here's where `okf-generator` sits relative to other producers:

| | **okf-generator** | Other OKF producers |
| --- | --- | --- |
| Language coverage | 10 languages (Python, JS/TS, Go, Java, Rust, Ruby, SQL, C, C++, C#) | Usually 1 language or doc-only |
| Cross-reference linking | Imports → dependencies, function calls → caller/callee across all languages | Not typically supported |
| Dependency/manifest parsing | 12 formats (pip, npm, cargo, go, maven, gradle, composer, rubygems, swiftpm, clojars, hex, +1) | Not typically supported |
| Extraction | Zero-LLM, deterministic, offline | Often LLM-required for every concept |
| Optional enrichment | Any OpenAI-compatible endpoint (Claude, local llama.cpp, Ollama) | Often locked to one vendor |
| Training data export | Built-in JSONL pair generator (5 pair types) | Not typically included |
| Agent compatibility | Any agent that can run a CLI (Claude Code, Cursor, Windsurf, Copilot, OpenCode, Cline) | Often single-agent focused |

If you're choosing between OKF producers: pick `okf-generator` when you want broad language + dependency coverage with zero mandatory LLM cost, and you want the bundle to double as a fine-tuning data source.

## How it works

[#how-it-works](#how-it-works)

![okf-generator pipeline](https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/workflow.png)

> **Pipeline:** `okf generate` scans your codebase → linker resolves cross-references → writes an OKF bundle → consumed via 6 commands (lookup, pairs, visualize, diff, serve, install).

Extraction is fully deterministic and offline-capable. LLM enrichment is an optional second pass, resumable on interrupt.

After scanning, a **cross-reference linker** builds two edge types:
- **Imports → Dependencies** — module imports matched against the dependency index.
- **Calls → Callees** — function call sites resolved to concept IDs.

## Used by / Built for

[#used-by--built-for](#used-by--built-for)

`okf-generator` was originally built to index a large, multi-domain codebase (`StockAI`/`TrainLLMs`) spanning Python data connectors, ML pipelines, and SQL schemas — the kind of project where giving an agent the *whole* repo as context is both slow and unaffordable in tokens. If you're working in a sprawling codebase and tired of re-explaining your own code to your AI agent every session, this is the tool that problem was built to solve.

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

Full documentation for every command:

```bash
okf --help              Show available commands
okf <command> --help    Show options for a specific command
okf --version           Show version
```

| Command | Usage |
|---------|-------|
| `generate` | `okf generate <source_dir> [output_dir]` |
| `lookup` | `okf lookup <query>` |
| `diff` | `okf diff <old_bundle> <new_bundle>` |
| `pairs` | `okf pairs <bundle_dir> [output_file]` |
| `summarize` | `okf summarize <bundle_dir>` |
| `install` | `okf install [claude \| opencode \| copilot \| cursor \| windsurf \| cline]` |
| `visualize` | `okf visualize <bundle_dir> [output.html]` |
| `serve` | `okf serve [dir] [--port] [--open]` |

See [docs/cli-reference.md](https://github.com/UmairBaig8/okf-generator/blob/main/docs/cli-reference.md) for full options, environment variables, and examples.

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
| C | tree-sitter | Functions, structs with `/**` doc comments |
| C++ | tree-sitter | Functions, classes, structs, methods with `///` doc comments |
| C# | tree-sitter | Classes, methods, top-level functions |
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
| `yarn.lock` | regex | Yarn lockfile (v1) — package name + pinned versions |
| `pnpm-lock.yaml` | `yaml` | pnpm lockfile — package name + version + dev flag |
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

### Recommended system prompt

When setting up agent instructions, include:

```markdown
This project has an OKF knowledge bundle at ./okf_bundle/.
- Use `okf lookup <Name>` to get full concept context.
- Use `okf lookup --type <Type>` to filter by type (Class, Function, Dependency).
- Use `okf lookup --tag ecosystem:<name>` for ecosystem-specific queries.
- Read `SUMMARY.md` for the full knowledge map.
```

### Token efficiency

| Optimization | How okf-generator helps | Agent impact |
|-------------|------------------------|--------------|
| Deterministic types | Every concept has `type: Function`, `type: Class`, `type: Dependency` | Agent filters by type precisely |
| Incremental access | `okf lookup <Name>` returns one concept, not whole files | Saves 80-95% token cost vs reading source |
| Structured metadata | Signature, params, returns in YAML frontmatter | Agent extracts info without parsing code |
| Cross-reference edges | Calls / Called By / Used By in each concept | Enables multi-hop reasoning without grep |

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

See [docs/python-api.md](https://github.com/UmairBaig8/okf-generator/blob/main/docs/python-api.md) for the full API reference.

```python
from okf.generator import scan_codebase, write_bundle, write_summary
from okf.lookup import load_bundle, search

concepts = scan_codebase("./my_project")
write_bundle(concepts, "./okf_bundle", "my_project", ["initial generation"])
write_summary("my_project", concepts, "./okf_bundle", {})
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
