<p align="center">
  <img src="https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/images/okf-logo-light.svg" alt="okf-generator" width="500">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/images/banner.png" alt="okf-generator demo" width="700">
</p>

<p align="center">
  <a href="https://pypi.org/project/okf-generator/"><img src="https://img.shields.io/pypi/v/okf-generator?style=flat-square&label=PyPI" alt="PyPI"></a>
  <a href="https://pypi.org/project/okf-generator/"><img src="https://img.shields.io/pypi/dm/okf-generator?style=flat-square" alt="Downloads"></a>
  <a href="https://pypi.org/project/okf-generator/"><img src="https://img.shields.io/pypi/pyversions/okf-generator?style=flat-square" alt="Python"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/actions"><img src="https://img.shields.io/github/actions/workflow/status/UmairBaig8/okf-generator/ci.yml?style=flat-square&label=tests" alt="Tests"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/commits/main"><img src="https://img.shields.io/github/last-commit/UmairBaig8/okf-generator?style=flat-square" alt="Last commit"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="MIT"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/blob/main/SKILL.md"><img src="https://img.shields.io/badge/Claude-Skill-orange?style=flat-square&logo=anthropic" alt="Claude Skill"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/blob/main/CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square" alt="PRs Welcome"></a>
  <a href="https://umairbaig8.github.io/okf-generator/"><img src="https://img.shields.io/badge/🌐-Site-7c3aed?style=flat-square" alt="Site"></a>
</p>

<p align="center">
  <b>Parse any codebase into structured, agent-ready knowledge. High-velocity extraction across 17 languages — zero LLM required.</b>
</p>

<p align="center">
  <a href="#installation">Installation</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#how-it-works">Architecture</a> ·
  <a href="#for-ai-agents">Agents</a> ·
  <a href="#for-local-ai--slms">Local AI</a> ·
  <a href="#for-cicd-pipelines">CI/CD</a> ·
  <a href="#language--manifest-coverage">Languages</a> ·
  <a href="#faq">FAQ</a>
</p>

<br>

## Visual Showcase

![okf-generator demo](https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/images/demo.gif)

`okf generate` scans any repo using tree-sitter AST parsers, resolves cross-references across 17 languages, and outputs a structured knowledge graph. Explore it interactively or consume it programmatically — no LLM required.

```bash
# Generate a knowledge bundle from any codebase
okf generate ./my_project ./okf_bundle

# Explore as an interactive HTML dashboard
okf visualize ./okf_bundle

# Browse via local HTTP
okf serve ./okf_bundle --open

# Look up any concept in milliseconds
okf lookup WorldBankConnector
```

---

## Quick Start

```bash
# Install
pip install okf-generator

# Generate a bundle from your project
okf generate ./my_project ./okf_bundle

# Look up a concept (zero LLM, instant)
okf lookup WorldBankConnector

# List all dependencies
okf lookup --deps

# Interactive bundle setup wizard
okf init

# Visualize as interactive HTML
okf visualize ./okf_bundle
```

---

## Installation

```bash
# One-liner (macOS / Linux)
curl -fsSL https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/scripts/install.sh | bash

# Or via pip
pip install okf-generator                        # core (offline extraction)
pip install "okf-generator[llm]"                  # with LLM enrichment + training pairs
```

---

## Why — Code-Level Knowledge Graphs

AI coding agents waste enormous amounts of context re-reading entire files to find one function signature or dependency version. Cloud models with 200K token windows mask this cost; local SLMs (Gemma, Llama, Phi) on a MacBook run out of memory immediately.

`okf-generator` solves this by converting source code into a **deterministic, cross-referenced knowledge graph**. Using tree-sitter AST parsers across 17 languages, every function, class, module, and dependency becomes a structured node with typed edges (calls, called-by, imports, depends-on).

```bash
# Before touching WorldBankConnector, get its full graph context
okf lookup WorldBankConnector
```

