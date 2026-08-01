# Plugin Development Guide

OKF discovers parser and manifest plugins automatically via Python entry points. No core code changes needed to add a language or manifest format.

## Table of Contents

- [How It Works](#how-it-works)
- [Plugin Types](#plugin-types)
- [ManifestPlugin Interface](#manifestplugin-interface)
- [ParserPlugin Interface](#parserplugin-interface)
- [Step-by-Step: Manifest Plugin](#step-by-step-manifest-plugin)
- [Step-by-Step: Parser Plugin](#step-by-step-parser-plugin)
- [Testing Your Plugin](#testing-your-plugin)
- [Publishing to PyPI](#publishing-to-pypi)
- [CLI Reference](#cli-reference)
- [Sample Plugin](#sample-plugin)
- [Troubleshooting](#troubleshooting)

---

## How It Works

A plugin is any Python package that registers an entry point in one of two groups:

| Entry point group | Purpose |
|---|---|
| ``okf.parsers`` | Adds a new source-code language parser |
| ``okf.manifests`` | Adds a new dependency-manifest format |

Registration happens in ``pyproject.toml``:

```toml
[project.entry-points."okf.manifests"]
myformat = "mypackage:MyHandler"
```

OKF discovers plugins at startup via ``importlib.metadata.entry_points()`` — the same mechanism used by Flake8, Pygments, Black, and pytest. No manual registration, no configuration files, no environment variables.

When a plugin fails to load (e.g., missing dependency, import error), OKF logs a warning and continues. The other plugins and built-in handlers are unaffected.

---

## Plugin Types

### ManifestPlugin

A manifest plugin teaches OKF to recognise a new dependency file format (e.g. ``.env``, ``Makefile``, ``Brewfile``). OKF calls the plugin's ``parse()`` method during ``okf generate`` whenever it encounters a matching filename.

**Use case:** Your project uses a custom configuration or dependency file that OKF doesn't know about. Write a 30-line plugin and ``pip install`` it — next scan picks it up.

### ParserPlugin

A parser plugin teaches OKF to parse a new programming language (e.g. COBOL, R, Elixir). OKF calls the plugin's ``parse_file()`` method for every source file with a matching extension.

**Use case:** You work with a niche language not yet supported by OKF. Write a parser plugin with tree-sitter or a custom AST walker, register it, and OKF indexes it alongside built-in languages.

---

## ManifestPlugin Interface

Your plugin class must provide:

```python
class ManifestHandler:
    MANIFEST_FILES: list[str] = []

    def parse(self, path: Path, repo_root: Path) -> list[dict]: ...
```

### ``MANIFEST_FILES``

List of filenames this handler recognises. Each name is checked against the file's basename during scanning.

```python
MANIFEST_FILES = [".env", ".env.example", ".env.local"]
```

Handlers for filenames starting with ``.`` will be checked **before** OKF's hidden-file filter, so ``.env`` files are not silently skipped.

### ``parse(path, repo_root) -> list[dict]``

Called for every file whose basename matches ``MANIFEST_FILES``.

| Argument | Type | Description |
|---|---|---|
| ``path`` | ``Path`` | Absolute path to the manifest file |
| ``repo_root`` | ``Path`` | Absolute path to the repository root |

**Return** a list of dependency dicts. Each dict must have:

| Key | Type | Description |
|---|---|---|
| ``name`` | ``str`` | Dependency name (e.g. ``"requests"``, ``"DB_URL"``) |
| ``ecosystem`` | ``str`` | Ecosystem label (e.g. ``"pip"``, ``"npm"``, ``"dotenv"``) |
| ``version`` | ``str`` | Version constraint string (e.g. ``">=2.28"``, ``"=postgres://..."``) |
| ``dev`` | ``bool`` | Whether this is a dev-only dependency |

Optional keys that OKF will preserve if present:

| Key | Type | Description |
|---|---|---|
| ``type`` | ``str`` | Concept type (default ``"Dependency"``) |
| ``description`` | ``str`` | Human-readable summary |
| ``body_extra`` | ``dict`` | Arbitrary extra data (e.g. ``{"source_manifest": "..."}``) |
| ``tags`` | ``list[str]`` | Additional tags merged into the concept |

---

## ParserPlugin Interface

Your plugin class must provide:

```python
class Parser:
    LANGUAGE: str = ""
    EXTENSIONS: set[str] = set()

    def parse_file(self, path: Path, repo_root: Path) -> list[Concept]: ...
```

### ``LANGUAGE``

A short identifier string like ``"cobol"``, ``"elixir"``, ``"r"``. Used for tagging concepts.

### ``EXTENSIONS``

Set of file extensions this parser handles.

```python
EXTENSIONS = {".cbl", ".cob", ".cpy"}
```

### ``parse_file(path, repo_root) -> list[Concept]``

Called for every source file whose extension matches ``EXTENSIONS``.

| Argument | Type | Description |
|---|---|---|
| ``path`` | ``Path`` | Absolute path to the source file |
| ``repo_root`` | ``Path`` | Absolute path to the repository root |

**Return** a list of ``Concept`` objects. The first concept should be a ``Module`` (representing the file), followed by any child symbols (functions, classes, etc.).

The ``Concept`` dataclass is imported from ``okf.parsers.base``:

```python
from okf.parsers.base import Concept
```

For tree-sitter based parsers, subclass ``TreeSitterParser`` from ``okf.parsers.base`` to get lazy language loading, parsing helpers, and the standard module-wrapper pattern.

```python
from okf.parsers.base import TreeSitterParser, Concept

class CobolParser(TreeSitterParser):
    LANGUAGE = "cobol"
    EXTENSIONS = {".cbl", ".cob"}
    _TS_MODULE = "tree_sitter_cobol"  # pip package providing the grammar

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        # Walk tree-sitter CST, yield Concept objects
        ...
```

If you don't use tree-sitter (like OKF's built-in ``PythonParser`` which uses stdlib ``ast``), implement ``parse_file()`` directly without subclassing.

### Optional methods

These are only used by OKF's linker for call-graph and dependency resolution:

| Method | Signature | Purpose |
|---|---|---|
| ``collect_imports`` | ``(self, root_node, source_bytes) -> list[str]`` | Extract import statements (for linking to Dependency concepts) |
| ``collect_calls`` | ``(self, node, source_bytes) -> list[str]`` | Extract function call names (for call-graph edges) |

If your parser doesn't provide them, OKF simply won't resolve imports or calls for that language — concepts are still emitted and searchable.

---

## Step-by-Step: Manifest Plugin

Let's create a plugin that parses ``.env`` files. This is the complete process from zero to installed.

### 1. Create the package structure

```text
okf-my-plugin/
├── pyproject.toml
├── README.md
└── okf_my_plugin/
    └── __init__.py
```

### 2. Write ``pyproject.toml``

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "okf-my-plugin"
version = "0.1.0"
description = "OKF plugin — my custom manifest format"
requires-python = ">=3.10"

[project.entry-points."okf.manifests"]
myformat = "okf_my_plugin:Handler"

[tool.hatch.build.targets.wheel]
packages = ["okf_my_plugin"]
```

The entry point name (``myformat``) is an arbitrary identifier. It doesn't affect behaviour — only the class attributes matter.

### 3. Write the handler

```python
# okf_my_plugin/__init__.py
from pathlib import Path


class Handler:
    MANIFEST_FILES = ["myproject.conf", ".myprojectrc"]

    def parse(self, path: Path, repo_root: Path) -> list[dict]:
        deps = []
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return deps
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                deps.append({
                    "name": key.strip(),
                    "ecosystem": "myecosystem",
                    "version": f"={val.strip()}",
                    "dev": False,
                })
        return deps
```

### 4. Install and test

```bash
cd okf-my-plugin
pip install .
okf plugin list
# → Manifests:
#     myproject         [myproject.conf, .myprojectrc]

mkdir -p /tmp/test_myplugin
echo 'DATABASE_URL=postgres://localhost/mydb
API_KEY=sk-test' > /tmp/test_myplugin/.myprojectrc
echo 'x=1' > /tmp/test_myplugin/main.py

okf generate /tmp/test_myplugin /tmp/test_bundle
okf lookup --bundle /tmp/test_bundle --type Dependency
# → DATABASE_URL, API_KEY
```

---

## Step-by-Step: Parser Plugin

For a parser plugin, the same structure applies but with the ``okf.parsers`` entry point group.

### Minimal non-tree-sitter parser

This parser extracts top-level function definitions without any grammar library:

```python
# okf_my_lang_plugin/__init__.py
import re
from pathlib import Path
from okf.parsers.base import Concept


class Parser:
    LANGUAGE = "mylang"
    EXTENSIONS = {".my"}

    def parse_file(self, path: Path, repo_root: Path) -> list[Concept]:
        rel = str(path.relative_to(repo_root))
        src = path.read_text(encoding="utf-8")
        module = Concept(
            type="Module",
            title=path.stem,
            resource=rel,
            tags=[self.LANGUAGE],
            concept_id=rel.replace(f".{self.LANGUAGE}", ""),
        )
        symbols = []
        for match in re.finditer(r"^func\s+(\w+)", src, re.MULTILINE):
            name = match.group(1)
            symbols.append(Concept(
                type="Function",
                title=name,
                resource=rel,
                tags=[self.LANGUAGE],
                concept_id=f"{module.concept_id}/{name}",
                source_lines=(match.start(), match.end()),
            ))
        return [module] + symbols
```

### With tree-sitter

If a ``tree-sitter-<lang>`` grammar package exists on PyPI, subclass ``TreeSitterParser``:

```python
from okf.parsers.base import TreeSitterParser, Concept

class ElixirParser(TreeSitterParser):
    LANGUAGE = "elixir"
    EXTENSIONS = {".ex", ".exs"}
    _TS_MODULE = "tree_sitter_elixir"

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        symbols = []
        # Walk tree-sitter CST and emit Concept objects
        #    self._make_concept("Function", name, doc, sig, resource, ts, parent_id, ...)
        return symbols
```

``_TS_MODULE`` is the Python import path for the tree-sitter grammar package. OKF lazily imports it and creates a ``Language`` object via ``Language(mod.language())``.

---

## Testing Your Plugin

### With ``okf plugin``

```bash
# Verify discovery
okf plugin list

# Check for load errors
okf plugin list | grep -A5 "Errors"
```

### With a real scan

```bash
# Manifest plugin
mkdir -p /tmp/test_plugin
echo 'MY_VAR=hello' > /tmp/test_plugin/.mypluginfile
echo 'print(1)' > /tmp/test_plugin/main.py
okf generate /tmp/test_plugin /tmp/test_bundle
okf lookup --bundle /tmp/test_bundle --type Dependency

# Parser plugin
echo 'func hello()' > /tmp/test_plugin/test.my
okf generate /tmp/test_plugin /tmp/test_bundle2
okf lookup --bundle /tmp/test_bundle2 --type Function
```

### Entry point verification

```bash
python3 -c "
from importlib.metadata import entry_points
eps = entry_points(group='okf.manifests')
for ep in eps:
    print(ep.name, '→', ep.value)
"
```

---

## Publishing to PyPI

Once your plugin works locally, publish it so others can ``pip install`` it:

1. **Choose a name** — prefix with ``okf-`` for discoverability (e.g. ``okf-parser-cobol``)
2. **Build** — ``python -m build``
3. **Upload** — ``twine upload dist/*``
4. **Verify** — ``pip install okf-parser-cobol && okf plugin list``

No changes needed in OKF itself — entry points are auto-discovered at runtime.

---

## CLI Reference

### ``okf plugin list``

Show all discovered parser and manifest plugins (built-in + external).

```
okf plugin list

  Parsers (18 languages, 29 extensions):
    python            [.py]
    go                [.go]
    ...

  Manifests (23 files):
    pip               [requirements.txt]
    Docker            [Containerfile, Dockerfile]
    dotenv            [.env, .env.example, .env.local]
    ...
```

### ``okf plugin install <package>``

``pip install`` a plugin package and verify it loads correctly.

```bash
okf plugin install okf-parser-cobol
# → Installed okf-parser-cobol
# → Plugin registered successfully.
```

### ``okf plugin uninstall <package>``

``pip uninstall`` a plugin package.

```bash
okf plugin uninstall okf-parser-cobol
```

---

## Sample Plugin

OKF ships a complete reference plugin at ``sample-plugins/okf-dotenv-plugin/`` in the repository. It demonstrates every aspect of the plugin system:

- Package structure with ``pyproject.toml``
- ``ManifestHandler`` implementation
- ``.env`` file parsing
- Full docstrings and type annotations

Install it to test the plugin system end-to-end:

```bash
cd sample-plugins/okf-dotenv-plugin
pip install .
okf plugin list
# → dotenv  [.env, .env.example, .env.local, ...]
```

---

## Troubleshooting

### Plugin not showing up in ``okf plugin list``

```bash
# Check if the package is installed
pip list | grep okf-

# Check if the entry point is registered
python3 -c "
from importlib.metadata import entry_points
eps = entry_points(group='okf.manifests')
for ep in eps:
    print(ep.name, '→', ep.value)
"

# Check for load errors
okf plugin list | grep -i error
```

Common causes:

- **``pyproject.toml`` missing or misconfigured** — Double-check the ``[project.entry-points."okf.manifests"]`` section.
- **Build system didn't include entry points** — If using ``hatchling``, ensure ``[tool.hatch.build.targets.wheel]`` includes your package.
- **Import error in plugin** — OKF logs a warning and skips the plugin, but ``okf plugin list`` shows it under Errors.

### Plugin found but scan doesn't use it

For **manifest plugins**: check that the filename matches exactly. ``MANIFEST_FILES = [".env"]`` won't match ``.env.local`` unless you list it separately.

For **parser plugins**: check that the file extension is in ``EXTENSIONS``. ``EXTENSIONS = {".my"}"`` won't match ``.MY`` (extensions are case-sensitive). Extensions must include the leading dot.

### PermissionError or missing file

Your ``parse()`` / ``parse_file()`` method receives the file path — handle exceptions gracefully and return an empty list if the file can't be read.
