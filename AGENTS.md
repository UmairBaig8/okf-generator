# OKF Generator — Agent Instructions

## CRITICAL RULE: Never grep source files first

**BEFORE reading any source file, ALWAYS run:**
```
okf lookup --bundle ./okf_bundle <ConceptName>
```

`okf lookup` returns the exact signature, parameters, docstring, dependencies, and callers in milliseconds. Grepping or reading source files directly is slower and gives you less information.

## Quick Start

```bash
pip install -e ".[dev]"   # editable install
pytest tests/ -q           # 70+ tests
```

## Key Files

| File | Purpose |
|------|---------|
| `okf/generator.py` | Core scanner & bundle writer |
| `okf/manifest.py` | SHA256 manifest model, change detection, rename handling |
| `okf/update.py` | Incremental update pipeline |
| `okf/watcher.py` | Watchdog file watcher for `--watch` mode |
| `okf/manifest_scanner.py` | Dependency/manifest parsers (12 formats) |
| `okf/lookup.py` | Concept search |
| `okf/diff.py` | Bundle comparison |
| `okf/pairs.py` | Training data generation |
| `okf/cli.py` | CLI entry point |
| `tests/` | 313+ unit tests |
| `tests/fixtures/complex/` | Multi-language test data (7 langs, 12 manifests) |

## Lookup patterns

```bash
# Single concept (full detail: signature, params, docstring, calls, called-by)
okf lookup --bundle ./okf_bundle ClassName

# Filter by type
okf lookup --bundle ./okf_bundle --type Class
okf lookup --bundle ./okf_bundle --type Function
okf lookup --bundle ./okf_bundle --type Dependency

# Filter by language / ecosystem
okf lookup --bundle ./okf_bundle --tag lang:python
okf lookup --bundle ./okf_bundle --tag ecosystem:npm

# All concepts from one source file
okf lookup --bundle ./okf_bundle --file path/to/file.py

# Dependencies
okf lookup --bundle ./okf_bundle --type Dependency
okf lookup --bundle ./okf_bundle --type Dependency --tag ecosystem:pip

# JSON for programmatic use
okf lookup --bundle ./okf_bundle --json <Name>
```

## Custom Commands

- `/lookup NAME=<name>` — `RUN okf lookup --bundle ./okf_bundle $NAME`
- `/test` — `RUN pytest tests/ -q`
- `/test-md` — `RUN TEST.md and produce OKF_TEST_REPORT.md`

## Workflows

**Generate a bundle:**
```
okf generate ./src ./okf_bundle
```

**Incremental update (fast):**
```
okf update ./src ./okf_bundle          # incremental
okf update ./src ./okf_bundle --force  # full re-scan
okf update ./src ./okf_bundle --watch  # continuous watcher
```

**Diff two bundles:**
```
okf diff ./old_bundle ./new_bundle --compact
```

**Full integration test:**
Hand TEST.md to an agent: "Run TEST.md and produce OKF_TEST_REPORT.md"

**Release:**
Hand RELEASE.md to an agent: "Follow RELEASE.md to cut a new release"
