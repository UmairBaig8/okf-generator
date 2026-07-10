# OpenCode Integration Guide

How to wire your OKF bundle into OpenCode so the agent automatically
looks up exact concepts before touching your code.

## 1. AGENTS.md (auto-loaded by OpenCode on every session)

Add to your repo root `AGENTS.md`:

```markdown
## OKF Knowledge Bundle

This codebase has an OKF v0.2 knowledge bundle at `./okf_bundle/`.

Before working on ANY class, function, or module:
1. Look it up: `okf lookup <ConceptName>`
2. If unsure of name: `okf lookup --file path/to/source.py`
3. For full map: `cat ./okf_bundle/SUMMARY.md`

This gives you the exact signature, docstring, params, returns, and
related concepts — without reading the full source file.
```

## 2. Custom Commands (.opencode/commands/)

```bash
mkdir -p .opencode/commands
```

### lookup.md — find any concept by name
```markdown
Look up an exact concept in the OKF knowledge bundle.
RUN okf lookup --bundle ./okf_bundle $NAME
```

Usage in OpenCode: `/lookup NAME=WorldBankConnector`

### lookup-file.md — all concepts from one file
```markdown
Show all OKF concepts extracted from a source file.
RUN okf lookup --bundle ./okf_bundle --file $FILE
```

Usage: `/lookup-file FILE=StockAI/RnD/python/connectors/economic_data.py`

### lookup-class.md — find classes by keyword
```markdown
Find all Class concepts matching a keyword.
RUN okf lookup --bundle ./okf_bundle --type Class --compact $NAME
```

Usage: `/lookup-class NAME=connector`

### prime-domain.md — load a full domain index
```markdown
Load the OKF index for a specific domain to understand its structure.
RUN cat ./okf_bundle/$DOMAIN/index.md
```

Usage: `/prime-domain DOMAIN=StockAI/RnD/python/connectors`

## 3. Typical workflow inside OpenCode

```
# Before refactoring a class
/lookup NAME=WorldBankConnector

# Before adding a feature to a module
/lookup-file FILE=StockAI/RnD/python/connectors/economic_data.py

# When you don't know the exact name
/lookup-class NAME=bank

# When starting work on a new domain
/prime-domain DOMAIN=StockAI/RnD
```

## 4. JSON mode for programmatic agent use

If you're building a custom agent that reads OKF concepts:

```bash
okf lookup --json WorldBankConnector
```

Returns structured JSON:
```json
[
  {
    "type": "Class",
    "title": "WorldBankConnector",
    "description": "Fetches World Bank development indicators via wbdata API.",
    "resource": "StockAI/RnD/python/connectors/economic_data.py",
    "concept_id": "StockAI/RnD/python/connectors/economic_data/WorldBankConnector",
    "tags": ["lang:python", "type:Class", "module:StockAI", "domain:RnD"],
    "signature": "class WorldBankConnector",
    "docstring": "World Bank Development Indicators...",
    "methods": ["get_indicator", "search"],
    "returns": ""
  }
]
```