```
CLASS: WorldBankConnector
Source      : StockAI/RnD/python/connectors/economic_data.py  line 51
Description : Fetches World Bank development indicators via wbdata API.
Methods     : get_indicator, search
Signature   : class WorldBankConnector
Calls       : [wbdata.get_indicator, pandas.DataFrame]
Called-by   : [DataPipeline.fetch_economic]
```

No re-reading the file. No guessing. No LLM call required.

![Before and after comparison](https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/images/before_after.svg)

---

## How It Works

![okf-generator pipeline](https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/images/workflow.png)

**1. Scan** — tree-sitter AST parsers extract every function, class, method, and module with signature, params, docstring, and return types across 17 languages.

**2. Link** — the cross-reference linker resolves two edge types:
- Imports → Dependencies — module imports matched against the dependency index.
- Calls → Callees — function call sites resolved to concept IDs.

**3. Write** — outputs an OKF v0.1 bundle: structured markdown files (one per concept) mirroring the source tree.

**4. Consume** — 8 commands: `lookup`, `pairs`, `diff`, `visualize`, `mcp`, `serve`, `init`, `summarize`.

**5. Enrich (optional)** — 4 modes to enhance description, docstring, security, and cross-links. Runs at generate time or standalone against an existing bundle.

Extraction is fully deterministic and offline-capable. Enrichment is optional, resumable, and works with any AI provider.

### Used by / Built for

`okf-generator` was originally built to index a large, multi-domain codebase (`StockAI`/`TrainLLMs`) spanning Python data connectors, ML pipelines, and SQL schemas — the kind of project where giving an agent the whole repo as context is both slow and unaffordable in tokens. If you are working in a sprawling codebase and tired of re-explaining your own code to your AI agent every session, this is the tool that problem was built to solve.

---

## Bundle at a Glance

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

Each file is OKF v0.1 conformant with YAML frontmatter:

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
```

---

## Interactive Visualization

`okf visualize` generates a self-contained HTML dashboard — no server, no installation, works offline:

```bash
okf visualize ./okf_bundle ./viz.html
# Open viz.html in any browser
```

The visualization uses D3.js with:
- **Force-directed graph** — color-coded nodes by concept type (Class, Function, Module, Dependency)
- **Relationship edges** — calls, called-by, imports, related
- **Search/filter** — by name, type, ecosystem
- **Tooltip on hover** — description + resource location
- **Pan/zoom** — navigate large graphs
- **Dark/light theme** — toggle at runtime

### Multi-bundle monorepo support

If your bundle contains sub-bundles (detected by `SUMMARY.md` in subdirectories), the viz adds a **bundle selector** dropdown in the topbar to filter by project. Each sub-bundle's dependencies and source files are scoped under its own namespace.

```bash
# Combined viz with bundle switcher (cross-bundle edges preserved)
okf visualize ./okf_bundle

# Standalone viz per sub-bundle (smaller, faster)
okf visualize ./okf_bundle/AgentBox agentbox.html
okf visualize ./okf_bundle/StockAI stockai.html
```

The bundled viz is ideal for exploring relationships across projects; per-bundle viz files are better for focused navigation on a single project.

---

## Live Dashboard (FastAPI)

`okf dashboard` launches an interactive web UI — live search, detail inspection, and concept graph in your browser:

```bash
okf dashboard ./okf_bundle --open
```

Opens a 3-panel layout at `http://127.0.0.1:8700`:

| Panel | What it does |
|-------|-------------|
| **Sidebar tree** | Grouped by type, collapsible groups, search + type/language filters |
| **Detail panel** | Structured metadata grid (type, language, signature), expandable sections for params/returns/docstring, linked concept navigation (related, calls, called-by, used-by) |
| **Global Graph** | Force-directed vis-network of the top 120 connected concepts — color-coded by type, click-to-navigate, zoom/pan, legend bar |
| **Subgraph** | Per-concept connection graph showing immediate neighbors |

