# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.27] — 2026-07-02

### Added
- **Generics/type params** — extraction for Java, TypeScript, Rust, Go (1.18+), C++ (templates), C#. Each concept's `type_params` field captures `[T]`, `[T, U extends Comparable]`, etc.
- **Inheritance chain** — base class/interface extraction for Python, Java, TypeScript, C++, C#, Ruby. Each class concept shows `extends`/`implements`/inherits targets.
- **Decorators/Attributes** — extraction for Python (`@decorator`), Java (`@Annotation`), C# (`[Attribute]`), Rust (`#[derive]`). Captured as structured `decorators` field.
- **Method emission** — class methods now emitted as individual `Function` concepts for Python, JS/TS, C++ (Ruby already supported). ~2x more Function concepts from those languages.
- 22 new tests covering Tier 1 extraction across all 10 languages with real-world code fixtures.
- README language table updated with per-language extraction capabilities.

### Changed
- `Concept` dataclass: 3 new fields (`type_params`, `inheritance`, `decorators`).
- Java modifiers now use child iteration (no field name in grammar).
- C++ function methods no longer skipped — emitted as individual concepts.

---

## [0.1.28] — 2026-07-02

### Added
- **Tier 2 extraction:** Visibility modifiers (Java, C#, TS, Rust, C++), class fields/properties (Python, TS, Java, C#), TypeScript completeness (interfaces, type aliases, enums), SQL column/constraint extraction (PRIMARY KEY, NOT NULL, UNIQUE, DEFAULT, REFERENCES).
- **Realworld test fixtures:** 78 files, 3,545 lines, 20 projects (easy + complex per language) across 11 languages. Every extraction feature has fixture coverage.
- **test.sh runner:** `bash tests/test.sh` — 17 phases covering pytest, CLI generate/lookup/pairs/summarize/init/--help/--version, visualize, MCP server, serve, diff (v1→v2), edge cases. Generates `TEST_REPORT.html`.
- **C# parser:** `interface_declaration` and `struct_declaration` support (were silently skipped).
- Python `easy_v2` fixture for realistic versioned diff testing.

### Changed
- All tests migrated from `sample_codebase` (2 Python files) to `realworld` (78 files, 11 languages).
- Publish CI: smoke test now generates from realworld fixtures; test report attached to every GitHub Release.
- Viz code pane: "View Source" button in detail header, code card moved to top of detail panel.

### Removed
- `tests/fixtures/sample_codebase/` — no longer used.

---

## [0.1.26] — 2026-07-02

### Added
- `okf visualize` — bundle selector dropdown for multi-project monorepos.
- `okf visualize` — source code pane in concept detail view.
- `okf visualize` — resizable left sidebar via drag handle.
- Multi-bundle detection via `SUMMARY.md` subdirectory markers.
- 3 new docs: agent-integration, ci-cd, languages-and-manifests.

### Changed
- README rewritten with code-level knowledge graph pitch, local AI/SLM section,
  CI/CD pipeline section, and architectural query examples.
- Viz display name now dynamic — removed hardcoded `fresh_agentbox`.
- Docs assets reorganized into `images/`, `banners/`, `Demo deck/` directories.

### Fixed
- `okf visualize` always showed `fresh_agentbox` as title (both JS var + HTML span).
- Bundle detection used naive first-path-segment causing false bundles.

---

## [0.1.30] — 2026-07-02

### Changed
- PyPI `Homepage` now points to GitHub Pages landing page (`https://umairbaig8.github.io/okf-generator/`).
- README: added 🌐 Site badge linking to landing page.

---

## [0.1.29] — 2026-07-02

### Fixed
- Publish CI: MCP/serve tests now use HTTP mode with unique ports (19876/19877), portable `sed -i` for Linux/macOS.

---

## [0.1.31] — 2026-07-03

### Added
- **Structured doc tag parsing** — Javadoc `@param`/`@return`, JSDoc `@param {type}`/`@returns {type}`, YARD `@param [Type]` now populate structured `concept.params` and `concept.returns`. Applies to Java, JS/TS, Ruby.
- **Go const/var declarations** — package-level `const` and `var` bindings extracted as `Constant`/`Variable` concept types with type annotations and values.
- **Ruby singleton methods** — `def self.foo` extracted as `Function` concepts with `self.` prefix in signature and `singleton` visibility tag.
- **C++ full template signatures** — `template<typename T>` prefix now appears in class/function signatures (e.g. `template<typename T> class Container`).

### Changed
- `Concept` dataclass: 2 new concept types (`Constant`, `Variable`) added to index renderer.
- `GoParser` refactored: `_prev_comment` extracted once per node to avoid `UnboundLocalError` with new declaration types.

---

## [Unreleased]

### Planned
- **Plugin system** — `okf plugin install <lang>` to add parsers without modifying core

---

## [0.1.40] — 2026-07-07

### Added
- **Project root auto-detection** — `okf generate` can now be run without arguments. Walks up the directory tree looking for project markers (`pyproject.toml`, `Cargo.toml`, `package.json`, `go.mod`, `.git/`, etc.) across all languages. Falls back to current directory. (`okf/root_detector.py`)
- **Full mkdocs documentation site** — Restructured docs with dedicated pages for Installation, Quick Start, Configuration, CLI Reference, Bundle Format, Language Coverage, Agent Integration, MCP Server, LLM Enrichment, CI/CD, Visualization, Comparison, Troubleshooting, Architecture, Contributing, API Reference, Changelog. Material theme with dark/light toggle, navigation breadcrumbs, header auto-hide, announcement bar, section index pages.
- **Branding assets** — SVG logo family (light, dark, icon, white header variant), favicon, updated banner. Landing page: floating glass nav, 13→17 language pills, copy buttons on code blocks, auto-version badge from PyPI.
- **PyPI docs link** updated to point to mkdocs site.

### Changed
- Landing page tagline to "High-Velocity Codebase Parser"
- README and docs Home slimmed from 2000→350 words with grid cards and nav links
- Landing page and docs-site badges synced: added GitHub Stars, MCP Server, Cursor Ready, Claude Ready badges; removed rate-limited downloads badge
- Bundle Format documentation corrected to match actual code schema
- `extra.css` removed (was breaking toggle position)
- `edit_uri` removed (no edit button on docs)

---

## [0.1.39] — 2026-07-07

### Added
- **mkdocs documentation site** — `mkdocs.yml` with Material theme, organizes existing docs (CLI reference, agent integration, CI/CD, development, API) into a navigable portal. Run `mkdocs serve` for local preview, `mkdocs build` for static output.
- **Branding assets** — New SVG logo family (light, dark, icon) in `docs/images/` with project purple theme. Nav bar now shows the streaming-data icon.
- **Landing page copy buttons** — Clipboard icons on all step commands, agent install cards, enrichment commands, and code blocks.
- **Favicon** — `okf-icon.svg` linked in landing page `<head>`.
- **Auto-version badge** — Fetches latest release version from PyPI API.

### Changed
- Tagline updated to "HIGH-VELOCITY CODEBASE PARSER" across hero, meta description, README.
- Nav bar: floating glass island effect on scroll via GPU-composited transitions.
- Landing page language pills updated from 13→17 (added PHP, Dart, Scala, Julia).
- `pyproject.toml`: new optional dep group `[dashboard]` (fastapi, uvicorn), `[dev]` now includes mkdocs + mkdocs-material.
- `docs/index.md` created as symlink to root README for mkdocs compatibility.

---

## [0.1.38] — 2026-07-07

### Added
- **PHP parser** — `okf/parsers/php.py` extracts classes, interfaces, traits, enums, functions, methods, visibility, typed params, return types, PHPDoc blocks. Fixtures at `tests/fixtures/realworld/php/{easy,complex}/`. 3 new fixture tests.
- **Dart parser** — `okf/parsers/dart.py` extracts classes, mixins, enums, functions, constructors, methods. Fixtures at `tests/fixtures/realworld/dart/{easy,complex}/`. 3 new fixture tests.
- **Scala parser** — `okf/parsers/scala.py` extracts classes, objects, traits (→Interface), enums, functions, methods, visibility, typed params. Fixtures at `tests/fixtures/realworld/scala/{easy,complex}/`. 3 new fixture tests.
- **Julia parser** — `okf/parsers/julia.py` extracts functions, structs (→Class), abstract types (→Interface), constants, macros. Fixtures at `tests/fixtures/realworld/julia/{easy,complex}/`. 3 new fixture tests.
- **Web dashboard** — `okf dashboard <bundle_dir>` launches a FastAPI-based live bundle browser. Search/filter concepts, view full detail (signature, params, docstring, source), explore interactive dependency graph per concept. API endpoints: `/api/info`, `/api/types`, `/api/languages`, `/api/search`, `/api/concept/{id}`, `/api/graph`. Optional dep: `pip install "okf-generator[dashboard]"`.

### Changed
- Language coverage expanded from 13→17 languages (added PHP, Dart, Scala, Julia).
- `tests/test_realworld_fixtures.py`: 61 total tests (12 new for 4 new languages).
- Fixture corpus: 106 files across 17 languages, 28 projects.

---

## [0.1.37] — 2026-07-07

### Added
- **`okf diff --impact`** — dependency impact analysis traces changed deps → affected modules → downstream functions/classes. Uses `## Used By` sections from existing bundles. Output: hierarchical tree or JSON (with `--json`). No new data required — `used_by` already populated by linker.
- **MCP tool polish** — `get_concept` (full detail by concept_id), `find_callers` (citators via `## Related` link scanning), `list_by_file` (concepts by source file path). Enhanced `lookup` with `detail=true` param for full output (signature, params, source). Structured error handling for missing/invalid args. 6 new MCP protocol tests.
- **GitHub Action** — `.github/workflows/okf-bundle.yml`: auto-generates OKF bundle on push/PR to main. Caches previous bundle per branch, diffs with `--compact` + `--impact`, posts/updates single PR comment showing changes and dependency impact. Restores main branch cache for PR comparison.

### Changed
- `okf/diff.py` refactored: `diff_bundles()` accepts optional pre-loaded concept lists to avoid double load when `--impact` is used.
- `okf/mcp_server.py` refactored: tool dispatch via `_dispatch()` with structured `ToolError` for validation.
- `tests/test_diff.py`: 11 total tests (6 new for impact analysis).
- `tests/test_mcp.py`: 11 total tests (6 new for MCP new tools + validation).

---

## [0.1.36] — 2026-07-05

### Added
- **Modular parser architecture** — All 13 language parsers extracted from `generator.py` into `okf/parsers/` (one file per language). Adding a new language is a single file + single registry entry. See `docs/development.md`.
- **`okf enrich` command** — Standalone enrichment of an existing bundle without re-scanning. Reads `source_root` from bundle `index.md` frontmatter (stored at generate time). Usage: `okf enrich <bundle_dir> [--mode base|deep|security|full]`.
- **Enrichment mode selection** — `--enrich` now accepts mode qualifiers: `--enrich base` (descriptions/docstrings), `--enrich deep` (+usage examples, side effects, security, complexity), `--enrich security` (risk audit only), `--enrich full` (all passes). Backward compatible — plain `--enrich` defaults to `base`.
- **`--security` standalone mode** — `okf generate --security <source_dir> <bundle_dir>` audits security/complexity on an existing bundle. Uses `_upsert_section()` for surgical file patching — only touches Security/Complexity sections, leaves all others intact.
- **Semantic related-links pass** — `enrich_related_semantic()` uses LLM to find relevant cross-links beyond the call graph. Gated behind `enrich.semantic_related.enabled`. Includes deterministic candidate pre-filtering (`_candidate_pool()`) to keep prompt sizes bounded.
- **`source_root` stored in bundle metadata** — `render_root_index()` writes `source_root` to `index.md` frontmatter. `_read_source_root()` reads it back. `_read_body()` falls back to bundle metadata when no source dir is provided.
- **`_get()` multi-level dot-notation** — now supports arbitrary depth (e.g. `enrich.deep.provider`).
- **Anthropic SDK support** — `_resolve_client()` uses `anthropic.Anthropic` for "anthropic" provider, `openai.OpenAI` for all others.
- **`docs/development.md`** — New developer guide with full parser onboarding walkthrough, method reference table, and shared utilities index.
- **7 new unit tests** — provider resolution cascade, per-mode overrides, built-in provider lookups, multi-level `_get`.
- **6 new CLI test scenarios in TEST.md** — `okf enrich` modes and `--enrich` mode qualifier validation.

### Changed
- `generator.py` reduced from 3509 to ~1630 lines — all parsers extracted to `okf/parsers/`. Remaining code (rendering, enrichment, scanning, writer, main) is focused and readable.
- `Concept` dataclass moved to `okf/parsers/base.py` — re-exported from `generator.py` for backward compat.
- `config.py` DEFAULTS now includes `providers.*` and `enrich.*` sections. Default LLM provider changed to `"local"`.
- `load()` uses `copy.deepcopy(DEFAULTS)` instead of mutable reference merge — fixes test isolation.
- `DEEP_ENRICH_PROMPT` expanded from 2 fields to 4 (usage_example, side_effects, security, complexity). `max_tokens` bumped 350→500.
- `_read_body()` now accepts optional `bundle_dir` parameter for body-dependent passes without a source directory argument.
- CLI docstring updated to document `--enrich` modes and `okf enrich` command.
- README updated: new Enrichment Modes section, multi-provider routing config example, modular parsers table with file paths, comparison table with 2 new rows, FAQ links to `docs/development.md`.
- Version bumped to `0.1.36`.

---

## [0.1.35] — 2026-07-05

### Added
- **Named provider registry** — `okf/config.py` now ships built-in provider presets (`anthropic`, `openai`, `deepseek`, `gemini`, `glm`, `openrouter`, `dashscope`, `minimax`, `ollama`, `lmstudio`, `local`) with default `base_url`s. Users reference by name instead of repeating URL+model.
- **Per-mode provider routing** — `enrich.description`, `enrich.deep`, `enrich.security`, and `enrich.semantic_related` each resolve their own provider independently. Resolution cascade: `enrich.{mode}.{key}` → `providers.{name}.{key}` → `llm.{key}`.
- **LLM enrichment extensions** — `enrich_concept()` now also sets `design_pattern` and LLM-suggested semantic `tags` (merged, deduped). New `enrich_concept_deep()` second pass (gated behind `enrich.deep.enabled`) reads actual source body via `source_lines` to produce `usage_example`, `side_effects`, `security`, `complexity`.
- **Deterministic deprecation detection** — `_detect_deprecation()` uses regex over docstring+decorators, no LLM call needed.
- **`_get()` multi-level dot-notation** — now supports arbitrary depth (e.g. `enrich.deep.provider` resolves correctly).
- **Anthropic SDK support** — `_resolve_client()` uses `anthropic.Anthropic` for `"anthropic"` provider, `openai.OpenAI` for all others.
- **7 new unit tests** — provider resolution cascade, per-mode overrides, built-in provider lookups, multi-level `_get`.

### Changed
- `config.py` DEFAULTS now includes `providers.*` and `enrich.*` sections. Default LLM provider changed to `"local"`.
- `load()` uses `copy.deepcopy(DEFAULTS)` instead of mutable reference merge — prevents config file loads from mutating module-level defaults (fixes test isolation).
- `enrich_concept()` now also accepts `inheritance` context in prompt, `max_tokens` bumped 300→400.
- Version bumped to `0.1.35`.

---

## [0.1.34] — 2026-07-03

### Added
- **Fuzzy search** — camelCase/snake_case tokenization, acronym matching (`okf lookup repo` finds `UserRepository`). New `--exact` flag for strict title-only matching.
- **Dockerfile + Containerfile + docker-compose.yml parsers** — `FROM` → docker dep with tag, `RUN pip install` → pip dep with version, `image:` and `depends_on:` for compose services.
- **LLM enrichment CLI** — `okf generate --enrich` activates LLM description/docstring enrichment. Gracefully skips when no API key is configured.
- **`.okfconfig` config system** — extensible flat + sectional config (global `bundle_dir`, feature sections `llm.*`, `serve.*`, `lookup.*`, `mcp.*`, `pairs.*`). No environment variables. `okf config` CLI to view/edit. `okf init` prompts for config interactively.
- **Pre-commit hook** — `.pre-commit-config.yaml` includes `okf-generate` hook that auto-regenerates bundle when source files change.
- **Docker image** — `Dockerfile` + GHCR publish workflow on release.
- **Live Demo** button on landing page with CI-published visualization.

### Changed
- Config system migrated from env vars to `.okfconfig` file. All `os.environ` lookups removed from generator, pairs, serve, lookup, and init.
- Default LLM endpoint changed to `http://localhost:8080/v1` (local-first, works with llama.cpp/Ollama out of the box).
- `okf init` wizard now prompts for config (LLM provider, model, API key) before generating bundle.
- RELEASE.md expanded with 15-point pre-release audit including feature validation and landing page freshness checks.
- README.md feature table updated with fuzzy search, Dockerfile/compose, config, pre-commit, Docker image rows.

---

## [0.1.33] — 2026-07-03

### Fixed
- `pyproject.toml` — added missing `tree-sitter-swift` and `tree-sitter-kotlin` dependencies (CI workflows were failing to install them).
- CI workflows — added Rust toolchain setup for building `tree-sitter-kotlin` from source on Linux runners.
- `visualize.py` — guarded `PermissionError` in source code file lookup (was crashing on CI when scanning `/tmp/` siblings).
- GitHub Pages deployment — fixed by resolving CI failures; `docs/viz.html` now auto-deploys.

---

## [0.1.32] — 2026-07-03

### Added
- **Swift parser** — tree-sitter based: classes, structs, enums, protocols (→ Interface), generics, methods, functions, typealiases. Full field extraction, protocol conformance, associated types.
- **Kotlin parser** — tree-sitter based: classes, data classes, interfaces, objects, enums, generics, functions, typealiases. Constructor parameter field extraction, visibility modifiers.
- **18 new fixture files** — `realworld/swift/{easy,complex}/` and `realworld/kotlin/{easy,complex}/` (8 files) covering generics, protocols/interfaces, enums, data classes. Plus `complex/src/app.swift` and `complex/src/app.kt`.
- **8 new test cases** — dedicated parser unit tests (`test_swift_parser_*`, `test_kotlin_parser_*`) and realworld feature tests (protocols, generics, interfaces, data class fields).
- **viz detail page overhaul** — Prism.js syntax highlighting (Tomorrow dark theme), slide-in code panel showing only relevant lines, 2×2 compact section grid, meta-tag pills for visibility/decorators, type stacked above concept name.
- **Live Demo button** on landing page — `docs/index.html` hero section links to interactive bundle viz.
- **GitHub Actions workflow** — `.github/workflows/demo-viz.yml` auto-regenerates `docs/viz.html` from realworld fixtures on push to main or release.
- **Bundle dropdown fix** — moved to sidebar above type filter, statically populated (no JS duplication).

### Changed
- `_viz_template.py` — from `const` to `var` declarations for data/BUNDLES/BUNDLE_NAME (fixes JS scope in IIFE).
- `visualize.py` — source code resolution searches sibling directories and sub-bundle dirs; structured `visibility`/`decorators`/`inheritance`/`type_params` fields parsed from bundle sections.

---

## [0.1.25] — 2026-07-02

### Added
- **10 languages** — C, C++, C# tree-sitter parsers (was 7).
- **17 manifest formats** — `yarn.lock` and `pnpm-lock.yaml` parsers.
- `okf mcp` — MCP server for Claude Desktop, Cursor, and any MCP client.
- `okf init` — interactive wizard with REPL commands (`/lookup`, `/viz`, `/serve`, `/deps`, `/install`).
- `okf serve` — local HTTP server with auto-redirect to viz.
- `okf diff` — bundle comparison (added/removed/changed).
- `okf lookup --deps` — shortcut for `--type Dependency`.
- `okf generate` progress bar via `tqdm`.
- CLI banner (compact dashboard style with version).
- Lookup cache for instant repeat queries.

### Changed
- README updated: 10 languages, 17 manifests, 7 consume commands, new demo GIF.

### Fixed
- `okf visualize` — embedded template (no more `demo.html` not found on PyPI).
- `source_lines` end was hardcoded to 0 — now uses `node.end_point`.

---

## [0.1.24] — 2026-07-02

### Added
- `okf serve [dir] [--port] [--open]` — launch a local HTTP server for any bundle directory. Zero dependencies, auto-detects visualization HTML.
- `okf/_viz_template.py` — embedded HTML template (base64) so `okf visualize` works from PyPI without external files.

### Fixed
- `okf visualize` no longer fails with `demo.html not found` when installed from PyPI — template is now bundled inside the package.

---

## [0.1.23] — 2026-07-02

### Added
- **10 languages** — C, C++, C# tree-sitter parsers (was 7). Each supports functions, classes/structs, and doc comments.
- **17 manifest formats** — `yarn.lock` and `pnpm-lock.yaml` parsers added (was 15).
- `okf lookup --deps` — shortcut for `--type Dependency`.
- `okf generate` progress bar — `tqdm` wraps the scan loop, visible on 500+ file repos.
- `okf visualize` — "generated by okf" link in topbar.
- `okf install` — prompts before overwriting existing agent config files.

### Changed
- README: language count 7→10, manifest count 15→17, new features section.
- 85 tests (was 76) covering C/C++/C# parsers, lock file parsers.

---

## [0.1.22] — 2026-07-01

### Fixed
- `okf visualize`: edges now correctly extracted from `## Related`, `## Calls`, `## Called By`, and `## Used By` sections (was always 0).
- `okf visualize`: dependency detail panel now shows ecosystem/version/dev table.
- `okf visualize`: full markdown body rendering via `marked.js` with internal link rewiring.
- `okf visualize`: CDN switched from `unpkg.com` (broken) to `cdn.jsdelivr.net`.

### Changed
- `okf visualize`: upgraded from D3.js to Cytoscape.js with 4 layouts (Graph, Circle, Grid, Tree), type filter, search, and detail panel.

---

## [0.1.21] — 2026-07-01

### Added
- `okf visualize <bundle_dir>` — generates a self-contained interactive HTML graph of any OKF bundle using D3.js force-directed layout. Color-coded by concept type, searchable, with relationship edges (calls, imports, related). No server or install required.

### Changed
- README restructured: demo GIF at top, feature cards, installation earlier, moved CLI reference and Python API to `docs/` subpages.
- Banner updated to `docs/banner.png`.
- New demo GIF with real `okf` output.

---

## [0.1.20] — 2026-07-01

### Changed
- README restructured as landing page: demo GIF moved to top, feature cards, installation earlier, CLI reference and Python API moved to `docs/` subpages.
- Banner updated to `docs/banner.png`.
- Mermaid flowchart: removed `<br/>` tags for GitHub compatibility, added plain-text fallback.
- Added system prompt template and token efficiency table for AI agent integrators.
- TEST.md now installs with `[dev,llm]` extras (ruff available for lint step).

---

## [0.1.19] — 2026-07-01

### Added
- `okf install [agent]` — unified agent setup. Install integration for Claude Code, OpenCode, Copilot, Cursor, Windsurf, or Cline with a single command. Replaces `okf install-skill`.
- **Bumblebee supply-chain scan** — pre-commit hook (`.pre-commit-config.yaml`) and CI job scans dependencies for known compromises via `bumblebee scan --findings-only`.
- AI agent instructions made forceful: AGENTS.md and `.github/copilot-instructions.md` now lead with "CRITICAL RULE: Never grep source files first, always run `okf lookup`".
- AI-assisted pre-release audit section in RELEASE.md.

### Changed
- `.github/copilot-instructions.md` — detailed lookup patterns for Copilot users.
- README: unified "Agent Installation" section replacing "Claude Skill" section.

---

## [0.1.18] — 2026-07-01

### Added
- Lock file parsers: `Cargo.lock` (Rust), `go.sum` (Go), `poetry.lock` (Python Poetry) — each dependency becomes a `Dependency` concept alongside the existing manifest formats.
- `okf generate --exclude <dir>` — skip directories per-run without editing `SKIP_DIRS`. Repeatable: `--exclude tests --exclude docs`.
- `okf diff <old> <new>` CLI subcommand — compares two bundles via content hash, prints added/removed/changed concepts. Supports `--compact` and `--json`.

### Fixed
- `go.sum` parser: skips `/go.mod` checksum lines and deduplicates module+version pairs.

---

## [0.1.17] — 2026-07-01

### Added
- `okf --version` flag — prints version and exits.

### Fixed
- `source_lines` end was hardcoded to `0` in `_make_concept` — now uses `node.end_point` so every concept shows correct end line number.
- SQL Function concepts now pass `node` to `_make_concept`, fixing their `source_lines` end (was `0`).

### Changed
- README: cross-reference linker documentation under "How it works". SQL parser updated from regex to tree-sitter. `--version` added to CLI reference.
- `TEST.md`: added ruff lint check (Phase 1.1).

---

## [0.1.16] — 2026-07-01

### Changed
- SQL parser: replaced regex-based scanner with `tree-sitter-sql` grammar, following the same `TreeSitterParser` base class as the other 6 code languages. Reduces false positives on multi-statement or dialect-specific SQL, and adds source line numbers, proper SQL signatures, and preceding-comment extraction.

---

## [0.1.15] — 2026-07-01

### Added
- Cross-reference linker (`okf/linker.py`) — resolves imports → dependency edges and function calls → caller/callee edges across all 7 code languages. Each concept now shows **Calls**, **Called By**, and **Used By** in its markdown body.
- `Concept` dataclass: `imports`, `calls_raw`, `calls`, `called_by` fields.
- Per-language import/call collectors for Python (AST), JavaScript, TypeScript, Go, Java, Rust, Ruby.

---

## [0.1.14] — 2026-07-01

### Fixed
- README images now use absolute `raw.githubusercontent.com` URLs so they render on PyPI.
- Banner switched to `banner_v2.svg`.

---

## [0.1.13] — 2026-07-01

### Fixed
- Tip text in `okf lookup` output now shows `okf lookup ...` instead of `python okf_lookup.py`.

### Changed
- README: added `before_after.svg` comparison image and `demo.gif` terminal recording.

---

## [0.1.12] — 2026-06-30

### Fixed
- Lint errors: `E402` (import order in `lookup.py`), `W291`/`W292` (trailing whitespace + missing newline in `manifest_scanner.py`).
- Publish smoke test: `--json` query now uses `--limit 200` to avoid 10-result default truncation.

### Changed
- README: added manifest formats table (12 parsers), lookup cache feature, `_dependencies/` folder layout, Dependency type in lookup reference.

---

## [0.1.11] — 2026-06-30

### Added
- Manifest scanner (`okf/manifest_scanner.py`) — 12 parsers: `requirements.txt`, `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `composer.json`, `pom.xml`, `Gemfile`, `build.gradle`, `Package.swift`, `project.clj`, `mix.exs`. Each dependency becomes a `Dependency` concept with ecosystem/version/dev-flag metadata.
- `_dependencies/{ecosystem}/{name}.md` folder structure in bundles — organized by ecosystem (pip, npm, cargo, etc.) with navigable `index.md` per subfolder.
- `SUMMARY.md` now has a **Dependencies** section with compact ecosystem counts and a link to `_dependencies/index.md`.
- Publish smoke test — CI installs the published wheel from PyPI, runs `generate` + `lookup` + `pairs` + `summarize` end-to-end.
- `RELEASE.md` — release checklist.
- `TEST.md` — full integration test spec (AI-agent-executable).
- `CLAUDE.md` — Claude Code project context.

### Changed
- Bundle `index.md` pluralization: `## Dependencies` (not `## Dependencys`).
- `CONTRIBUTING.md` — new sections for manifest parsers, integration spec, AI agent usage.
- README broadened from "OpenCode" to **any AI agent** — Cursor, Windsurf, Cline, Copilot badges + per-agent integration instructions.
- `AGENTS.md` — comprehensive agent instructions with custom commands.

### Fixed
- Manifest concept tags now preserve `ecosystem:`, `manifest:`, `version:` tags alongside standardised `lang:`/`type:`/`module:` tags.
- `parse_mix_exs` return typo (`depsreview` → `deps`).

---

## [0.1.10] — 2026-06-30

### Added
- Lookup cache — `load_bundle()` now auto-caches parsed concepts to `.okf_lookup_cache.json`. Subsequent lookups skip re-parsing all `.md` files unless bundle changed (mtime fingerprint). ~1.8x faster on 220-concept bundle, scales better on larger bundles.
- `--no-cache` flag to bypass cache for debugging.

### Changed
- `.gitignore` — ignores `.okf_lookup_cache.json`.

---

## [0.1.9] — 2026-06-30

### Added
- SQL parser (`.sql`) — extracts `CREATE TABLE`/`VIEW`/`FUNCTION`/`PROCEDURE`/`INDEX` as concepts via a dialect-tolerant regex scanner (no LLM, no fragile tree-sitter-sql grammar dependency). Preceding `--` and `/* */` comments become the concept description.
- `CODE_OF_CONDUCT.md`, `SECURITY.md` — community and security documentation.

### Changed
- Banner SVG updated — added SQL pill, language count bumped to 7.
- CI: Python 3.13 added to test matrix.
- CI: Auto GitHub Release on tag push via `publish.yml`.
- `pyproject.toml` — repository URL casing fix, added `Changelog` URL.
- `CONTRIBUTING.md` — deduplicated good-first-issues list.
- Various formatting cleanup in `lookup.py`, `pairs.py`, `generator.py`.

### Fixed
- `migrations/` removed from default `SKIP_DIRS` — most SQL lives in migrations, and skipping it silently dropped an entire codebase domain.
- Empty/unsupported source directories no longer hard-exit (`sys.exit(1)`) — `okf generate` on an empty folder now writes a valid (empty) bundle instead of failing.
- Directories with no extractable concepts no longer disappear from the bundle — they still get an `index.md` and show up in parent subdirectory listings.
- `write_summary` no longer crashes (`IndexError`) when a bundle has zero domains.

---

## [0.1.8] — 2026-06-29

### Fixed
- JS/TS parser cache poison — `_lang_obj` class attribute leaked TypeScript grammar into subsequent JS parses (H3)
- `okf pairs` `_lang()` never matched tags — tags stored as `lang:python` but checked bare `python` (H4)
- Go interfaces stamped as `Class` instead of `Interface` (H1)
- LLM enrichment crash on `None` API response — `.strip()` on nullable `message.content` (H7)
- Version drift — `cli.py` hardcoded `v0.1.6+`, `__init__.py` had stale 0.1.6 (H6)
- Fence hardcoded to `python` in concept signatures — now uses actual concept language
- `_sig()` only stripped ````python` fences — regex now strips any language fence
- Bare `except:` at 6 locations (captured `KeyboardInterrupt` etc.) → `except Exception:`
- Dead `if/else` in `_concept_output_path` — both branches identical

### Changed
- Unused imports removed: `hashlib`, `dedent`, `Optional`
- `defaultdict` import hoisted from function to module level
- `f.flush()` after every `f.write()` in `okf pairs` for crash-safe partial output

---

## [0.1.7] — 2026-06-29

### Added
- One-liner curl install: `curl -fsSL https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/scripts/install.sh | bash`
- `scripts/install.sh` — installs okf-generator + Claude Code skill in one shot

### Changed
- README badges fixed — test badge URL now uses correct repo case (`UmairBaig8`)
- README install section leads with the one-liner

### Fixed
- `tqdm` missing import in `generator.py:1583` — crashed on any `OKF_ENRICH=1` run

---

## [0.1.6] — 2026-06-29

### Added
- `okf install-skill` command — copies SKILL.md to `~/.config/opencode/skills/okf-generator/`

---

## [0.1.5] — 2026-06-29

### Changed
- README updated with curl-based Claude skill install instructions

---

## [0.1.4] — 2026-06-29

### Changed
- OpenCode integration guide and skill docs updated for `okf` CLI

---

## [0.1.3] — 2026-06-29

### Fixed
- Skip dirs check against relative path instead of absolute
- Stale import causing `ModuleNotFoundError` on fresh install

---

## [0.1.2] — 2026-06-29

### Fixed
- Absolute URL for banner image in README

---

## [0.1.1] — 2026-06-29

### Changed
- Initial PyPI release plumbing

---

## [0.1.0] — 2026-06-29

### Added
- `okf generate` — scan a codebase and produce an OKF v0.1 bundle
- `okf lookup` — zero-LLM concept search (exact, fuzzy, by file, type, tag)
- `okf pairs` — convert bundle to JSONL training pairs (codegen, qa, doc, summarize, crosslink)
- `okf summarize` — regenerate SUMMARY.md from an existing bundle
- Python parser via stdlib `ast` — functions, classes, params, return types, docstrings
- JS/TypeScript parser via tree-sitter — functions, arrow fns, classes, JSDoc
- Go parser via tree-sitter — funcs, methods, structs, interfaces, GoDoc
- Java parser via tree-sitter — classes, methods, constructors, Javadoc
- Rust parser via tree-sitter — fns, structs, enums, traits, impl blocks, doc comments
- Ruby parser via tree-sitter — defs, classes, modules, hash comments
- Domain/resource-path bundle layout mirroring the source tree
- Resumable LLM enrichment (skips already-enriched concepts on rerun)
- Standardised OKF tags: `lang:`, `type:`, `module:`, `domain:`, `git:branch:`, `git:repo:`
- SUMMARY.md with stats table, domain map, key concepts, OpenCode usage snippet
- `SKILL.md` for use as a Claude skill
- OpenCode integration guide
- 32 passing tests

[Unreleased]: https://github.com/UmairBaig8/okf-generator/compare/v0.1.40...HEAD
[0.1.40]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.40
[0.1.39]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.39
[0.1.38]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.38
[0.1.37]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.37
[0.1.36]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.36
[0.1.35]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.35
[0.1.34]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.34
[0.1.33]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.33
[0.1.32]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.32
[0.1.31]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.31
[0.1.30]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.30
[0.1.29]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.29
[0.1.28]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.28
[0.1.27]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.27
[0.1.26]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.26
[0.1.25]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.25
[0.1.24]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.24
[0.1.23]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.23
[0.1.22]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.22
[0.1.21]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.21
[0.1.20]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.20
[0.1.19]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.19
[0.1.18]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.18
[0.1.17]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.17
[0.1.16]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.16
[0.1.15]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.15
[0.1.14]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.14
[0.1.13]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.13
[0.1.12]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.12
[0.1.11]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.11
[0.1.10]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.10
[0.1.9]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.9
[0.1.8]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.8
[0.1.7]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.7
[0.1.6]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.6
[0.1.5]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.5
[0.1.4]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.4
[0.1.3]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.3
[0.1.2]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.2
[0.1.1]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.1
[0.1.0]: https://github.com/UmairBaig8/okf-generator/releases/tag/v0.1.0
