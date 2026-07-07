# Installation

## One-liner (macOS / Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/scripts/install.sh | bash
```

This installs the core package with all language parsers.

---

## pip (recommended)

```bash
pip install okf-generator
```

Core extraction is fully offline and deterministic — no LLM, no API key, no internet required.

### Optional extras

| Extras | What you get | Command |
|--------|-------------|---------|
| `[llm]` | LLM enrichment (OpenAI SDK) | `pip install "okf-generator[llm]"` |
| `[dashboard]` | Live bundle browser (FastAPI + uvicorn) | `pip install "okf-generator[dashboard]"` |
| `[dev]` | Development tools (pytest, ruff, mkdocs) | `pip install "okf-generator[dev]"` |

**All at once:**
```bash
pip install "okf-generator[llm,dashboard]"
```

---

## uv (fast alternative)

```bash
uv pip install okf-generator
```

Or with extras:
```bash
uv pip install "okf-generator[llm,dashboard]"
```

---

## Docker

```bash
docker pull ghcr.io/umairbaig8/okf-generator/okf-generator:latest

# Generate a bundle
docker run -v "$PWD:/repo" ghcr.io/umairbaig8/okf-generator/okf-generator \
  generate /repo/src /repo/okf_bundle
```

---

## Verify installation

```bash
okf --version
# Should print: okf-generator v0.1.39

okf --help
# Shows all available commands
```

---

## Quick smoke test

```bash
# Create a tiny test project
mkdir -p /tmp/test_project
cat > /tmp/test_project/greet.py << 'EOF'
"""A simple greeting module."""
def greet(name: str) -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}!"
EOF

# Generate a knowledge bundle
okf generate /tmp/test_project /tmp/test_bundle

# Look up the concept
okf lookup --bundle /tmp/test_bundle greet
```

You should see a concept card for `greet` with its signature, docstring, parameters, and return type — all extracted without a single LLM call.

---

## Platform-specific notes

### Windows

Install via pip works on Windows, but some tree-sitter parsers require a C compiler. Use Windows Terminal + Python 3.11+:

```bash
pip install okf-generator
```

If you encounter build errors for language parsers, install Microsoft C++ Build Tools from [visualstudio.microsoft.com](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

### Linux arm64 (Raspberry Pi, AWS Graviton)

All tree-sitter wheels are available for `aarch64`. Standard pip install works:

```bash
pip install okf-generator
```

---

## Next steps

- **[Quick Start](quick-start.md)** — generate your first bundle in 30 seconds
- **[AI Agent Integration](../agent-integration.md)** — set up for Claude, Cursor, Copilot
- **[CLI Reference](../cli-reference.md)** — full command reference
- **[Dashboard](../index.md)** — launch the live bundle browser
