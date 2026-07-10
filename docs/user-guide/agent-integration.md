# AI Agent Integration Guide

`okf-generator` works with **any AI coding agent** — the output is plain markdown files that every agent can read. This guide covers setup for all major agents.

## Table of Contents

- [Token Efficiency](#token-efficiency)
- [Recommended System Prompt](#recommended-system-prompt)
- [OpenCode / Claude Code](#opencode--claude-code)
- [Cursor / Windsurf / Cline](#cursor--windsurf--cline)
- [GitHub Copilot](#github-copilot)
- [Any Agent with RUN Capability](#any-agent-with-run-capability)
- [MCP Integration](#mcp-integration-preferred)
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

This codebase has an OKF v0.2 knowledge bundle at `./okf_bundle/`.

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

## MCP Integration (Preferred)

Expose your OKF bundle via Model Context Protocol — gives the agent direct tools for lookup, call-graph traversal, tag search, and manifest inspection, without running shell commands.

```bash
# Register MCP server in OpenCode and/or Claude Desktop configs
okf mcp --install

# Or start in stdio mode (for clients that auto-launch the server)
okf mcp ./okf_bundle
```

This works with any MCP client — OpenCode, Claude Desktop, Cursor, VS Code extensions, and custom MCP hosts.

**11 MCP tools exposed:** `lookup`, `get_concept`, `find_callers`, `find_callees`, `list_by_file`, `list_dependencies`, `bundle_info`, `list_by_type`, `search_by_tag`, `get_related`, `get_manifest_source`.

### Skill vs MCP: Two Separate Concerns

| Concern | What it does | Install command |
|---|---|---|
| **Skills / Rules** | Text instructions telling the AI *how* to use okf (read SUMMARY.md, run lookup, etc.) | `okf install <agent>` |
| **MCP Server** | Registers the server so the AI can call tools directly without shell commands | `okf mcp --install` or `okf install mcp` |

You can install skills without MCP (the AI reads instructions and runs shell commands), or use MCP without skills (the AI discovers tools automatically). For the best experience, do both.

## Agent Installation Command

The `okf install` command automates skill installation:

```bash
# Install skills for all agents + register MCP
okf install all

# Or pick specific agents
okf install claude      # Claude Code skill
okf install opencode    # OpenCode /lookup command
okf install copilot     # GitHub Copilot instructions
okf install cursor      # Cursor rules
okf install windsurf    # Windsurf rules
okf install cline       # Cline rules
okf install mcp         # Register MCP server (same as okf mcp --install)
```

**What each install does:**

| Command | Files created | Effect |
|---|---|---|
| `okf install claude` | `~/.config/opencode/skills/okf-generator/SKILL.md` | Auto-triggers on phrases like "index my codebase" |
| `okf install opencode` | `.opencode/commands/lookup.md` | `/lookup NAME=<ConceptName>` |
| `okf install copilot` | `.github/copilot-instructions.md` | Auto-loaded in VS Code |
| `okf install cursor` | `.cursorrules` | Auto-loaded by Cursor |
| `okf install windsurf` | `.windsurfrules` | Auto-loaded by Windsurf |
| `okf install cline` | `.clinerules` | Auto-loaded by Cline |
| `okf install mcp` | `opencode.json` + `claude_desktop_config.json` | Registers MCP server for tool-based access |
