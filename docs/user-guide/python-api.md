# Python API

```python
from okf.generator import scan_codebase, write_bundle, write_summary
from okf.lookup import load_bundle, search
```

## Generate a bundle

```python
concepts = scan_codebase("./my_project")
write_bundle(concepts, "./okf_bundle", "my_project", ["initial generation"])
write_summary("my_project", concepts, "./okf_bundle", {})
```

Parameters:

| Function | Key params |
|----------|-----------|
| `scan_codebase(root, exclude=None)` | Scans a directory and returns `list[Concept]` |
| `write_bundle(concepts, output_dir, bundle_name, log_entries, source_dirs=None)` | Writes concept `.md` files + directory index files |
| `write_summary(bundle_name, concepts, output_dir, git)` | Writes `SUMMARY.md` |

## Search concepts

```python
bundle = load_bundle("./okf_bundle")
results = search(bundle, tokens=["WorldBankConnector"])
print(results[0]["description"])
```

Parameters:

| Function | Key params |
|----------|-----------|
| `load_bundle(bundle_dir, use_cache=True)` | Loads all concepts from a bundle dir |
| `search(concepts, tokens, file_filter, type_filter, tag_filters, limit, min_score)` | Filters and scores concepts |

## Concept dataclass

```python
@dataclass
class Concept:
    type: str          # Module | Function | Class | Method | Dependency
    title: str
    description: str
    resource: str       # relative source path
    tags: list[str]
    signature: str
    docstring: str
    params: list[dict]  # {name, annotation, default}
    returns: str
    methods: list[str]
    source_lines: tuple
    calls: list[str]    # resolved concept IDs this concept calls
    called_by: list[str] # resolved concept IDs that call this concept
    imports: list[str]  # raw import strings (for dependency linking)
    body_extra: dict    # type-specific fields (Dependency → ecosystem, version, etc.)
    concept_id: str
```
