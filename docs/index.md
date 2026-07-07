# okf-generator

**Parse any codebase into structured, agent-ready knowledge. High-velocity extraction across 17 languages — zero LLM required.**

```bash
pip install okf-generator
okf generate ./my_project ./okf_bundle
okf lookup --bundle ./okf_bundle FunctionName
```

## Why okf-generator?

- **Zero-LLM extraction** — Fully deterministic, offline. tree-sitter AST parsers extract every symbol with no API calls. Works in airgapped environments.
- **Surgical token efficiency** — Agents retrieve one concept card (signature + params + callers) instead of reading entire files. 80-95% fewer tokens.
- **Cross-linked knowledge** — Imports → dependencies, function calls → caller/callee resolved across all 17 languages. Multi-hop reasoning without grep.

## What you get

Every function, class, module, and dependency becomes a structured markdown file with YAML frontmatter:

```yaml
---
type: Function
title: slugify
resource: utils.py
signature: "def slugify(text: str, max_length: int = 80) -> str"
tags: [lang:python, type:Function]
---
```

Searchable via CLI, browseable via interactive dashboard, consumable via MCP protocol — all from one `okf generate` command.

## Next steps

| Step | Command |
|------|---------|
| [Installation](getting-started/installation.md) | `pip install okf-generator` |
| [Quick Start](getting-started/quick-start.md) | Generate your first bundle in 30 seconds |
| [CLI Reference](user-guide/cli-reference.md) | Full command reference |
| [Bundle Format](user-guide/bundle-format.md) | How the output is structured |
| [Dashboard](user-guide/visualization.md) | Launch the live bundle browser |
| [Changelog](changelog.md) | Release history |
