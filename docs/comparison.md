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

## okf-generator vs. similar tools

| | **okf-generator** | Sourcegraph | Graphify / CodeSee | dep-graph tools |
|---|---|---|---|---|
| **Focus** | Structured knowledge bundles for AI agents | Universal code search | Visual codebase maps | Dependency visualization |
| **Extraction** | Static AST parsing, offline | Server-side indexing | Static analysis | Package manager metadata |
| **Output** | Markdown bundle (portable, git-friendly) | Web UI + API | Visual graph (proprietary) | DOT/JSON/SVG graphs |
| **Offline** | ✅ Fully offline | ❌ Requires server | ⚠️ Partial | ✅ Yes |
| **AI agent ready** | ✅ MCP, CLI, lookup cache | ✅ API | ❌ Visual-only | ❌ No |
| **CI/CD integration** | ✅ Built-in GitHub Action + impact diff | ❌ External | ❌ Not designed for CI | ✅ Can be scripted |
| **Cost** | Free, open-source (MIT) | Free tier + Enterprise | Free tier + Enterprise | Free, open-source |
| **Self-hostable** | ✅ Yes, pip install | ✅ Yes (Docker) | ✅ Yes (Docker) | ✅ Yes |
| **Language count** | 17 languages | 30+ languages | 10+ languages | Varies |
| **Enrichment** | 4 LLM tiers, multi-provider | ℹ️ Cody AI assistant | ❌ Not supported | ❌ Not supported |

### Sourcegraph

Sourcegraph is a universal code search engine. It indexes your entire codebase and provides cross-references, search, and AI features (Cody). Where okf-generator produces a portable, git-friendly bundle, Sourcegraph requires a running server.

**Use Sourcegraph when:** you need always-on code search across many repositories with a web UI for human developers.

**Use okf-generator when:** you need a portable knowledge bundle for AI agents, CI/CD pipelines, or offline use.

### Graphify / CodeSee

Graphify and CodeSee are visual code exploration platforms. They generate interactive maps of codebases showing file dependencies, call graphs, and architecture. Output is visual-first and proprietary.

**Use Graphify/CodeSee when:** you need visual architecture diagrams for onboarding or code review.

**Use okf-generator when:** you need structured machine-readable knowledge for AI agents, not human-facing diagrams.

### Dependency analysis tools (dep-graph, dependency-cruiser, cargo-deps)

These tools focus narrowly on dependency graphs from package managers. They produce DOT or JSON files that can be rendered as graphs.

**Use dep-graph tools when:** you only need package-level dependency visualization.

**Use okf-generator when:** you need full knowledge bundles including function-level cross-references, call graphs, and concept lookups across multiple languages.

## When to use what

**Use okf-generator** when you need deterministic, offline, cross-referenced knowledge from a codebase — without burning API credits or context windows.

**Use RAG / vector search** when you need semantic similarity search across unstructured documentation, not exact symbol lookup.

**Use manual docs** (README, wiki) for high-level architectural guidance and onboarding narratives that automated extraction can't capture.

**Use LLM-only** for one-off questions about small codebases where speed doesn't matter.

**Use Sourcegraph** when you have a large multi-repo environment and need always-on web-based code search for human developers.

**Use Graphify/CodeSee** when onboarding new team members who need visual architecture maps.

## Why not both?

okf-generator bundles are plain markdown — they can be indexed by any vector store alongside your existing docs. The bundle serves as the **deterministic symbol layer** while RAG handles the **fuzzy semantic layer**. They complement each other.
