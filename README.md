<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/UmairBaig8/okf-generator@main/docs/images/okf_banner.jpg" alt="okf-generator" width="700">
</p>

<p align="center">
  <a href="https://pypi.org/project/okf-generator/"><img src="https://img.shields.io/pypi/v/okf-generator?style=flat-square&label=PyPI" alt="PyPI"></a>
  <a href="https://pypi.org/project/okf-generator/"><img src="https://img.shields.io/pypi/pyversions/okf-generator?style=flat-square" alt="Python"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/stargazers"><img src="https://img.shields.io/github/stars/UmairBaig8/okf-generator?style=flat-square" alt="GitHub Stars"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/actions"><img src="https://img.shields.io/github/actions/workflow/status/UmairBaig8/okf-generator/ci.yml?style=flat-square&label=tests" alt="Tests"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/commits/main"><img src="https://img.shields.io/github/last-commit/UmairBaig8/okf-generator?style=flat-square" alt="Last commit"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="MIT"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/blob/main/CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square" alt="PRs Welcome"></a>
  <a href="https://umairbaig8.github.io/okf-generator/docs-site/"><img src="https://img.shields.io/badge/📖-Docs-7c3aed?style=flat-square" alt="Docs"></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-Server-5b21b6?style=flat-square" alt="MCP"></a>
  <a href="https://www.cursor.com"><img src="https://img.shields.io/badge/Cursor-Ready-7c3aed?style=flat-square" alt="Cursor"></a>
  <a href="https://github.com/anthropics/claude-code"><img src="https://img.shields.io/badge/Claude-Ready-7c3aed?style=flat-square&logo=anthropic" alt="Claude"></a>
</p>

<h1 align="center">OKF Generator</h1>
<h3 align="center">The knowledge layer for AI coding agents</h3>

<p align="center">
  <b>Scan any codebase into structured, agent-ready knowledge — 17 languages, <strong>~100x fewer tokens</strong> than reading whole files, <strong>zero LLM required</strong>.
</p>

<p align="center">
  <a href="#quick-start"><b>Quick Start</b></a> ·
  <a href="#the-why"><b>Why OKF?</b></a> ·
  <a href="#core-features"><b>Features</b></a> ·
  <a href="#agent-integration"><b>Agents</b></a> ·
  <a href="#comparison"><b>vs RAG</b></a> ·
  <a href="#faq"><b>FAQ</b></a>
</p>

<br>

## Visual Hook & Demos

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/UmairBaig8/okf-generator@main/docs/demo.gif" alt="okf-generator demo" width="540">
  <br>
  <em><code>okf generate</code> → <code>okf lookup</code> → <code>okf diff</code> → <code>okf visualize</code> → <code>okf mcp</code> → <code>okf pairs</code></em>
</p>

<p align="center">
  <a href="https://umairbaig8.github.io/okf-generator/viz.html"><b>Live Viz Graph</b></a>
  <span>&nbsp;&middot;&nbsp;</span>
  <a href="https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=UmairBaig8/okf-generator"><b>Interactive Dev Container</b></a>
  <span>&nbsp;&middot;&nbsp;</span>
  <a href="https://okf-generator.onrender.com"><b>Render App Demo</b></a>
</p>

---

## The Why

### AI agents waste tokens re-reading code

Every context reset forces agents to re-read entire files to find one function signature. A 600-line file costs **14,000 tokens** — just to find one class. Cloud models with 200K windows mask this cost; local SLMs on a MacBook run out of memory immediately.

Vector databases (RAG) don't solve this — they shred code into arbitrary chunks, losing syntax structure, import pathways, and call relationships.

### The OKF Edge: deterministic AST extraction

Instead of chunking text, `okf-generator` uses **tree-sitter AST parsers** to create a mathematical map of your codebase. Every function, class, module, and dependency becomes a structured node with typed edges (calls, called-by, imports, depends-on).

**The result:** an average lookup drops from **45,000 tokens → 1,200 tokens** — a **~97.3% reduction**.

