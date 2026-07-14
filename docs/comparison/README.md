# Comparisons

- [OKF Generator vs OpenWiki](./) — code-to-knowledge vs clipboard-to-wiki
- [OKF Generator vs okft](./okft-comparison.md) — bundle producer vs bundle consumer/validator

---

# OKF Generator vs OpenWiki — Comparison

## Quick Summary

| Dimension | OKF Generator | OpenWiki |
|---|---|---|
| **Purpose** | Codebase → structured knowledge graph for AI agents | Clipboard → personal wiki for humans |
| **Input** | Source code (13 langs, 20+ manifests) | Clipboard (text, URLs, images) |
| **Output** | Portable markdown bundles, CLI consumable | SQLite DB, desktop GUI |
| **AI Dependency** | Zero-AI by design (pure AST parsing) | AI-critical (LLM required for every op) |
| **Delivery** | PyPI package, CLI, MCP server | Tauri desktop app (DMG/MSI) |
| **Graph** | Typed edges: calls, extends, depends-on | TF-IDF cosine similarity on tag vectors |
| **Target User** | Developers, AI agents, CI/CD | Information workers, content collectors |
| **Language** | 10 programming languages | Natural language via LLM |
| **Offline** | Fully offline | Needs API keys |
| **Stars** | ~0 (new) | 513 |
| **Platform** | Cross-platform (Python) | macOS + Windows (Tauri) |
| **License** | MIT | MIT |

---

## Feature Comparison

| Feature | OKF Generator | OpenWiki |
|---|---|---|
| Code parsing (AST) | ✅ 13 languages, tree-sitter | ❌ |
| Dependency/manifest parsing | ✅ 20+ formats | ❌ |
| Call graph extraction | ✅ Cross-file resolution | ❌ |
| Cross-reference linking | ✅ imports→deps + calls | ❌ |
| Portable bundle output | ✅ Flat markdown files | ❌ (SQLite) |
| Bundle diff/versioning | ✅ `okf diff` | ❌ |
| Training data generation | ✅ JSONL pairs (5 types) | ❌ |
| MCP protocol | ✅ Stdio + HTTP/SSE | ✅ SQLite via npx |
| AI enrichment (optional) | ✅ 4 modes, multi-provider | ❌ (not optional) |
| Clipboard monitoring | ❌ | ✅ Background daemon |
| URL content extraction | ❌ | ✅ WeChat, X, YouTube, etc. |
| OCR / image capture | ❌ | ✅ macOS native + WinRT |
| Auto wiki compilation | ❌ | ✅ AI-driven |
| Insight reports | ❌ | ✅ Weekly, 7-dimension |
| Knowledge graph viz | ✅ D3.js (static HTML) | ✅ D3 force graph (in-app) |
| GUI | ❌ (CLI only) | ✅ Full desktop GUI |
| Agent integrations | ✅ 6 agents (skills) | ✅ MCP for Claude Desktop |
| Preference learning | ❌ | ✅ Like/dismiss feedback loop |
| CI/CD integration | ✅ GitHub Action, Docker | ❌ |

---

## Pros & Cons

### OKF Generator

**Pros**
- Zero AI dependency — fully offline, no API costs, deterministic
- 13-language parser coverage with rich detail (signatures, params, inheritance, call graphs)
- Portable markdown bundles — easy to diff, version, cache, grep
- Designed for AI agent consumption — lookup, search, filter by type/tag/file
- Generates JSONL training pairs for fine-tuning
- MCP server + 6 agent integrations (Claude Code, OpenCode, Cursor, Copilot, Windsurf, Cline)
- 20+ dependency manifest formats
- CI/CD ready (GitHub Action, Docker, pre-commit)

**Cons**
- CLI only — no GUI, higher onboarding friction
- Narrow focus: source code only, no natural language content
- No user feedback loop or preference learning
- Smaller community / fewer stars
- Tree-sitter dependency for non-Python langs (native compilation needed)

### OpenWiki

**Pros**
- Beautiful desktop GUI with popup capture, graph viz, calendar timeline
- Broad input: any clipboard content (text, URLs, images, YouTube)
- AI enrichment: summarization, tagging, insight reports, attention analysis
- Privacy-first: local SQLite, no cloud
- Knowledge linting (orphan detection, broken links)
- Preference learning engine
- 513 GitHub stars, active community
- MCP protocol integration for Claude Desktop

**Cons**
- Completely dependent on AI — dead without API key and internet
- Proprietary SQLite format — not portable, diffable, or greppable
- Cannot analyze source code structurally (treats it as plain text)
- Non-deterministic — same input can produce different wiki page output
- No CI/CD pipeline integration
- No training data generation
- macOS/Windows only — no Linux, no CLI mode
- Platform-specific build issues (unsigned DMG, permission prompts)

---

## Architecture Differences

```
OKF Generator:
  Source Code → AST Parser → Concept Extraction → Linker (calls/deps)
    → OKF Bundle (markdown) → [Lookup | Diff | Pairs | Viz | MCP]

OpenWiki:
  Clipboard → AI Summarize → AI Assess → AI Compile → Wiki Pages (SQLite)
    → Knowledge Graph (TF-IDF cosine) → [Search | Graph | Reports | MCP]
```

---

## Impact & Synergy Analysis

### They Do Not Compete

OKF Generator and OpenWiki solve fundamentally different problems for different users:

| Dimension | OKF Generator | OpenWiki |
|---|---|---|
| **Persona** | Developer, CI/CD, AI agent | Information worker, knowledge collector |
| **Problem** | "How do I give my AI agent codebase context?" | "How do I organize everything I read?" |
| **Workflow** | `okf generate → okf lookup` in terminal | Copy → popup → wiki pages in GUI |

### Potential Synergy

1. **Code snippet capture in OpenWiki**: OpenWiki treats code as plain text. Routing code content through OKF Generator's tree-sitter parsers before wiki compilation would produce structured wiki pages with signatures, params, and call graphs.

2. **OKF bundle import into OpenWiki**: OpenWiki users could import OKF bundles as structured project knowledge, queryable alongside their personal notes.

3. **OpenWiki-style insight reports for codebases**: OKF Generator could adopt OpenWiki's attention analysis and weekly report patterns for code health trends (e.g., "this week you deleted 500 lines of dead code").

4. **Shared MCP ecosystem**: Both projects implement MCP servers. A unified MCP tool that queries both personal wiki + code knowledge would give agents a holistic view.

---

## When to Use Which

| If you need... | Use |
|---|---|
| Give Claude/OpenCode context about a codebase | **OKF Generator** |
| Capture and organize articles, tweets, notes | **OpenWiki** |
| Generate training data from source code | **OKF Generator** |
| Spot code smells and call-graph issues | **OKF Generator** |
| Track what you read and get AI insights | **OpenWiki** |
| CI/CD pipeline that diffs code knowledge | **OKF Generator** |
| Desktop app with GUI and popup capture | **OpenWiki** |
| Both — use them side-by-side, they don't overlap | **Both** |
