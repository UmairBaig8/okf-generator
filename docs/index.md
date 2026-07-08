# OKF Generator
<p><strong>The knowledge layer for AI coding agents.</strong></p>

<p align="center">
  <img src="https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/images/okf_banner.png?v=2" alt="okf-generator demo" width="700">
</p>

<p align="center">
  <a href="https://pypi.org/project/okf-generator/"><img src="https://img.shields.io/pypi/v/okf-generator?style=flat-square&label=PyPI" alt="PyPI"></a>

  <a href="https://pypi.org/project/okf-generator/"><img src="https://img.shields.io/pypi/pyversions/okf-generator?style=flat-square" alt="Python"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/stargazers"><img src="https://img.shields.io/github/stars/UmairBaig8/okf-generator?style=flat-square" alt="GitHub Stars"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/actions"><img src="https://img.shields.io/github/actions/workflow/status/UmairBaig8/okf-generator/ci.yml?style=flat-square&label=tests" alt="Tests"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/commits/main"><img src="https://img.shields.io/github/last-commit/UmairBaig8/okf-generator?style=flat-square" alt="Last commit"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="MIT"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/blob/main/SKILL.md"><img src="https://img.shields.io/badge/Claude-Skill-orange?style=flat-square&logo=anthropic" alt="Claude Skill"></a>
  <a href="https://github.com/UmairBaig8/okf-generator/blob/main/CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square" alt="PRs Welcome"></a>
  <a href="https://umairbaig8.github.io/okf-generator/docs-site/"><img src="https://img.shields.io/badge/📖-Docs-7c3aed?style=flat-square" alt="Docs"></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-Server-5b21b6?style=flat-square" alt="MCP"></a>
  <a href="https://www.cursor.com"><img src="https://img.shields.io/badge/Cursor-Ready-7c3aed?style=flat-square" alt="Cursor"></a>
  <a href="https://github.com/anthropics/claude-code"><img src="https://img.shields.io/badge/Claude-Ready-7c3aed?style=flat-square&logo=anthropic" alt="Claude"></a>
</p>

<p align="center">
  <b>Scan any codebase into structured, agent-ready knowledge — 17 languages, ~100x fewer tokens than reading whole files, zero LLM required.</b>
</p>

okf-generator generates an [OKF v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) conformant knowledge bundle — structured Markdown that AI agents can query instead of re-reading whole files. Zero-LLM extraction, fully offline, deterministic every run.

---

## Quick Start

```bash
pip install okf-generator
cd my_project && okf generate
okf lookup WorldBankConnector
okf ask "how does the payment service work"
```

That's it — no API key, no vector DB, no config required to get value.

## Why

Agents waste tokens re-reading entire files to find one function signature — 14,000+ tokens for a 600-line file. `okf lookup` returns the exact concept card — signature, params, callers, callees — in about 140 tokens.

<div class="grid cards" markdown>

- :material-lightning-bolt:{ .lg } **Zero-LLM extraction**
  Deterministic, offline-capable. tree-sitter + AST parsers, no API calls required.
  [→ How it works](getting-started/quick-start.md)

- :material-graph:{ .lg } **17 languages, 17 manifest formats**
  Python, JS/TS, Go, Java, Rust, Swift, Kotlin, Ruby, C/C++/C#, SQL, PHP, Dart, Scala, Julia.
  [→ Language coverage](user-guide/languages-and-manifests.md)

- :material-robot:{ .lg } **Works with your agent**
  One command installs into Claude Code, Cursor, Copilot, Windsurf, Cline, OpenCode.
  [→ Agent integration](user-guide/agent-integration.md)

- :material-file-tree:{ .lg } **MCP server built in**
  11 tools — lookup, get_concept, find_callers, find_callees, search_by_tag, and more — exposed over Model Context Protocol.
  [→ MCP Server](user-guide/mcp-server.md)

- :material-cog:{ .lg } **LLM enrichment, optional**
  Four tiers — base, deep, security, full. Layer on top when you want it, never required.
  [→ Enrichment guide](user-guide/enrichment.md)

- :material-source-branch:{ .lg } **CI/CD ready**
  Built-in GitHub Action posts PR comments with dependency impact analysis.
  [→ CI/CD guide](user-guide/ci-cd.md)

</div>

## Where to Go Next

| I want to... | Go to |
|---|---|
| Install and generate my first bundle | [Getting Started](getting-started/installation.md) |
| See every CLI command | [CLI Reference](user-guide/cli-reference.md) |
| Understand the bundle file format | [Bundle Format Reference](user-guide/bundle-format.md) |
| Wire this into my agent | [Agent Integration](user-guide/agent-integration.md) |
| Compare to RAG / reading whole files | [Comparison](comparison.md) |
| Fix an error I'm hitting | [Troubleshooting](troubleshooting.md) |
| See what changed between versions | [Changelog](changelog.md) |
| Contribute a language parser | [Development](development/architecture.md) |

## FAQ

**Does this require an API key or internet connection?**
No. Core extraction (`okf generate`) is fully offline and deterministic. LLM enrichment via `--enrich` is optional and only kicks in if you explicitly enable it.

**How is this different from RAG or vector search?**
RAG retrieves by semantic similarity — approximate, can miss exact symbols. `okf lookup` is exact-match against real functions, classes, and dependencies, with zero embedding infrastructure. Same result every run. Full comparison [here](comparison.md).

**Does this work on monorepos or very large codebases?**
Yes. Scanning is linear in file count; scope `okf generate` to a subdirectory if you only need part of the repo indexed.

**Is the bundle safe to commit to git?**
Yes — that's the intended workflow. Bundles are plain Markdown with YAML frontmatter, diff cleanly, and version alongside the code they describe.

**Can I use this without any LLM at all, ever?**
Yes. `okf generate` + `okf lookup` is a complete, zero-LLM workflow. Enrichment and training-pair synthesis are optional layers on top.

---

<!-- <p style="text-align:center; color:var(--md-default-fg-color--light); font-size:0.85em;">
© 2026 Umair Baig · MIT License · Not affiliated with Google · Implements <a href="https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md">OKF v0.1</a>
</p> -->
