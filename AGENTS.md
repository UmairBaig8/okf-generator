# OKF Generator — Agent Instructions

## Quick Start

```bash
pip install -e ".[dev]"   # editable install
pytest tests/ -q           # 70+ tests
```

## Key Files

| File | Purpose |
|------|---------|
| `okf/generator.py` | Core scanner & bundle writer |
| `okf/manifest_scanner.py` | Dependency/manifest parsers (12 formats) |
| `okf/lookup.py` | Concept search |
| `okf/pairs.py` | Training data generation |
| `okf/cli.py` | CLI entry point |
| `tests/` | 70+ unit tests |
| `tests/fixtures/complex/` | Multi-language test data (7 langs, 12 manifests) |

## Before Editing a Class or Function

Look it up in the OKF bundle:
```
okf lookup --bundle ./okf_bundle <ConceptName>
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

**Full integration test:**
Hand TEST.md to an agent: "Run TEST.md and produce OKF_TEST_REPORT.md"

**Release:**
Hand RELEASE.md to an agent: "Follow RELEASE.md to cut a new release"
