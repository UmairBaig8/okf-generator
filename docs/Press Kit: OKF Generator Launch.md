Press Kit: OKF Generator Launch

Press Release: The Knowledge Layer for AI Coding Agents

FOR IMMEDIATE RELEASE

Deterministic AST Retrieval Replaces Naive RAG as the "Unlock" for Local AI Coding Agents

The launch of OKF Generator signals a definitive end to the era of "context-stuffing" and the inefficiencies of Naive RAG in AI-assisted development. By introducing a dedicated knowledge layer built on deterministic Abstract Syntax Tree (AST) parsing, the tool provides the critical architectural unlock needed to make local Small Language Models (SLMs) viable for enterprise-scale engineering.

Current industry standards force AI agents to waste enormous amounts of context re-reading entire source files just to locate a single function signature or dependency version. While a 600-line file can consume over 14,000 tokens—leading to "model memory starvation"—an OKF lookup provides a surgical "concept card" in approximately 140 tokens. This 100x reduction in token usage eliminates the context bloat that typically chokes local models like Gemma, Llama, and Phi on consumer hardware.

"We are moving beyond the point where 'more context' is the answer. Context-stuffing is a tax on both performance and privacy," said Umair Baig, creator of OKF Generator. "By converting source code into deterministic, cross-referenced knowledge bundles, we stop the 'shredding' of class context common in vector-based RAG and give agents an exact mathematical map of the codebase."

OKF Generator is a 100% offline, zero-LLM solution. Using Tree-sitter AST parsers, it extracts code structures with absolute reliability, ensuring information is reproducible every run. Because the core indexing process requires zero external API calls, it is fully air-gap compatible and operates with zero-latency local network sockets, protecting proprietary IP while delivering indexed lookups in 3–4ms.

Product Fact Sheet: Technical Specifications

OKF Generator at a Glance

Feature Category	Specifics
Token Efficiency	~100x reduction (97% context compression); ~140 tokens per concept card
Language Support	17 Languages: Python, JS/TS, Go, Java, Rust, Swift, Kotlin, PHP, Dart, Scala, Julia, Ruby, C, C++, C#, SQL
Manifest Support	22 Formats: requirements.txt, pyproject.toml, package.json, Cargo.toml, Cargo.lock, yarn.lock, pnpm-lock.yaml, go.mod, go.sum, poetry.lock, composer.json, pom.xml, Gemfile, build.gradle, build.gradle.kts, Package.swift, project.clj, mix.exs, Dockerfile, Containerfile, docker-compose.yml, .okfconfig
Core Technology	Tree-sitter AST parsers; deterministic cross-reference linker
Compliance	OKF v0.1 conformant (Open Knowledge Format)
License	MIT

The Architectural Paradigm Shift: Naive RAG vs. Deterministic AST

Feature	Naive RAG / Vector Search	Reading Whole Files	OKF Generator
Symbol Retrieval	Approximate (chunk similarity)	Manual scan	Precise AST lookup
Context Integrity	Shreds class/scope context	Retains context	Maps call hierarchies
Token Cost	High (Varies by chunk)	Extreme (14,000+ tokens)	Low (~140 tokens)
Search Logic	Semantic only	Grep / Regex	Fuzzy / camelCase search
System Impact	Embedding API latency	Model Memory Starvation	3–4ms indexed lookup
Infrastructure	Vector DB + API Key	Fully offline	Air-gap compatible

Developer Workflow & Agent Integration

OKF Generator integrates into the professional developer workflow via a single okf install command, automating setup for the industry's leading AI agents:

* Claude Code: Automates setup of a dedicated "skill" that auto-triggers when an agent needs to "index my codebase."
* Cursor & Windsurf: Generates .cursorrules or .windsurfrules files to provide agents with local codebase context without manual prompt engineering.
* GitHub Copilot: Automatically populates copilot-instructions.md to guide VS Code's native agent.
* MCP Server: Exposes 11 specialized tools via the Model Context Protocol, allowing agents to perform surgical queries. Key tools include:
  * lookup: Exact-symbol retrieval.
  * find_callers / find_callees: Navigate the call hierarchy.
  * list_by_file: Inspect all concepts within a specific source path.
  * get_manifest_source: Audit raw dependency declarations.
  * search_by_tag: Query by ecosystem (e.g., ecosystem:pip).

Technical Talking Points: Engineering Communities

* Privacy First (Air-Gapped): Core extraction is 100% offline. Zero code leaves the local environment. The tool utilizes zero-latency local network sockets, ensuring that sensitive IP never hits a third-party cloud during the indexing phase.
* No "Shredding" of Context: Unlike vector RAG—which breaks code into arbitrary text chunks—AST parsing preserves the call hierarchy and structural relationships. This eliminates hallucinations and "shredding" errors where class methods lose their connection to parent objects.
* The SLM Unlock: By providing surgically small 200–300 token summaries instead of 40k+ token raw files, OKF Generator makes local Small Language Models (Gemma, Llama, Phi) highly effective on consumer hardware like MacBooks.
* Deterministic Reliability: Information is extracted mathematically, not statistically. The result of a code scan is the same every time, providing a "Source of Truth" that agents can trust.
* CI/CD Native Impact Analysis: The built-in GitHub Action automates bundle generation and performs dependency impact analysis on PRs, highlighting how a version bump in a manifest (like Cargo.toml) affects specific code nodes.

Feature Deep Dive: Optional LLM Enrichment

While core extraction is zero-cost and deterministic, users can layer on LLM insights using a multi-provider routing system. This allows routing cheap work (descriptions) to local models while using cloud models for high-stakes security audits.

* Base: Standardizes and improves descriptions and docstrings using Google-style formatting.
* Deep: Generates usage examples, side effects, and complexity estimates.
* Security: Audits the structural bundle for visible risk patterns (e.g., injection vectors, auth bypasses).
* Full: The comprehensive tier including all above modes plus semantic related-links across concepts.

Frequently Asked Questions (FAQ)

Does this require an API key or internet connection? No. Core extraction (okf generate) and symbol retrieval (okf lookup) are fully offline and deterministic. No LLM calls are made unless enrichment is explicitly enabled.

How is this different from RAG? Vector-based RAG uses semantic similarity, which is approximate and often misses exact symbols or shreds class context. OKF Generator indexes real functions, classes, and dependencies by name for exact-symbol retrieval with 3–4ms latency and zero embedding infrastructure.

Does it work with monorepos? Yes. The scanning process is linear, and for large-scale repositories, OKF uses a SUMMARY.md discovery mechanism to navigate sub-bundles and scoped directories efficiently.

Is it safe to commit bundles to Git? Yes. Bundles are plain Markdown files with YAML frontmatter. They are designed to be versioned alongside the code, ensuring the AI agent always operates on the current source of truth.

Media Assets & Links

* Repository: GitHub - UmairBaig8/okf-generator
* Documentation: Official Docs Site
* Package: PyPI - okf-generator
* Visual Showcase:
  * Interactive Viz Graph: A self-contained, force-directed D3.js graph featuring color-coded nodes (Class, Function, Module, Dependency) and relationship edges for calls and imports.
  * Live Dashboard: A FastAPI-powered UI with a 3-panel layout, global graph networks, and dark/light theme persistence.

About the Creator

Umair Baig is a developer focused on optimizing the interface between source code and artificial intelligence. OKF Generator is an independent, third-party implementation of the Open Knowledge Format (OKF) v0.1 specification introduced by Google Cloud. This project is not built, maintained, or endorsed by Google; it is a community-driven tool designed to bridge the gap between complex codebases and AI agent context constraints.
