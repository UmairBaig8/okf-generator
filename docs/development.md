# Development Guide

## Adding a New Language Parser

### Overview

Each parser lives in its own file under `okf/parsers/`. The registry in `__init__.py` maps file extensions to parser classes.

Adding a new language requires **2 files** and **1 line** in the registry.

### Step-by-step

#### 1. Create the parser file

`okf/parsers/my_lang.py`:

```python
"""MyLang (tree-sitter)."""

from okf.parsers.base import _prev_comment, _find_all, _node_text, TreeSitterParser


class MyLangParser(TreeSitterParser):
    LANGUAGE   = "my_lang"
    EXTENSIONS = {".my", ".myl"}
    _TS_MODULE = "tree_sitter_my_lang"
    _lang_obj  = None

    def _module_doc(self, root, src_bytes: bytes) -> str:
        for child in root.children:
            if child.type == "comment":
                return _prev_comment(child, src_bytes)
        return ""

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []
        for node in _find_all(root, "function_definition", "class_definition"):
            ...
        return concepts
```

**Required class attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| `LANGUAGE` | `str` | Language identifier (used in tags) |
| `EXTENSIONS` | `set[str]` | File extensions this parser handles |
| `_TS_MODULE` | `str` | tree-sitter pip package name |
| `_lang_obj` | `None` | Class-level cache for the Language object |

**Methods you can override:**

| Method | Default | When to override |
|--------|---------|------------------|
| `parse_file()` | Calls `_parse_symbols()` + wraps in Module | Override only if the TS grammar needs special setup (see `JSTSParser`) |
| `_module_doc()` | Returns `""` | Language has file-level doc comments |
| `_collect_imports()` | Returns `[]` | Language has import statements |
| `_collect_calls()` | Returns `[]` | Language has function calls |
| `_parse_symbols()` | Returns `[]` | **Always override** — extract functions, classes, etc. |

#### 2. Register the parser

Add **one line** to `okf/parsers/__init__.py`:

```python
from okf.parsers.my_lang import MyLangParser

def get_parser(ext: str):
    ...
    if ext in MyLangParser.EXTENSIONS:
        return MyLangParser()
    ...
```

#### 3. Add test fixtures

```
tests/fixtures/realworld/my_lang/
├── easy/
│   └── hello.my
└── complex/
    └── app.my
```

#### 4. Install the tree-sitter dependency

```bash
pip install tree-sitter-my-lang
```

Add to `pyproject.toml` under `[project.dependencies]`.

If the package lacks pre-built wheels, add a Rust toolchain step to CI workflows.

### Parser Interface

```python
class TreeSitterParser:
    LANGUAGE: str = "unknown"
    EXTENSIONS: set[str] = set()

    def parse_file(self, path: Path, repo_root: Path) -> list[Concept]:
        """Parse one source file into OKF concepts.
        
        Returns:
            [Module concept, ...symbol concepts]
        """

    def _module_doc(self, root, src_bytes: bytes) -> str:
        """Extract file-level doc comment."""

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        """Collect raw import names for the module concept."""

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        """Collect raw callee names inside a function body."""

    def _parse_symbols(
        self, root, src_bytes, resource: str, ts: str, parent_id: str
    ) -> list[Concept]:
        """Extract functions, classes, methods, and other symbols."""

    def _make_concept(
        self, ctype: str, name: str, doc: str, sig: str,
        resource: str, ts: str, parent_id: str,
        lineno: int = 0, node=None, src_bytes: bytes = b"",
        ...
    ) -> Concept:
        """Build a Concept with the common fields filled in."""
```

### Shared Utilities (from `okf.parsers.base`)

| Function | Purpose |
|----------|---------|
| `_ts(path)` | ISO-8601 timestamp from file mtime |
| `_prev_comment(node, src_bytes)` | Extract doc comment preceding a node |
| `_find_all(node, *kinds)` | Recursively find child nodes by type |
| `_node_text(node)` | Decode node bytes to string |
| `_parse_doc_tags(docstring, lang)` | Parse `@param`/`@return` tags |
| `_safe_id(name)` | Sanitize symbol name for file ID |
| `_first_line(text)` | First non-empty line of text |
| `Concept` | OKF concept dataclass |

### Concept Fields Set by Parsers

| Field | Description |
|-------|-------------|
| `type` | `Module` / `Function` / `Class` / `Method` |
| `title` | Display name |
| `description` | First line of doc comment |
| `docstring` | Full doc comment text |
| `signature` | Function/class signature string |
| `resource` | Relative source path |
| `tags` | `[language, concept_type]` |
| `timestamp` | ISO-8601 file mtime |
| `source_lines` | `(start_line, end_line)` 1-indexed |
| `concept_id` | Unique ID for cross-referencing |
| `params` | `[{name, annotation, default}]` |
| `returns` | Return type string |
| `methods` | Method names (for classes) |
| `type_params` | Generic type parameters `["T", "U"]` |
| `inheritance` | Base classes/interfaces |
| `decorators` | Decorators/attributes |
| `visibility` | Access modifiers `["public"]` |
| `fields` | `[{name, type, visibility}]` |
| `imports` | Raw import names (Module only) |
| `calls_raw` | Raw callee names |
| `related` | Related concept IDs |

### Non-tree-sitter Parsers

For languages without a tree-sitter grammar, subclass `object` directly and implement `parse_file()` from scratch. See `okf/parsers/python.py`.

### Testing

```bash
# After adding fixtures:
pytest tests/ -k "my_lang" -q

# Full suite:
pytest tests/ -q
```
