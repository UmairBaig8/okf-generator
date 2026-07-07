# Changelog

All notable changes to okf-generator. Versions follow [SemVer](https://semver.org/).

For the raw commit list, see [GitHub Releases](https://github.com/UmairBaig8/okf-generator/releases).

---

## [Unreleased]

- (add entries here as features land)

---

## v0.1.39 — 2026-07-07

### Added
- mkdocs documentation site with Material theme
- Branding assets: SVG logo family (light, dark, icon), favicon
- Copy buttons on all landing page code blocks
- Auto-version badge from PyPI API

### Changed
- Landing page: floating glass nav, 13→17 language pills
- Tagline: "High-Velocity Codebase Parser"

---

## v0.1.38 — 2026-07-07

### Added
- PHP parser (classes, interfaces, traits, enums, functions, typed params, PHPDoc)
- Dart parser (classes, mixins, enums, constructors, methods)
- Scala parser (classes, objects, traits→Interface, enums, visibility)
- Julia parser (functions, structs→Class, abstract→Interface, constants, macros)
- Web dashboard — `okf dashboard` (FastAPI + interactive graph, 6 API endpoints)

### Changed
- Language coverage expanded 13→17 languages
- Fixture corpus: 106 files across 17 languages, 28 projects

---

## v0.1.37 — 2026-07-07

### Added
- `okf diff --impact` — dependency impact analysis
- MCP tool polish: `get_concept`, `find_callers`, `list_by_file`, `detail=true`, structured error handling
- GitHub Action — `.github/workflows/okf-bundle.yml` (auto-bundle + PR comments)

### Changed
- `diff_bundles()` accepts pre-loaded concept lists (avoids double load with `--impact`)
- `mcp_server.py`: tool dispatch via `_dispatch()` with `ToolError` validation
- 6 new MCP tests, 6 new impact analysis tests

---

## v0.1.36 — 2026-07-05

### Added
- Modular parser architecture — 13 parsers extracted to `okf/parsers/` (one file per language)
- `okf enrich` standalone command (no re-scan needed)
- Enrichment mode selection: `--enrich base|deep|security|full`
- Semantic related-links pass
- `source_root` stored in bundle metadata
- Anthropic SDK support
- `docs/development.md` developer guide

### Changed
- `generator.py` halved 3509→1630 lines
- `Concept` dataclass moved to `okf/parsers/base.py`
- `_read_body()` accepts optional `bundle_dir` parameter

---

## v0.1.35 — 2026-07-05

### Added
- Named provider registry (11 presets: anthropic, openai, deepseek, gemini, etc.)
- Per-mode provider routing — each enrich mode resolves its own provider
- LLM deep enrichment: usage examples, side effects, security, complexity
- Deterministic deprecation detection via regex
- Anthropic SDK support

### Changed
- Default LLM provider changed to `"local"`
- `load()` uses `copy.deepcopy(DEFAULTS)` for test isolation

---

## v0.1.34 — 2026-07-03

### Added
- Fuzzy search — camelCase/snake_case tokenization, acronym matching, `--exact` flag
- Dockerfile + Containerfile + docker-compose.yml parsers
- LLM enrichment CLI — `okf generate --enrich`
- `.okfconfig` config system (no env vars)
- Pre-commit hook for auto bundle regeneration
- Docker image + GHCR publish workflow

### Changed
- Config migrated from env vars to `.okfconfig` file
- Default LLM endpoint changed to `http://localhost:8080/v1`
- `okf init` wizard prompts for LLM config

---

## v0.1.33 — 2026-07-02

### Added
- 12-manifest dependency scanner (pip, npm, cargo, go, maven, gradle, rubygems, composer, swiftpm, clojars, hex)
- Two-pass dependency-to-code linker (`okf/linker.py`)
- Conservative call graph resolution with `possible_calls`

### Changed
- Dependency concept IDs standardized under `_dependencies/{ecosystem}/`

---

## v0.1.32 — 2026-07-02

### Added
- `okf visualize` — interactive HTML bundle browser
- Multi-bundle detection via `SUMMARY.md` subdirectory markers

### Fixed
- Viz always showed hardcoded bundle title

---

## v0.1.31 — 2026-07-03

### Added
- Structured doc tag parsing: Javadoc `@param`/`@return`, JSDoc, YARD
- Go const/var declarations extraction
- Ruby singleton method detection
- C++ full template signatures

---

## v0.1.30 — 2026-07-02

### Changed
- PyPI homepage points to GitHub Pages landing page

---

## v0.1.29 — 2026-07-02

### Fixed
- Publish CI: portable `sed -i` for Linux/macOS, unique ports for MCP/serve tests

---

## v0.1.28 — 2026-07-02

### Added
- Tier 2 extraction: visibility modifiers, class fields/properties
- SQL column/constraint extraction (PRIMARY KEY, NOT NULL, UNIQUE, DEFAULT, REFERENCES)
- Realworld test fixtures: 78 files, 11 languages, 20 projects
- `test.sh` runner (17 phases, generates TEST_REPORT.html)
- C# interface and struct support

---

## v0.1.27 — 2026-07-02

### Added
- Generics/type params extraction (Java, TypeScript, Rust, Go 1.18+, C++, C#)
- Inheritance chain extraction (base class/interface)
- Decorator/attribute extraction (Python, Java, C#, Rust)
- Method emission — class methods emitted as individual Function concepts

---

## v0.1.26 — 2026-07-02

### Added
- `okf visualize` — D3.js force-directed graph
- Bundle selector for multi-project monorepos
- Resizable left sidebar in viz
- Agent integration docs

---

## Earlier versions (v0.1.1 — v0.1.25)

- Initial multi-language parsing via Python AST + tree-sitter (Python, JS/TS, Go, Java, Rust, Ruby, C, C++, C#, SQL)
- `okf generate`, `okf lookup`, `okf pairs`, `okf summarize`, `okf init`, `okf diff`
- MCP server — 7 tools
- Lookup cache with mtime fingerprinting
- LLM enrichment passes (base, deep, security, full)
- Training data export (5 pair types)
- Agent integration (Claude, Cursor, Copilot, Windsurf, Cline, OpenCode)

---

## Upgrading

```bash
pip install --upgrade okf-generator
```

Bundles remain readable across minor versions — the bundle format is additive. Regenerate after upgrading to pick up new concept types or fixed extraction bugs.
