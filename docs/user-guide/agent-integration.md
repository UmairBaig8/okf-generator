# AI Agent Integration Guide

`okf-generator` works with **any AI coding agent** — the output is plain markdown files that every agent can read. This guide covers setup for all major agents.

## Table of Contents

- [Token Efficiency](#token-efficiency)
- [Recommended System Prompt](#recommended-system-prompt)
- [OpenCode / Claude Code](#opencode--claude-code)
- [Cursor / Windsurf / Cline](#cursor--windsurf--cline)
- [GitHub Copilot](#github-copilot)
- [Any Agent with RUN Capability](#any-agent-with-run-capability)
- [MCP Integration](#mcp-integration)
- [Agent Installation Command](#agent-installation-command)

## Token Efficiency

| Optimization | How okf-generator helps | Agent impact |
|---|---|---|
| Deterministic types | Every concept has `type: Function`, `type: Class`, `type: Dependency` | Agent filters by type precisely |
| Incremental access | `okf lookup <Name>` returns one concept, not whole files | Saves 80-95% token cost vs reading source |
| Structured metadata | Signature, params, returns in YAML frontmatter | Agent extracts info without parsing code |
| Cross-reference edges | Calls / Called By / Used By in each concept | Enables multi-hop reasoning without grep |

## Recommended System Prompt

When setting up agent instructions, include:

```markdown
This project has an OKF knowledge bundle at ./okf_bundle/.
- Use `okf lookup <Name>` to get full concept context.
- Use `okf lookup --type <Type>` to filter by type (Class, Function, Dependency).
- Use `okf lookup --tag ecosystem:<name>` for ecosystem-specific queries.
- Use `okf lookup --file <path>` for all concepts from one source file.
- Use `okf lookup --deps` to list all dependencies.
- Read `SUMMARY.md` for the full knowledge map.
```

## OpenCode / Claude Code

### 1. AGENTS.md (auto-loaded)

Add to your repo root `AGENTS.md`:

```markdown
## OKF Knowledge Bundle

This codebase has an OKF v0.1 knowledge bundle at `./okf_bundle/`.

Before working on ANY class, function, or module:
1. Look it up: `okf lookup <ConceptName>`
2. If unsure of name: `okf lookup --file path/to/source.py`
3. For full map: `cat ./okf_bundle/SUMMARY.md`

This gives you the exact signature, docstring, params, returns, and
related concepts — without reading the full source file.
```

### 2. Custom Commands

```bash
mkdir -p .opencode/commands
```

**`lookup.md`** — find any concept by name:
```markdown
Look up an exact concept in the OKF knowledge bundle.
RUN okf lookup --bundle ./okf_bundle $NAME
```

Usage: `/lookup NAME=WorldBankConnector`

**`lookup-file.md`** — all concepts from one source file:
```markdown
Show all OKF concepts extracted from a source file.
RUN okf lookup --bundle ./okf_bundle --file $FILE
```

Usage: `/lookup-file FILE=StockAI/RnD/python/connectors/economic_data.py`

**`lookup-class.md`** — find classes by keyword:
```markdown
Find all Class concepts matching a keyword.
RUN okf lookup --bundle ./okf_bundle --type Class --compact $NAME
```

Usage: `/lookup-class NAME=connector`

**`prime-domain.md`** — load a full domain index:
```markdown
Load the OKF index for a specific domain to understand its structure.
RUN cat ./okf_bundle/$DOMAIN/index.md
```

Usage: `/prime-domain DOMAIN=StockAI/RnD/python/connectors`

### 3. Typical Workflow

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

## Cursor / Windsurf / Cline

Add to `.cursorrules` (or `.windsurfrules` / `.clinerules`):

```
Before editing a function or class, run:
  okf lookup --bundle ./okf_bundle <Name>
To see dependencies:
  okf lookup --bundle ./okf_bundle --type Dependency
```

## GitHub Copilot

Reference OKF bundle files in `/.github/copilot-instructions.md`:

```
Project knowledge is indexed in ./okf_bundle/
  - okf lookup <Name> returns full concept context
  - okf lookup --type Dependency returns dependency info
```

## Any Agent with RUN Capability

```bash
# Prime full context
cat ./okf_bundle/SUMMARY.md

# Look up a specific concept
okf lookup --bundle ./okf_bundle WorldBankConnector

# List dependencies
okf lookup --bundle ./okf_bundle --type Dependency

# JSON for programmatic agent use
okf lookup --bundle ./okf_bundle --json WorldBankConnector
```

### JSON Mode

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

## MCP Integration

Expose your OKF bundle via Model Context Protocol:

```bash
# Start MCP server
okf mcp ./okf_bundle
```

This works with any MCP client — Claude Desktop, Cursor, VS Code extensions, and custom MCP hosts.

## Agent Installation Command

The `okf install` command automates all of the above:

```bash
# Install for all detected agents
okf install all

# Or pick specific agents
okf install claude      # Claude Code skill
okf install opencode    # OpenCode /lookup command
okf install copilot     # GitHub Copilot instructions
okf install cursor      # Cursor rules
okf install windsurf    # Windsurf rules
okf install cline       # Cline rules
```

**What each install does:**

| Agent | Files created | Effect |
|---|---|---|
| Claude Code | `~/.config/opencode/skills/okf-generator/SKILL.md` | Auto-triggers on phrases like "index my codebase" |
| OpenCode | `.opencode/commands/lookup.md` | `/lookup NAME=<ConceptName>` |
| Copilot | `.github/copilot-instructions.md` | Auto-loaded in VS Code |
| Cursor | `.cursorrules` | Auto-loaded by Cursor |
| Windsurf | `.windsurfrules` | Auto-loaded by Windsurf |
| Cline | `.clinerules` | Auto-loaded by Cline |