**Theme switch** — light/dark toggle persisted to localStorage. All graphs re-render on theme change.

**Keyboard shortcuts** — `Esc` close detail, `/` focus search, Enter to navigate.

---

## For AI Agents

Every concept in the bundle is deterministic, typed, and cross-referenced — agents get surgical precision without burning context:

| Capability | How |
|---|---|
| Manifest coverage | 19 formats incl. **Dockerfile**, **Containerfile**, **docker-compose.yml** |
| Smart config | `okf config` / `.okfconfig` — global + per-section settings, no env vars |
| Quick setup wizard | `okf init` — interactive prompts for source, bundle, LLM enrichment |
| Pre-commit hook | Auto-regenerates bundle on commit when source files change |
| Docker image | `ghcr.io/umairbaig8/okf-generator/okf-generator` — CI-ready |
| Zero-LLM lookups | `okf lookup <Name>` returns full concept detail in milliseconds |
| Fuzzy / camelCase search | `okf lookup repo` finds `UserRepository`; `okf lookup ur` matches acronyms |
| Type filters | `okf lookup --type Function | Class | Dependency` |
| Ecosystem queries | `okf lookup --tag ecosystem:pip` |
| Source file queries | `okf lookup --file path/to/file.py` |
| JSON output | `okf lookup --json <Name>` for programmatic agent use |
| MCP protocol | `okf mcp ./okf_bundle` exposes 7 tools: `lookup`, `get_concept`, `find_callers`, `list_by_file`, `list_dependencies`, `bundle_info`, `list_by_type` |
| Summary map | `cat ./okf_bundle/SUMMARY.md` primes full context |

### Quick setup for any agent:

Add to your agent instructions or custom rules:

```markdown
This project has an OKF knowledge bundle at ./okf_bundle/.
- Use `okf lookup <Name>` for full concept context.
- Use `okf lookup --type <Type>` to filter by type.
- Read `SUMMARY.md` for the full knowledge map.
```

### Token efficiency

| Optimization | Agent impact |
|---|---|
| Incremental access — one concept, not whole files | Saves 80-95% token cost vs reading source |
| Structured metadata in YAML frontmatter | Agent extracts info without parsing code |
| Cross-reference edges (calls/called-by) | Multi-hop reasoning without grep |
| Deterministic types | Agent filters by type precisely |

> Full agent integration guide — OpenCode commands, Cursor rules, Copilot instructions, MCP setup: **[docs/agent-integration.md](docs/agent-integration.md)**

