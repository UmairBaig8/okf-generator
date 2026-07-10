# OKF Generator — Project Context

## What is this?

Generates OKF v0.2 knowledge bundles (extended dialect of Google's OKF v0.1) from codebases. Scans source code (7 languages via AST/tree-sitter + SQL via regex) and manifest files (12 formats) into structured markdown that AI agents can read.

## Quick Commands

```bash
pip install -e ".[dev]"      # editable install
pytest tests/ -q              # 70+ unit tests (all pass)
okf generate ./src ./bundle   # generate a bundle
okf lookup <Name>              # look up a concept
```

## Architecture

```
okf/
├── generator.py         # Scanner (7 langs + SQL) + bundle writer
├── manifest_scanner.py  # 12 manifest parsers (pip, npm, cargo, go, etc.)
├── lookup.py            # Concept search with cache
├── pairs.py             # Training data pipeline
└── cli.py               # CLI dispatch
```

- Concepts are `@dataclass Concept` objects with type/title/description/resource/tags/timestamp/signature/docstring/params/returns/methods/body_extra
- Dependency concepts use `body_extra` with ecosystem/version_constraint/dev_dependency/source_manifest
- Tags follow standard: `lang:`, `type:`, `module:`, `domain:`, `git:`, `ecosystem:`, `manifest:`, `version:`
- Lookup cache: `.okf_lookup_cache.json` auto-generated, mtime-invalidated

## Test Strategy

| Layer | Tool | Count |
|-------|------|-------|
| Unit | `pytest tests/` | 70+ |
| Integration | `TEST.md` | All CLI commands end-to-end |
| Release smoke | CI in `publish.yml` | Installs published wheel, generates, looks up |

## Key Files

- `AGENTS.md` — instructions for AI agents
- `TEST.md` — full integration test spec
- `RELEASE.md` — release checklist
- `CONTRIBUTING.md` — contributor guide
- `.github/workflows/publish.yml` — CI/CD pipeline

## Future Plans

See `FUTURE.md` — 5 prioritized features ordered by effort (CI/CD auto-publish → v0.2 schema → agent REPL → WASM viz → IDE plugins).

## Release Workflow

1. Run `TEST.md` to verify everything works
2. Follow `RELEASE.md` to bump version, update changelog, tag, and push
3. CI builds, publishes to PyPI, runs smoke test, creates GitHub Release
