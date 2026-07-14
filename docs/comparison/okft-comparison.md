# Comparison: okf-generator vs okft

Both tools operate on the Open Knowledge Format (OKF), but they serve fundamentally different roles
in the OKF ecosystem. This report covers what each does, where they overlap, and whether
they compete or complement.

---

## At a glance

| Dimension | okf-generator | okft |
|-----------|--------------|------|
| **What it is** | Bundle generator + enricher + server | Bundle linter + MCP server |
| **Version** | v0.1.48 | v0.1.0 |
| **OKF spec** | v0.2 (extended dialect of Google's v0.1) | v0.1 |
| **License** | MIT | Apache-2.0 |
| **Author** | Umair Baig | Poorva |
| **PyPI** | `okf-generator` | `okft` |
| **Stars** | ~40 | 0 |
| **Release date** | Jul 2026 | Jul 2026 |

---

## Core purpose

### okf-generator — Producer

Scans source code (17 languages via tree-sitter AST parsers) and generates OKF bundles from scratch.
Also enriches bundles with LSP call graph resolution and optional LLM summaries.
Serves bundles via MCP, HTTP dashboard, and interactive HTML visualization.

```
Source code → [Scanner] → [Linker] → [OKF Bundle] → [LSP/LLM Enrich] → [MCP / Viz / Dashboard]
```

### okft — Consumer

Takes an existing OKF bundle and validates its structure/spec conformance. Also serves
bundles to AI agents via MCP with read/search/list tools. Does NOT generate bundles
from source code.

```
OKF Bundle → [Linter] → [Validated Bundle]
           → [MCP Server] → AI Agent
```

---

## Feature comparison

| Feature | okf-generator | okft |
|---------|:------------:|:----:|
| **Bundle generation from source** | ✅ 17 languages | ❌ |
| **Manifest dependency scanning** | ✅ 12 ecosystems | ❌ |
| **Bundle linting / spec validation** | ❌ | ✅ 11 rules (E001-E004, W001-W007) |
| **MCP server** | ✅ 11 tools | ✅ 4 tools |
| **LSP enrichment** | ✅ 4 servers | ❌ |
| **LLM enrichment** | ✅ 3 modes | ❌ |
| **Cross-reference linker** | ✅ calls/called-by/related | ❌ |
| **Bundle diff** | ✅ `okf diff` + `--impact` | ❌ |
| **Training pair generation** | ✅ `okf pairs` | ❌ |
| **Interactive visualization** | ✅ HTML graph (Cytoscape.js + WASM) | ❌ |
| **HTTP dashboard** | ✅ FastAPI | ❌ |
| **OKF spec version** | v0.2 (extended) | v0.1 |
| **Source code extraction** | ✅ | ❌ (no-op on source) |
| **Package size** | ~1.5 MB | ~16 KB |

---

## MCP tool comparison

Both expose an MCP server, but with different scope:

### okf-generator MCP tools (11)

| Tool | Description |
|------|-------------|
| `lookup` | Search concepts by name |
| `get_concept` | Full concept card by ID |
| `find_callers` | All callers of a concept |
| `find_callees` | All callees of a concept |
| `list_by_file` | Concepts in a source file |
| `list_dependencies` | All dependency concepts |
| `bundle_info` | Bundle metadata + stats |
| `list_by_type` | Filter by concept type |
| `search_by_tag` | Filter by tag |
| `get_related` | Related concepts (all edge types) |
| `get_manifest_source` | Original manifest file content |

### okft MCP tools (4)

| Tool | Description |
|------|-------------|
| `okf_overview` | Root index + concepts grouped by type |
| `okf_read` | Single concept (frontmatter, body, links) |
| `okf_search` | Ranked full-text search with snippets |
| `okf_list` | Filter by type and/or tag |

---

## Complementary, not competitive

The two tools solve different problems in the same ecosystem:

| Stage | Tool |
|-------|------|
| **Create** bundle from source code | `okf-generator` |
| **Enrich** bundle (LSP/LLM) | `okf-generator` |
| **Validate** bundle spec conformance | `okft` |
| **Serve** bundle to AI agents | Both (different tooling depth) |
| **Visualize** bundle | `okf-generator` |
| **Diff** bundle versions | `okf-generator` |

A natural workflow:

```bash
# 1. Generate bundle from source
okf generate ./src ./okf_bundle

# 2. Validate spec conformance
okft lint ./okf_bundle

# 3. Serve to AI agent (either works)
okf mcp ./okf_bundle
# or
okft serve ./okf_bundle
```

okft fills a gap okf-generator doesn't cover: spec validation. okf-generator focuses on
extraction, enrichment, and serving. Neither replaces the other.

---

## Areas where okf-generator could learn from okft

1. **Bundle linting** — okft's 11 validation rules (orphaned concepts, broken links, malformed
   timestamps, missing frontmatter fields) are not currently implemented in okf-generator.
   Adding an `okf validate` command would improve bundle quality assurance.

2. **Spec compliance** — okft tracks Google's OKF v0.1 spec. okf-generator uses an extended
   v0.2 dialect. Documenting where the dialect diverges and providing a validation mode
   would help interoperability with okft and other OKF tools.

---

## Summary

| | okf-generator | okft |
|---|---|---|
| Best at | **Generating** OKF bundles from code | **Validating** existing OKF bundles |
| Should you install both? | Yes, if you generate bundles and want spec validation | Yes, if you need CI linting for hand-maintained bundles |
| Competition | None — they target different stages of the OKF lifecycle | None — same |
