# Comparison

## okf-generator vs. other approaches

| | **okf-generator** | RAG / vector search | Manual docs | LLM-only |
|---|---|---|---|---|
| **Language coverage** | 17 languages, modular parsers | Any (embedding model dependent) | Manual | Any (context window dependent) |
| **Extraction** | Zero-LLM, deterministic, offline | Embedding step (often cloud) | Manual authorship | Full file reading (costly) |
| **Cross-references** | Imports→deps, calls→callee across all languages | Semantic similarity (approximate) | Manual | Implicit in context |
| **Dependency parsing** | 17 manifest formats | Not supported | Manual | Not reliable |
| **Token efficiency** | One concept card (~200 tokens) | Chunk-based (varies) | Varies | Full files (10K+ tokens) |
| **Enrichment** | 4 tiers, multi-provider routing | N/A | N/A | Single pass |
| **CI/CD** | Built-in GitHub Action + impact diff | Vector DB sync needed | Manual review | Not practical |
| **Agent integration** | MCP, CLI, lookup cache | API-dependent | Manual | Chat interface |
| **Training data** | Built-in JSONL generator (5 pair types) | Not typically included | Not applicable | Prompt-based |

## When to use what

**Use okf-generator** when you need deterministic, offline, cross-referenced knowledge from a codebase — without burning API credits or context windows.

**Use RAG / vector search** when you need semantic similarity search across unstructured documentation, not exact symbol lookup.

**Use manual docs** (README, wiki) for high-level architectural guidance and onboarding narratives that automated extraction can't capture.

**Use LLM-only** for one-off questions about small codebases where speed doesn't matter.

## Why not both?

okf-generator bundles are plain markdown — they can be indexed by any vector store alongside your existing docs. The bundle serves as the **deterministic symbol layer** while RAG handles the **fuzzy semantic layer**. They complement each other.
