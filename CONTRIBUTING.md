# Contributing to okf-generator

Thank you for taking the time to contribute! This document covers how to get set up,
what kinds of contributions are most useful, and how to submit them.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Adding a Language Parser](#adding-a-language-parser)
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
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_generator.py -v

# Run with coverage
pytest tests/ --cov=okf --cov-report=term-missing
```

All PRs must pass the full test suite. If you add a new feature, please add tests.

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

## Submitting a Pull Request

1. Ensure `pytest tests/ -v` passes with no failures
2. Keep commits focused — one logical change per commit
3. Write a clear PR description explaining what and why
4. Reference any related issues with `Closes #<issue>`

**Commit message format:**
```
feat: add C# tree-sitter parser
fix: handle __init__.py in nested packages
docs: update OpenCode integration guide
test: add fuzzy search edge cases
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