> Automated agent setup — `okf install claude`, `okf install opencode`, `okf install cursor`, etc: see [Agent Installation](#agent-installation).

---

## For Local AI & SLMs

Cloud models have massive context windows. Local SLMs (Gemma 3 4B, Llama 3.2, Phi-3) running on a MacBook Pro or Air do not — they run out of memory if you try to feed an entire repository.

`okf lookup` solves this with **exact-symbol retrieval**: the agent sends a 50-token query and gets back a 200-token concept card. No embeddings, no vector DB, no RAG pipeline. This makes local coding assistants viable for enterprise-scale codebases.

### Enrichment modes

Choose how deep the LLM goes — all modes are resumable (interrupt and rerun freely, already-enriched concepts are skipped):

| Mode | What it does | Needs source body? |
|------|-------------|:---:|
| `base` | Improves descriptions + docstrings (Google-style) | ❌ |
| `deep` | Adds usage examples, side effects, security notes, complexity estimates | ✅ |
| `security` | Audits existing bundle for visible risk patterns only | ✅ |
| `full` | All of the above + semantic related-links | ✅ |

```bash
# Enrich at generate time
okf generate ./my_project ./okf_bundle --enrich deep

# Or enrich an existing bundle (no re-scan needed)
okf enrich ./okf_bundle --mode full
```

### Multi-provider routing

Each enrich mode can use a different provider. Route cheap description work to local llama.cpp and security audits to a stronger cloud model — all from one config file:

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

Built-in provider presets: `local`, `openai`, `anthropic`, `deepseek`, `gemini`, `glm`, `ollama`, `lmstudio`, `openrouter`, `dashscope`, `minimax`.

Enrichment works with any OpenAI-compatible endpoint — Ollama, llama.cpp, vLLM, or cloud APIs (Claude, GPT, DeepSeek, GLM).

---

## For CI/CD Pipelines

Deterministic + fully offline = ideal for automated pipelines:

A pre-built **GitHub Action** (`.github/workflows/okf-bundle.yml`) auto-generates the bundle on every push/PR to `main`, caches previous bundles per branch, diffs with `--impact`, and posts a PR comment showing which dependency changes affect which code:

```yaml
# .github/workflows/okf-bundle.yml  (ships with the package)
name: OKF Bundle
on:
  push:     { branches: [main] }
  pull_request: { branches: [main] }
jobs:
  generate:
    runs-on: ubuntu-latest
    permissions: { contents: read, pull-requests: write }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5          { python-version: "3.12" }
      - run: pip install okf-generator
      - run: okf generate . okf_bundle
      - uses: actions/cache/restore@v4          { ... }
      - run: okf diff .okf_bundle_prev okf_bundle --impact
      - uses: actions/github-script@v7          # post/update PR comment
      - uses: actions/upload-artifact@v4         { name: okf-bundle, path: okf_bundle/ }
```

Push bundles to S3/GCS/Azure for centralized multi-tenant access. Serve them as static websites for zero-infrastructure browsing.

> Full CI/CD guide — GitLab, pre-commit hooks, S3 static hosting, monorepo strategies: **[docs/ci-cd.md](docs/ci-cd.md)**

---

## Language & Manifest Coverage

### Code Languages (17)

Each language lives in its own file under `okf/parsers/`. Adding a new language requires one file + one registry entry — no changes to the core generator.

| Language | File | Parser | Extracts |
|----------|------|--------|----------|
| Python | `parsers/python.py` | stdlib `ast` | Functions, classes, methods, params, return types, docstrings, decorators, inheritance, type params |
| JavaScript / TypeScript | `parsers/javascript.py` | tree-sitter | Functions, arrow fns, methods, classes, interfaces, type aliases, enums, JSDoc, generics, heritage, visibility |
| Go | `parsers/go.py` | tree-sitter | Funcs, methods, structs, interfaces, GoDoc, type params (Go 1.18+) |
| Java | `parsers/java.py` | tree-sitter | Classes, interfaces, enums, methods, constructors, Javadoc, generics, annotations, visibility, inheritance, fields |
| Rust | `parsers/rust.py` | tree-sitter | Fns, structs, enums, traits, impl blocks, `///`/`//!`, generics, `#[derive]`, visibility |
| Swift | `parsers/swift.py` | tree-sitter | Classes, structs, enums, protocols (→Interface), generics, methods, init, doc comments |
| Kotlin | `parsers/kotlin.py` | tree-sitter | Classes, data classes, objects, enums, interfaces, generics, constructor params, visibility |
| PHP | `parsers/php.py` | tree-sitter | Classes, interfaces, traits, enums, functions, methods, visibility, typed params, return types, PHPDoc |
| Dart | `parsers/dart.py` | tree-sitter | Classes, mixins, enums, functions, constructors, methods |
| Scala | `parsers/scala.py` | tree-sitter | Classes, objects, traits (→Interface), enums, functions, visibility, typed params |
| Julia | `parsers/julia.py` | tree-sitter | Functions, structs (→Class), abstract types (→Interface), constants, macros |
| Ruby | `parsers/ruby.py` | tree-sitter | Defs, classes, modules, `#`/YARD doc comments, superclass |
| C | `parsers/c.py` | tree-sitter | Functions, structs, enums, typedefs, `/**` doc comments |
| C++ | `parsers/cpp.py` | tree-sitter | Functions, classes, methods, templates, base classes, visibility |
| C# | `parsers/csharp.py` | tree-sitter | Classes, methods, generics, attributes, base types, visibility, fields |
| SQL | `parsers/sql.py` | tree-sitter | Tables (columns, PK, FK, constraints), views, functions, indexes, triggers |
| _new_ | `parsers/your_lang.py` | tree-sitter | You define it — see [development guide](docs/development.md) |

### Manifest / Build Formats (17)

`requirements.txt` · `pyproject.toml` · `package.json` · `Cargo.toml` · `Cargo.lock` · `yarn.lock` · `pnpm-lock.yaml` · `go.mod` · `go.sum` · `poetry.lock` · `composer.json` · `pom.xml` · `Gemfile` · `build.gradle` / `.kts` · `Package.swift` · `project.clj` · `mix.exs` · `Dockerfile` / `Containerfile` · `docker-compose.yml`

> Full table with parser details + architectural query examples: **[docs/languages-and-manifests.md](docs/languages-and-manifests.md)**

**Architectural query example** — find every microservice depending on a deprecated Rust crate:

```bash
okf lookup --type Dependency --tag ecosystem:cargo --compact
okf lookup --type Dependency openssl
```

Same logic works for pip, npm, go, maven — any of the 17 supported formats. Pin a vulnerable package version across every service in seconds.

---

## CLI Reference

```bash
okf --help              Show available commands
okf <command> --help    Show options for a specific command
okf --version           Show version
```

| Command | Usage |
|---|---|
| `generate` | `okf generate <source_dir> [output_dir] [--enrich [mode]]` |
| `enrich` | `okf enrich <bundle_dir> [--mode mode] [--src path]` |
| `lookup` | `okf lookup <query>` |
| `diff` | `okf diff <old_bundle> <new_bundle>` |
| `pairs` | `okf pairs <bundle_dir> [output_file]` |
| `summarize` | `okf summarize <bundle_dir>` |
| `install` | `okf install [claude \| opencode \| copilot \| cursor \| windsurf \| cline]` |
| `init` | `okf init [dir]` |
| `visualize` | `okf visualize <bundle_dir> [output.html]` |
| `mcp` | `okf mcp <bundle_dir>` |
| `serve` | `okf serve [dir] [--port] [--open]` |
| `dashboard` | `okf dashboard <bundle_dir> [--port] [--open]` |

> Full options, environment variables, and examples: **[docs/cli-reference.md](docs/cli-reference.md)**

---

## Training Data

Convert your OKF bundle into JSONL training pairs for fine-tuning:

```bash
# 5 pair types: codegen, qa, doc, summarize, crosslink
okf pairs ./okf_bundle ./train.jsonl
```

Each pair is in chat format compatible with most fine-tuning pipelines.

- **Static pairs** (no LLM): `SKIP_SYNTH=1 okf pairs ...`
- **LLM-synthesized pairs**: set `SYNTH_MODEL`, `QA_PER_CONCEPT`, `PAIR_TYPES`

---

## Python API

```python
from okf.generator import scan_codebase, write_bundle, write_summary
from okf.lookup import load_bundle, search

concepts = scan_codebase("./my_project")
write_bundle(concepts, "./okf_bundle", "my_project", ["initial generation"])
write_summary("my_project", concepts, "./okf_bundle", {})

bundle = load_bundle("./okf_bundle")
results = search(bundle, tokens=["WorldBankConnector"])
```

> Full API reference with `Concept` dataclass: **[docs/python-api.md](docs/python-api.md)**

---

## Agent Installation

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
|---|---|---|
| Claude Code | `~/.config/opencode/skills/okf-generator/SKILL.md` | Auto-triggers on phrases like "index my codebase" |
| OpenCode | `.opencode/commands/lookup.md` | `/lookup NAME=<ConceptName>` |
| Copilot | `.github/copilot-instructions.md` | Auto-loaded in VS Code |
| Cursor | `.cursorrules` | Auto-loaded by Cursor |
| Windsurf | `.windsurfrules` | Auto-loaded by Windsurf |
| Cline | `.clinerules` | Auto-loaded by Cline |

---

## How It Compares

| | **okf-generator** | Other OKF producers |
|---|---|---|
| Language coverage | 17 languages, modular parsers (`okf/parsers/*.py`) — add one in minutes | Usually 1 language or doc-only |
| Cross-reference linking | Imports → dependencies, function calls → caller/callee across all languages | Not typically supported |
| Dependency/manifest parsing | 17 formats (pip, npm, cargo, go, maven, gradle, composer, rubygems, swiftpm, clojars, hex, +7) | Not typically supported |
| Extraction | Zero-LLM, deterministic, offline | Often LLM-required for every concept |
| Enrichment modes | 4 tiers (`base`, `deep`, `security`, `full`) — per-model provider routing | Usually 1 mode, 1 provider |
| Multi-provider routing | Route each enrich mode to a different provider (local LLM for descriptions, cloud for security) | Often locked to one vendor |
| Post-hoc enrichment | `okf enrich` runs against existing bundle — no re-scan. Source origin auto-loaded from bundle metadata | Not supported |
| Training data export | Built-in JSONL pair generator (5 pair types) | Not typically included |
| Agent compatibility | Any agent that can run a CLI (Claude Code, Cursor, Windsurf, Copilot, OpenCode, Cline) | Often single-agent focused |
| CI/CD integration | Built-in GitHub Action (`okf-bundle.yml`) — bundle generation + impact diff + PR comments | Not typically included |

If you are choosing between OKF producers: pick `okf-generator` when you want broad language + dependency coverage with zero mandatory LLM cost, and you want the bundle to double as a fine-tuning data source.

---

## FAQ

**Does this require an API key or internet connection?**
No. Core extraction (`okf generate`) is fully offline and deterministic — no LLM call is made unless you explicitly enable `OKF_ENRICH=1`.

**How is this different from RAG / vector search?**
RAG retrieves chunks by semantic similarity, which is approximate and can miss exact symbols. `okf lookup` is exact: it indexes real functions, classes, modules, and dependencies by name and resolves to the precise concept, with zero embedding/vector infrastructure required.

**What happens if my language is not supported?**
Unsupported files are skipped, not dropped silently — `log.md` records what was scanned. Adding a new language is a self-contained tree-sitter grammar mapping: create `okf/parsers/your_lang.py` and add one line to the extension registry. See [docs/development.md](docs/development.md) for the step-by-step guide.

**Does this work on monorepos / very large codebases?**
Yes — the bundle mirrors your source tree, so scanning is linear in file count. For very large repos, scope `okf generate` to a subdirectory if you only need part of the codebase indexed.

**Can I use this without any LLM at all, ever?**
Yes. `okf generate` + `okf lookup` together form a complete, zero-LLM workflow. LLM enrichment and `okf pairs` synthesis are optional layers on top.

**Is the bundle safe to commit to git?**
Yes, and that is the intended workflow — bundles are plain markdown, diff cleanly, and version alongside the code they describe.

---

## Contributing

```bash
git clone https://github.com/UmairBaig8/okf-generator
cd okf-generator
pip install -e ".[dev]"
pytest tests/
```

**Good first issues:** adding a new language parser, improving fuzzy search scoring, adding incremental/diff-based regeneration.

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## Acknowledgments

`okf-generator` is an independent, third-party implementation of the [Open Knowledge Format (OKF) v0.1](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing), a knowledge-representation spec introduced by Google Cloud in June 2026. See the [full v0.1 specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) for the conformance rules this generator targets.

This project is not built, maintained, or endorsed by Google.

---

## License

[MIT](LICENSE) — Copyright © 2026 Umair Baig