```bash
# Before touching any file, get the exact concept card
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

---

## Core Features

| Capability | What it means |
|---|---|
| **17 languages** | Native AST extraction for Python, JS/TS, Go, Rust, Java, C++, Swift, Kotlin, Ruby, C/C++/C#, SQL, PHP, Dart, Scala, Julia — one parser file per language, add a new one in minutes |
| **22 manifest formats** | Automatic cross-indexing of `package.json`, `Cargo.toml`, `Dockerfile`, `go.mod`, `requirements.txt`, `Gemfile`, `pyproject.toml`, and 15 more |
| **Deterministic & offline** | Core extraction is **100% offline** — zero LLM calls, zero API keys, zero vector infrastructure. Same output every run |
| **Cross-reference linker** | Resolves imports → dependency edges and function calls → caller/callee across all languages. Multi-hop reasoning without grep |
| **LSP call-graph enrichment** | Optional LSP pass (`okf enrich --lsp`) uses local language servers for compiler-accurate caller/callee resolution — 4 servers mapped (pyright ✅, gopls, rust-analyzer, typescript-language-server), zero token cost |
| **Interactive visualization** | Self-contained D3.js HTML dashboard — force-directed graph, search, filter, dark/light theme, no server required |
| **Token efficiency** | ~140 tokens per concept lookup vs 14,000+ reading whole files. Local SLMs become viable for enterprise-scale codebases |
| **4 enrichment tiers** | Optional LLM layer: `base` (descriptions), `deep` (examples + side effects), `security` (risk audit), `full` (all + semantic links). Runs at generate time or standalone |
| **Multi-provider routing** | Route cheap work to local llama.cpp, security audits to Claude — one config file |
| **Bundle diff & impact** | `okf diff --impact` shows exactly what changed between runs — which deps affect which modules |
| **Training data export** | `okf pairs` converts any bundle into JSONL fine-tuning pairs (codegen, QA, doc, summarize, crosslink) |

### How it works

![okf-generator pipeline](https://cdn.jsdelivr.net/gh/UmairBaig8/okf-generator@main/docs/images/workflow.png)

```
1. Scan  → tree-sitter AST parsers extract functions, classes, modules (17 langs)
2. Link  → cross-reference linker resolves imports→deps, calls→callees
3. Write → OKF v0.2 bundle: structured markdown, mirrors your source tree
4. Use   → lookup, ask, diff, visualize, mcp, dashboard — 14 commands
5. Enrich → optional LSP pass (deterministic call-graph refinement) + optional LLM layer: 4 modes, multi-provider routing
```

Core extraction is fully deterministic and offline. Enrichment is optional, resumable, works with any AI provider. LSP enrichment requires language server binaries on `$PATH`.

> Full language table with per-parser details: **[docs/languages-and-manifests.md](docs/languages-and-manifests.md)**

### Supported languages (18)

`Python` · `JavaScript` · `TypeScript` · `Go` · `Java` · `Rust` · `Swift` · `Kotlin` · `PHP` · `Dart` · `Scala` · `Julia` · `Ruby` · `C` · `C++` · `C#` · `SQL` · `YAML`

Each language lives in its own file under `okf/parsers/`. Add a new one in minutes — one file + one registry entry.

### Domain Classification

Use `--domains crossplane` to re-classify YAML concepts using data-driven rules. Built-in rules for Crossplane (XRD, Composition, Claim, ProviderConfig, ManagedResource). Custom domains via `--domain-rules ./my-rules.yaml`. See **[docs/domain-classification.md](docs/domain-classification.md)**.

### Manifest formats (17)

`requirements.txt` · `pyproject.toml` · `package.json` · `Cargo.toml` · `Cargo.lock` · `yarn.lock` · `pnpm-lock.yaml` · `go.mod` · `go.sum` · `poetry.lock` · `composer.json` · `pom.xml` · `Gemfile` · `build.gradle` / `.kts` · `Package.swift` · `Dockerfile` / `Containerfile` · `docker-compose.yml`

