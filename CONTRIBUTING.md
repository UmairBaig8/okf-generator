# Contributing to okf-generator

Thank you for taking the time to contribute! This document covers how to get set up,
what kinds of contributions are most useful, and how to submit them.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Integration Test Spec](#integration-test-spec)
- [Adding a Language Parser](#adding-a-language-parser)
- [Adding a Manifest Parser](#adding-a-manifest-parser)
- [Releasing](#releasing)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Code Style](#code-style)
- [Reporting Issues](#reporting-issues)
- [Good First Issues](#good-first-issues)

---

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/okf-generator
   cd okf-generator
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feat/my-feature
   ```

## Development Setup

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
okf --help
```

## Running Tests

```bash
# Run all unit tests (70+ tests)
pytest tests/ -v

# Run a specific test file
pytest tests/test_generator.py -v
pytest tests/test_lookup.py -v
pytest tests/test_manifest_scanner.py -v

# Run with coverage
pytest tests/ --cov=okf --cov-report=term-missing

# Run the full integration test spec (end-to-end CLI tests)
# See TEST.md for detailed instructions
```

All PRs must pass the full test suite. If you add a new feature, please add tests in the appropriate file:
- `tests/test_generator.py` — scanner and bundle generation tests
- `tests/test_lookup.py` — concept search tests
- `tests/test_manifest_scanner.py` — manifest parser tests

New fixture files go in `tests/fixtures/`. Use `tests/fixtures/complex/` to add languages/manifests to the comprehensive test suite.

## Integration Test Spec

[`TEST.md`](TEST.md) is a step-by-step integration spec that exercises every CLI command against real codebases. It covers:

- All 7 languages (Python, JS, TS, Go, Java, Rust, Ruby)
- All 12 manifest types (pip, npm, cargo, go, composer, maven, rubygems, gradle, swiftpm, clojars, hex)
- Lookup cache (miss, hit, bypass, corrupt, invalidation)
- Edge cases (empty dir, non-existent path, unsupported-only files)
- Static pair generation, summary regeneration
- Production checklist (gitignore, version consistency, stale files)

Run it before any major change or release. See `TEST.md` for full instructions.

**Using with AI agents:** Hand `TEST.md` to any LLM-powered coding agent with:
> "Run TEST.md in dev_wspace and produce OKF_TEST_REPORT.md"

The spec is formatted as a self-contained script — each phase has exact bash commands and verification criteria. The agent executes it and writes a structured report.

## Adding a Language Parser

Adding support for a new language is one of the most impactful contributions.

**Steps:**

1. Install the tree-sitter grammar:
   ```bash
   pip install tree-sitter-<language>
   ```

2. Probe the grammar to find node type names:
   ```python
   from tree_sitter import Language, Parser
   import tree_sitter_<language> as tslang

   lang = Language(tslang.language())
   parser = Parser(lang)
   src = b"... sample code ..."
   tree = parser.parse(src)

   def all_types(node, depth=0):
       if depth > 4: return set()
       types = {node.type}
       for c in node.children:
           types |= all_types(c, depth+1)
       return types

   print(sorted(all_types(tree.root_node)))
   ```

3. Subclass `TreeSitterParser` in `okf/generator.py`:
   ```python
   class MyLangParser(TreeSitterParser):
       LANGUAGE   = "mylang"
       EXTENSIONS = {".ml"}
       _TS_MODULE = "tree_sitter_mylang"
       _lang_obj  = None

       def _module_doc(self, root, src_bytes): ...
       def _parse_symbols(self, root, src_bytes, resource, ts, parent_id): ...
   ```

4. Register it in `_get_parser()`:
   ```python
   if ext in {".ml"}:
       return MyLangParser()
   ```

5. Add the dependency to `pyproject.toml` under `dependencies`

6. Add a fixture file and test cases in `tests/`

**Good languages to add next:** C/C++, C#, Swift, Kotlin, Scala, PHP

## Adding a Manifest Parser

Manifest parsers live in `okf/manifest_scanner.py` and follow a simple pattern:

1. Add the filename to `MANIFEST_HANDLERS` dict
2. Write a `parse_<format>(path: Path) -> list[dict]` function returning deps with `name`, `ecosystem`, `version`, `dev` keys
3. Add test cases in `tests/test_manifest_scanner.py`
4. Add a fixture file to `tests/fixtures/complex/` (so the e2e `test_complex_all_manifest_ecosystems` test covers it)

**Requirements:**
- Zero external deps (stdlib only: `re`, `json`, `xml.etree.ElementTree`, `tomllib`)
- Mark `dev=True` for dev/test-only dependencies
- Handle edge cases: comments, version ranges, platform entries (like `ext-*`, `php`)

**Good manifests to add next:** `Cargo.lock`, `yarn.lock`, `poetry.lock`, `packages.config`, `*.csproj`

## Releasing

See [`RELEASE.md`](RELEASE.md) for the full release process.

Before a release, run the complete test suite and integration spec:
```bash
pytest tests/ -q      # 70+ unit tests
# Then follow TEST.md  # full integration spec
```

**Using with AI agents:** Hand `RELEASE.md` to an LLM-powered coding agent with:
> "Follow RELEASE.md to cut a new release"

The agent will: bump version, update changelog, commit, tag, and push — everything the CI pipeline needs to publish automatically.

1. Ensure `pytest tests/ -v` passes with no failures
2. Keep commits focused — one logical change per commit
3. Write a clear PR description explaining what and why
4. Reference any related issues with `Closes #<issue>`

**Commit message format:**
```
feat: add C# tree-sitter parser
feat(manifest): add Cargo.lock parser
fix: handle __init__.py in nested packages
docs: broaden AI agent integration guide
test: add manifest parser edge cases
chore: bump v0.1.11
```

## Code Style

- Follow PEP 8
- Type hints on all public functions
- Docstrings on all public classes and functions
- Max line length: 100 characters

## Reporting Issues

Please use GitHub Issues. Include:

- Python version (`python --version`)
- Package version (`okf --version` once that's added)
- Minimal reproduction case
- Full error traceback if applicable

## Good First Issues

Look for issues tagged `good first issue` on GitHub. Some ideas:

- **New language**: Add parser for C#, Swift, Kotlin, PHP, Scala
- **Fuzzy search**: Improve scoring for camelCase / snake_case queries
- **Docs**: Add a `docs/` site with mkdocs or sphinx
- **CLI**: Add `okf --version` flag
- **Performance**: Parallelize the scan phase for large codebases

## Code of Conduct

Be kind and constructive. We follow the
[Contributor Covenant](https://www.contributor-covenant.org/).
