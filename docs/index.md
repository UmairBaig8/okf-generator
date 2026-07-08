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

<p align="center">
  <a href="https://umairbaig8.github.io/okf-generator/viz.html"><b>Live Viz Graph</b></a>
  <span>&nbsp;&middot;&nbsp;</span>
  <a href="https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=UmairBaig8/okf-generator"><b>Dev Container</b></a>
  <span>&nbsp;&middot;&nbsp;</span>
  <a href="https://okf-generator.onrender.com"><b>Render App</b></a>
</p>

## Visual Showcase

<div id="okf-term" style="background:#0d1117;border-radius:12px;padding:20px 24px;font-family:'JetBrains Mono',monospace;font-size:13px;line-height:1.6;color:#c9d1d9;max-width:640px;margin:0 auto 24px;box-shadow:0 8px 32px rgba(0,0,0,0.35);overflow:hidden;">
  <div style="display:flex;gap:6px;margin-bottom:14px;">
    <span style="width:11px;height:11px;border-radius:50%;background:#ff5f56;display:inline-block;"></span>
    <span style="width:11px;height:11px;border-radius:50%;background:#ffbd2e;display:inline-block;"></span>
    <span style="width:11px;height:11px;border-radius:50%;background:#27c93f;display:inline-block;"></span>
  </div>
  <pre id="okf-term-body" style="margin:0;white-space:pre-wrap;word-break:break-word;min-height:340px;"></pre>
</div>
<script>
(function(){
  const lines = [
    {type:"cmd", text:"okf generate . ./okf_bundle"},
    {type:"out", text:"21:28:21 [INFO] Scanning 2 paths...\n21:28:21 [INFO] Linking: 2 call edges resolved\n21:28:21 [INFO] Found 6 concepts\n\n  Bundle: demo_project\n  Type            Concepts\n  ------------------------\n  Class                  2\n  Function               3\n  Module                 1\n  ------------------------\n  TOTAL                  6\n\n21:28:21 [INFO] OKF bundle written -> ./okf_bundle\n"},
    {type:"cmd", text:"okf lookup WorldBankConnector"},
    {type:"out", text:"CLASS: WorldBankConnector\n  Description : Fetches World Bank development indicators via wbdata API.\n  Source      : connectors/economic_data.py  line 6\n  Methods     : get_indicator, search\n  Related     : economic_data, get_indicator, search\n\nFUNCTION: get_indicator\n  Signature   : def get_indicator(self, indicator_code: str, country: str = 'US') -> pd.DataFrame\n  Returns     : pd.DataFrame\n  Related     : WorldBankConnector\n"}
  ];
  const body = document.getElementById('okf-term-body');
  let li = 0, ci = 0;
  function typeChar(){
    if (li >= lines.length) return;
    const line = lines[li];
    const prefix = line.type === 'cmd' ? '$ ' : '';
    if (ci === 0 && line.type === 'cmd') body.innerHTML += '\n' + '<span style="color:#7ee787">' + prefix + '</span>';
    if (ci < line.text.length){
      const span = line.type === 'cmd' ? '<span style="color:#e6edf3">' : '<span style="color:#8b949e">';
      body.innerHTML += span + line.text[ci].replace(/\n/g,'<br>') + '</span>';
      ci++;
      setTimeout(typeChar, line.type === 'cmd' ? 28 : 4);
    } else {
      li++; ci = 0;
      setTimeout(typeChar, 400);
    }
  }
  typeChar();
})();
</script>

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
