# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- C# / Swift / Kotlin parsers
- `okf --version` flag
- mkdocs documentation site

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

[Unreleased]: https://github.com/UmairBaig8/okf-generator/compare/v0.1.11...HEAD
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