![Before and after: 14,000 tokens vs 140 tokens](https://cdn.jsdelivr.net/gh/UmairBaig8/okf-generator@main/docs/images/before_after.svg)

### What a bundle looks like

```
okf_bundle/
├── SUMMARY.md                    ← agent's bird's-eye view
├── index.md                      ← root navigation
├── _dependencies/                ← deps by ecosystem (pip, npm, cargo…)
└── my_project/
    └── connectors/
        ├── index.md              ← lists all concepts in folder
        ├── economic_data.md      ← Module concept
        └── economic_data/
            ├── WorldBankConnector.md   ← Class (signature, methods, calls)
            ├── get_indicator.md        ← Function (params, returns)
            └── search.md               ← Function
```

Each file follows the OKF v0.2 dialect (extended from Google's OKF v0.1) with structured YAML frontmatter — agents parse it deterministically, no guessing.

---

## Quick Start

### Install in 30 seconds

```bash
# Via pip
pip install okf-generator

# Or one-liner (macOS / Linux)
curl -fsSL https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/scripts/install.sh | bash
```

### Generate your first bundle

```bash
okf generate ./my_project ./okf_bundle
```

That's it — no API key, no vector DB, no config required.

### Look up any concept

```bash
okf lookup WorldBankConnector

# Filter by type
okf lookup --type Function

# Filter by ecosystem
okf lookup --tag ecosystem:pip

# JSON output for programmatic use
okf lookup --json WorldBankConnector

# Fuzzy / camelCase search
okf lookup repo          # finds UserRepository
```

### Visualize as interactive HTML

```bash
okf visualize ./okf_bundle viz.html
# Open viz.html in any browser
```

### Launch the live dashboard

```bash
okf dashboard ./okf_bundle --open
```

Opens a 3-panel FastAPI web UI at `http://127.0.0.1:8700` with search, detail inspection, and force-directed graphs.

---

## Agent Integration

### One command per agent

`okf install` writes the exact rules, instructions, and commands each agent needs. No manual configuration.

```bash
# Install for all detected agents at once
okf install all

# Or pick specific agents
okf install claude      # Claude Code skill (auto-triggers on "index my codebase")
okf install cursor      # Cursor rules (.cursorrules)
okf install copilot     # GitHub Copilot instructions
okf install windsurf    # Windsurf rules
okf install cline       # Cline rules
okf install opencode    # OpenCode /lookup command
okf install mcp         # Register MCP server (OpenCode + Claude Desktop)
```

### MCP server (11 tools)

Start an offline-first MCP server that exposes your knowledge bundle to any MCP client:

```bash
okf mcp ./okf_bundle --port 4567
```

Tools: `lookup`, `get_concept`, `find_callers`, `find_callees`, `list_by_file`, `list_dependencies`, `bundle_info`, `list_by_type`, `search_by_tag`, `get_related`, `get_manifest_source`.

Connect from **Cursor**, **Cline**, **Claude Desktop**, or any MCP-compatible IDE.

### Quick agent context

```markdown
Add to your agent instructions:
This project has an OKF knowledge bundle at ./okf_bundle/.
- Use `okf lookup <Name>` for full concept context.
- Use `okf lookup --type <Type>` to filter by type.
- Read `SUMMARY.md` for the full knowledge map.
```

---

## Comparison

### okf-generator vs RAG / vector search

| Capability | **okf-generator** | RAG / Vector Search |
|---|---|---|
| Retrieval | ✓ Precise AST lookup (exact symbols) | ~ Approximate (chunk similarity) |
| Token cost per lookup | ✓ **~140 tokens** | ~ Varies by chunk strategy |
| Cross-reference edges | ✓ Calls / called-by / imports | ✗ Not supported |
| Privacy | ✓ **100% offline**, no data leaves | ✗ Needs embeddings API (data may egress) |
| Search speed | ✓ **~3-4ms** (indexed) | ~ 200-500ms (embed + search) |
| Dependency manifest parsing | ✓ **17 formats** automatically | ✗ Not designed for this |
| CI/CD integration | ✓ **Built-in GitHub Action** + impact diff | ✗ Custom pipeline required |
| Training data export | ✓ **Built-in JSONL** pairs | ✗ Not a feature |
| Context compression | ✓ **~97% reduction** (45K→1.2K tokens) | ~ Varies by chunk strategy |
| Setup | ✓ **pip install + 1 command** | ⚠ Vector DB + embedding pipeline |

> Full comparison with Sourcegraph, Graphify/CodeSee, and dep-graph tools: **[docs/comparison.md](docs/comparison.md)**

---

## Enterprise & CI/CD

### Built-in GitHub Action

A pre-built workflow (`.github/workflows/okf-bundle.yml`) auto-generates the bundle on every push/PR to `main`, caches previous bundles per branch, diffs with `--impact`, and posts a PR comment showing which dependency changes affect which code:

```yaml
# .github/workflows/okf-bundle.yml
name: OKF Bundle
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install okf-generator
      - run: okf generate . okf_bundle
      - run: okf diff .okf_bundle_prev okf_bundle --impact
      - uses: actions/github-script@v7  # post/update PR comment
```

### Fine-tuning data export

Convert your bundle into JSONL training pairs for fine-tuning private local SLMs:

```bash
# 5 pair types: codegen, qa, doc, summarize, crosslink
okf pairs ./okf_bundle ./train.jsonl
```

### Docker image

```bash
docker pull ghcr.io/umairbaig8/okf-generator/okf-generator:latest
docker run ghcr.io/umairbaig8/okf-generator/okf-generator --help
```

### Pre-commit hook

Auto-regenerates the bundle when source files change — no stale knowledge graphs:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: okf-generate
        name: okf generate
        entry: okf generate
        language: system
        pass_filenames: false
```

> CI/CD guide + copy-paste workflow template: **[docs/user-guide/ci-cd.md](docs/user-guide/ci-cd.md)**

---

## CLI Reference

```bash
okf --help              Show available commands
okf <command> --help    Show options for a specific command
okf --version           Show version
```

| Command | Usage | Description |
|---|---|---|
| `generate` | `okf generate [src] [out] [--enrich]` | Scan codebase (auto-detects project root) |
| `lookup` | `okf lookup <query>` | Instant exact-symbol concept retrieval |
| `ask` | `okf ask <question>` | AI-powered Q&A about your codebase |
| `enrich` | `okf enrich <bundle> [--mode]` | LLM-enhance an existing bundle |
| `diff` | `okf diff <old> <new> [--impact]` | Compare two bundles, show dependency impact |
| `visualize` | `okf visualize <bundle> [out.html]` | Generate interactive D3 graph |
| `mcp` | `okf mcp <bundle> [--port]` | Start MCP server with 11 tools |
| `dashboard` | `okf dashboard <bundle> [--port]` | Launch FastAPI live bundle browser |
| `serve` | `okf serve [dir] [--port]` | Browse bundle via local HTTP server |
| `pairs` | `okf pairs <bundle> [output.jsonl]` | Export fine-tuning training pairs |
| `install` | `okf install [agent]` | Write agent integration rules/configs |
| `init` | `okf init [dir]` | Interactive wizard for bundle setup |
| `summarize` | `okf summarize <bundle>` | Regenerate SUMMARY.md for agents |
| `domains` | `okf domains` | List available domain classification rule sets |
| `plugin` | `okf plugin [list\|install\|uninstall]` | Manage external parser plugins |

> Full CLI reference: **[docs/cli-reference.md](docs/cli-reference.md)**

---

## FAQ

**Does this require an API key or internet connection?**
No. Core extraction (`okf generate`) is **fully offline and deterministic** — no LLM call is made unless you explicitly enable `--enrich`. All 18 language parsers use tree-sitter (or stdlib equivalent) and work completely air-gapped.

**How is this different from RAG / vector search?**
RAG retrieves chunks by semantic similarity, which is approximate and can miss exact symbols. `okf lookup` is **exact**: it indexes real functions, classes, modules, and dependencies by name and resolves to the precise concept, with zero embedding/vector infrastructure required. Same result every run.

**Does my proprietary code leave my local environment?**
**Never.** Core extraction runs 100% offline on your local CPU. No code or metadata is sent to any third-party cloud. Optional LLM enrichment can be enabled manually and works with self-hosted models or private enterprise APIs.

**Does this work on monorepos or very large codebases?**
Yes — scanning is linear in file count. Scope `okf generate` to a subdirectory if you only need part of the codebase indexed. Multi-bundle support visualizes cross-project edges.

**Can I use this without any LLM at all, ever?**
Yes. `okf generate` + `okf lookup` form a complete **zero-LLM workflow**. LLM enrichment and training-pair synthesis are optional layers on top — you can get full value without ever providing an API key.

**Is the bundle safe to commit to git?**
Yes — that's the intended workflow. Bundles are plain Markdown with YAML frontmatter — they diff cleanly, version alongside the code they describe, and can be reviewed in any code review tool.

---

## Contributing

```bash
git clone https://github.com/UmairBaig8/okf-generator
cd okf-generator
pip install -e ".[dev]"
pytest tests/ -q
```

**242+ tests passing.** See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## License

[MIT](LICENSE) — Copyright © 2026 Umair Baig

`okf-generator` produces OKF v0.2 bundles — an extended dialect of the [Open Knowledge Format (OKF) v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) by Google. Our v0.2 adds schema version, concept identity, language, status, and typed relationships to every concept file. Not affiliated with Google.
