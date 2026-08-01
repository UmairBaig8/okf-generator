# Architecture Overview

okf-generator converts source code into a structured knowledge bundle through a pipeline of discrete phases. This page documents how the pieces fit together.

## Pipeline

```
Source Code
    │
    ▼
┌─────────────┐
│   Scanner   │  Walk directories, identify files by extension
│  generator  │  Skip excluded dirs (node_modules, .venv, etc.)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Parsers   │  Per-language AST extraction via tree-sitter
│  parsers/*  │  Each file → Module concept + child concepts
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Manifest   │  Extract dependencies from requirements.txt,
│  Scanner    │  Cargo.toml, package.json, go.mod, etc. (20 formats)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Linker    │  Resolve imports → Dependency concepts
│  linker.py  │  Build call graph (calls ↔ called_by)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Writer    │  Write concept files + SUMMARY.md + index.md
│  generator  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Enrichment │  Optional LLM passes (base, deep, security, full)
│  generator  │  Multi-provider routing per mode
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Consume   │  lookup, diff, dashboard, MCP, pairs, visualize
└─────────────┘
```

## Key files

| File | Purpose |
|------|---------|
| `okf/generator.py` | Entry point: `scan_codebase()`, `write_bundle()`, enrichment passes |
| `okf/parsers/base.py` | `Concept` dataclass, `TreeSitterParser` base class, shared utilities |
| `okf/parsers/*.py` | One file per language — each extends `TreeSitterParser` |
| `okf/manifest_scanner.py` | 20 manifest format parsers (pip, npm, cargo, go, maven, etc.) |
| `okf/linker.py` | Two-pass linker: imports→dependencies, call graph |
| `okf/lookup.py` | Bundle loader, search/scoring, CLI |
| `okf/diff.py` | Bundle comparison + dependency impact analysis |
| `okf/pairs.py` | Training data export (5 pair types) |
| `okf/mcp_server.py` | Model Context Protocol server (7 tools) |
| `okf/dashboard.py` | FastAPI live bundle browser |
| `okf/serve.py` | Static HTTP server for viz |
| `okf/visualize.py` | Interactive HTML graph generator |
| `okf/config.py` | `.okfconfig` loading, defaults, provider registry |
| `okf/cli.py` | Unified CLI dispatcher |

## Scanner phase

`generator.py:scan_codebase()` walks the source directory tree, skipping excluded dirs (`SKIP_DIRS` in `parsers/base.py`). For each recognized file extension, it dispatches to the corresponding parser from the `EXTENSION_MAP` registry in `parsers/__init__.py`.

Unrecognized file types are silently skipped (logged in `log.md`).

## Parser phase

Each parser extends `TreeSitterParser` and implements:

| Method | Returns | Description |
|--------|---------|-------------|
| `_module_doc(root, src_bytes)` | `str` | Module-level docstring |
| `_parse_symbols(root, src_bytes, ...)` | `list[Concept]` | Extract functions, classes, etc. |
| `_collect_imports(root, src_bytes)` | `list[str]` | Import statements for dependency linking |
| `_collect_calls(node, src_bytes)` | `list[str]` | Call expressions for call graph |

The base class `parse_file()` wraps these into a `Module` concept + child concepts. Each child gets its `concept_id` derived from the relative file path + sanitized name.

## Manifest scanner

`manifest_scanner.py` detects manifest files by name (not extension). Supported formats: `requirements.txt`, `pyproject.toml`, `Cargo.toml`, `package.json`, `go.mod`, `Gemfile`, `pom.xml`, `build.gradle`, `composer.json`, `Package.swift`, `deps.edn`, `mix.exs`, `Dockerfile`, `Containerfile`, `docker-compose.yml`, `cpanfile`, `Brewfile`.

Each produces `Dependency` concepts with `body_extra` containing ecosystem, version constraint, and source manifest path.

## Linker phase

`linker.py:link_all()` runs two passes:

**Pass 1: `link_dependencies()`**
- Builds `dep_index: dict[(ecosystem, name)] → concept_id`
- For each Module's imports, normalizes the import name per-language
- Resolves against the dep index
- Sets `module.related` → dep concept_ids and `dep.body_extra["used_by"]` → module concept_ids

**Pass 2: `link_calls()`**
- For each function/method, collects call expressions via `_collect_calls()`
- Resolves each call to a concept_id (same-file → same-module → global)
- Ambiguous matches go to `possible_calls` (not guessed)
- Sets `calls` / `called_by` on concept objects

## Writer phase

`generator.py:write_bundle()` renders each `Concept` to a markdown file with:

- YAML frontmatter (`type`, `title`, `description`, `resource`, `tags`, `timestamp`)
- Markdown body (signature, docstring, parameters, returns, source, related, calls)
- Dependency concepts get a structured table (ecosystem, version, used_by)

Also writes `SUMMARY.md` (table of contents) and `index.md` (bundle metadata).

## Enrichment phase

Optional LLM passes run after writing. Each mode is resumable — already-enriched concepts are skipped:

| Mode | What it adds | Source body needed? |
|------|-------------|:---:|
| `base` | Improved descriptions, docstrings | ❌ |
| `deep` | Usage examples, side effects, security, complexity | ✅ |
| `security` | Security risk audit | ✅ |
| `full` | All above + semantic related-links | ✅ |

Each mode resolves its own provider via the config cascade: `enrich.{mode}.{key}` → `providers.{name}.{key}` → `llm.{key}`.

## Consume phase

| Tool | What it does |
|------|-------------|
| `okf lookup` | Search and retrieve concept cards |
| `okf diff` | Compare two bundles, trace dependency impact |
| `okf dashboard` | FastAPI live browser with search + interactive graph |
| `okf mcp` | MCP server for AI agents (7 tools) |
| `okf pairs` | Convert bundle to JSONL training pairs |
| `okf visualize` | Self-contained HTML graph viewer |
| `okf serve` | Static HTTP server for viz |

## Config system

`okf/config.py` manages `.okfconfig` with:

- Built-in `DEFAULTS` dict
- File loading from `.okfconfig` (cwd, walking up) → `~/.config/okf/config.json`
- Dot-notation access (`_get(cfg, "llm.base_url")`)
- Provider resolution cascade for enrichment routing
- `okf config` CLI for viewing and setting values

No environment variables are used — all configuration goes through the config file.
