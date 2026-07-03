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
- **Fuzzy search** — `okf lookup` with substring/prefix/fuzzy matching (not just exact token match)
- **LLM enrichment CLI** — `okf generate --enrich` with configurable model, resumable per-concept
- **More manifest formats** — Dockerfile (base images, env vars), docker-compose.yml, .editorconfig, .gitmodules
- **GitHub Action** — marketplace action to auto-generate bundle on push, PR comments with dep diffs
- **Dependency impact analysis** — `okf diff --impact` traces which concepts depend on changed deps
- **Web dashboard** — FastAPI-powered live bundle browser beyond static viz.html
- **Docker image** — `docker pull okf/okf-generator` for CI without Python toolchain
- **Pre-commit hook** — auto-update `.okf_bundle` on commit
- **Plugin system** — `okf plugin install <lang>` to add parsers without modifying core
- **mkdocs documentation site**

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

[Unreleased]: https://github.com/UmairBaig8/okf-generator/compare/v0.1.33...HEAD
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
