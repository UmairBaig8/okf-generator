# Quick Start

In 3 minutes you'll generate a knowledge bundle from any codebase and look up any function, class, or dependency — no LLM, no API key, no setup.

---

## 1. Generate a bundle

Run `okf generate` from your project root — it auto-detects the source directory:

```bash
cd my_project
okf generate
```

Or specify paths explicitly:

```bash
okf generate ./my_project ./okf_bundle
```

Auto-detection walks up the directory tree looking for project markers (`pyproject.toml`, `Cargo.toml`, `package.json`, `go.mod`, `.git/`, etc.) across all languages. If nothing is found, it uses the current directory.

This scans all recognized files using tree-sitter AST parsers (17 languages) and writes a structured knowledge bundle to `./okf_bundle/`.

**What you get:**
- Every function, class, method, and module as a concept card
- Every dependency extracted from manifest files
- Cross-reference edges (calls, called-by, imports, depends-on)
- Pure markdown — diff cleanly, version alongside code

**Example output:**
```
  Class                  12
  Function               48
  Module                 14
  Dependency              8
  Interface               3
  Enum                    2
  ────────────────────────
  TOTAL                  87
```

---

## 2. Look up any concept

```bash
okf lookup --bundle ./okf_bundle MyFunction
```

Returns the full concept card — signature, parameters, docstring, return type, callers, callees, and source location — in milliseconds.

**Filter by type:**
```bash
okf lookup --bundle ./okf_bundle --type Function
okf lookup --bundle ./okf_bundle --type Class
okf lookup --bundle ./okf_bundle --type Dependency
```

**Filter by language or ecosystem:**
```bash
okf lookup --bundle ./okf_bundle --tag lang:python
okf lookup --bundle ./okf_bundle --tag ecosystem:pip
```

**Fuzzy search — camelCase, snake_case, acronyms:**
```bash
okf lookup --bundle ./okf_bundle repo        # Finds UserRepository, OrderRepo
okf lookup --bundle ./okf_bundle calc        # Finds Calculator
okf lookup --bundle ./okf_bundle ur          # Acronym match: UserRepository
```

**JSON output for programmatic use:**
```bash
okf lookup --bundle ./okf_bundle --json MyClass
```

---

## 3. Browse visually

### Static visualization
```bash
okf visualize ./okf_bundle
# Opens an interactive HTML graph in your browser
```

### Live dashboard (FastAPI)
```bash
# Install the dashboard extra first:
pip install "okf-generator[dashboard]"

okf dashboard ./okf_bundle --open
# Launches at http://127.0.0.1:8700
```

The dashboard provides:
- **Search** — full-text search with type and language filters
- **Detail view** — signature, params, docstring, source, tags, related links
- **Interactive graph** — visual dependency graph per concept
- **REST API** — all data available at `/api/` endpoints

---

## 4. Diff and track changes

```bash
# Generate from two versions
okf generate ./project_v1 /tmp/v1
okf generate ./project_v2 /tmp/v2

# See what changed
okf diff /tmp/v1 /tmp/v2 --compact

# See dependency impact
okf diff /tmp/v1 /tmp/v2 --impact
```

The `--impact` flag traces changed dependencies to affected modules and their functions/classes — critical for CI/CD pipelines.

---

## 5. Use from Python

```python
from okf.generator import scan_codebase, write_bundle
from okf.lookup import load_bundle, search
from pathlib import Path

# Scan a codebase
concepts = scan_codebase(Path("./my_project"))
print(f"Extracted {len(concepts)} concepts")

# Write a bundle
write_bundle(concepts, Path("./okf_bundle"), "my_project", ["initial scan"])

# Load and search
bundle = load_bundle(Path("./okf_bundle"))
results = search(bundle, tokens=["PaymentService"])
print(results[0].title)        # "PaymentService"
print(results[0].type)         # "Class"
print(results[0].signature)    # "class PaymentService"
```

---

## 6. Set up for AI agents

One command installs okf-generator into your preferred agent:

```bash
okf install claude        # Claude Code skill
okf install cursor        # Cursor rules
okf install copilot       # GitHub Copilot
okf install opencode      # OpenCode /lookup command
okf install all           # All of the above
```

After installation, when you ask your agent about any concept in your codebase, it will automatically run `okf lookup` instead of reading entire files — saving 80-95% tokens.

---

## 7. What's next?

| If you want to... | Go here |
|-------------------|---------|
| Explore all commands | [CLI Reference](../user-guide/cli-reference.md) |
| Enrich with LLM descriptions | `okf generate --enrich` |
| Convert bundle to training data | `okf pairs ./okf_bundle ./train.jsonl` |
| Set up CI/CD pipeline | [CI/CD Guide](../user-guide/ci-cd.md) |
| Add a new language parser | [Development Guide](../development.md) |
| Use with MCP-compatible tools | `okf mcp ./okf_bundle` |
