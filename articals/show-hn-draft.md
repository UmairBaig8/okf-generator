------------------------------------------------------------------------------------------------------------------------------------------
Final
------------------------------------------------------------------------------------------------------------------------------------------

Hi HN,

After the hundredth time watching an AI coding assistant reread my entire codebase just to find one function signature, I realized we were solving the wrong problem. IDEs and compilers don't rebuild from scratch on every keystroke, so why do AI agents? 

That question eventually became OKF Generator. My hypothesis is that repository understanding should be a reusable artifact, not something every AI agent rebuilds from scratch every session.

Instead of repeatedly feeding raw source files into an LLM, it scans the repository once and builds a structured knowledge bundle. Looking up a function goes from ~14,000 tokens (reading a whole file) to ~140 tokens (one exact-match file). 

The core is deliberately boring and deterministic:
- Tree-sitter/AST parsing: Supports 18 languages and 17 dependency formats (pip, npm, cargo, go.mod, etc.).
- The core extraction runs entirely offline: Outputs plain Markdown + YAML frontmatter. No LLMs, vector DBs, or API keys required for base extraction.
- Symbol lookup is deterministic: It matches parsed symbols rather than relying on semantic similarity.
- Incremental sync: okf update --watch uses a SHA256 manifest to only re-index changed files in the background as you code.

Two optional layers sit on top if you want them:
- okf enrich --lsp: Uses local language servers (pyright, gopls, rust-analyzer, etc.) for compiler-accurate call graphs at zero token cost.
- okf enrich --llm: Adds natural language summaries if you point it at a local or remote model.

Integration:
- Built-in MCP server to query the bundle directly.
- One-command setup for agents: okf install claude / cursor / copilot / windsurf

GitHub: https://github.com/UmairBaig8/okf-generator
Docs & Live Demo: https://umairbaig8.github.io/okf-generator/
Design notes: https://www.linkedin.com/feed/update/urn:li:activity:7481012073091645440/

Quickstart:
pip install okf-generator
okf generate . ./okf_bundle
okf lookup <ConceptName>

Happy to dig into the tree-sitter integration, why static AST works well for this use case, or anything else!

------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------




title: Show HN: I got tired of AI agents re-reading whole files, so I built this

url: https://umairbaig8.github.io/okf-generator/

text:

Instead of an agent reading a 600-line file to find one method signature, it runs okf lookup <Name> and gets back ~140 tokens of exact, typed context instead of ~14,000.

A few specifics:
- Extraction is fully deterministic and offline — no LLM call unless you explicitly turn on enrichment (works with any OpenAI-compatible endpoint, including local llama.cpp/Ollama).
- 17 languages (Python, JS/TS, Go, Java, Rust, Swift, Kotlin, Ruby, C, C++, C#, SQL, PHP, Dart, Scala, Julia), 22 manifest formats (pip, npm, cargo, go.mod, maven, Dockerfile, etc.) for dependency queries like "which services still depend on this vulnerable package."
- One-command agent setup: okf install claude / okf install cursor / okf install copilot — writes the exact rules each agent needs. Also ships an MCP server (okf mcp) exposing 11 tools.
- ~97% token savings per lookup (45K → 1.2K tokens). Local SLMs on a MacBook become viable for enterprise-scale codebases.
- 242 tests passing, MIT licensed, independent implementation of the OKF v0.1 spec.
- Output is plain markdown mirroring your source tree — diffs cleanly, safe to commit alongside the code it describes.

Honest limitations: it's early (v0.1.x), the cross-reference linker doesn't yet resolve dynamic dispatch or reflection-heavy code well, and a couple of the 17 language parsers are more battle-tested than others (Python and JS/TS the most; C#/SQL/Dart/Scala the newest). I'd rather say that upfront than have people find out the hard way.

GitHub: https://github.com/UmairBaig8/okf-generator
Site: https://umairbaig8.github.io/okf-generator/

Feedback on the linker accuracy or missing language support especially welcome — that's where I'd focus next.



-----------

**Title (pick one):**

1. Show HN: OKF Generator – cut AI coding agent context from 45K to 1.2K tokens
2. Show HN: I stopped my AI agent from re-reading whole files to find one function
3. Show HN: OKF Generator – deterministic AST maps for AI coding agents, 97% fewer tokens

Go with #1. Numbers in the title outperform vague claims on HN, and "45K to 1.2K" is concrete enough to make people click without sounding like a stat you made up.

**Post body:**

---

Hi HN,

I built okf-generator because I got tired of watching AI coding agents burn 14-45K tokens re-reading entire files just to find one function signature.

The idea: instead of dumping raw files into context, scan the codebase once into structured "concept cards" — one per function/class/module — with typed edges for calls, callers, and dependencies. Looking up a concept becomes a ~1,200 token lookup instead of a 45,000 token file read. About 97% smaller, and it's exact-symbol retrieval, not embedding-similarity guesswork like RAG.

Core extraction is 100% offline and deterministic — tree-sitter + stdlib AST across 17 languages, no LLM calls, no vector DB, no API key required. Same output every run. There's an optional enrichment layer (LSP or LLM) if you want deeper descriptions or call-graph refinement, but the base bundle is fully useful without any of that.

It ships an MCP server (11 tools) so Claude Code, Cursor, or any MCP client can query the bundle directly, plus one-command installs for Claude/Cursor/Copilot/Windsurf/Cline agent configs.

GitHub: https://github.com/UmairBaig8/okf-generator
Docs: https://umairbaig8.github.io/okf-generator/docs-site/
Live demo: https://okf-generator.onrender.com

`pip install okf-generator` → `okf generate . ./okf_bundle` → `okf lookup <ConceptName>`

Happy to dig into the tree-sitter integration, the cross-reference linker, or why static AST beat embeddings for this use case.

---





------------------

**Top comment — variant A (origin story angle):**

---

Author here. Backstory: I was running local SLMs against a mid-size codebase and kept hitting the same wall — every time the agent needed one class, it read the whole file, chewed through half its context window, and had nothing left for the actual task.

Tried RAG first. It "worked" but chunk boundaries didn't respect syntax — a function would get split mid-body, or a class definition would land in one chunk and its methods in another. The agent got context, just not the *right* context, and confidently hallucinated call relationships that weren't there.

Switched to a different bet: don't chunk text, parse the AST. Every function/class/module becomes its own file with a proper signature, docstring, and resolved call edges. It's basically ctags for the LLM era, except the output is agent-readable Markdown instead of a binary index.

The 97% number isn't cherry-picked — it's the median across a few real repos I tested against (StockAI-style connector modules, a Go microservice, a Rust CLI). Happy to share the actual benchmark script if anyone wants to run it against their own code.

---

**Variant B (more technical/HN-native, leads with the interesting decision):**

---

Author here. The interesting design decision was refusing to use embeddings at all.

Everyone's first instinct for "give agents better code context" is RAG — chunk the repo, embed it, do similarity search. I tried that path first and abandoned it: embeddings don't understand that `def foo():` and its call sites are related unless you explicitly build that graph, and chunk boundaries don't respect syntax, so you get truncated functions and orphaned methods.

So instead: tree-sitter AST extraction (stdlib `ast` for Python) into typed concept nodes — Function, Class, Module — with a two-pass linker resolving imports→dependencies and calls→callers/callees. No embeddings, no vector DB, no LLM in the core path. Same input always produces the same bundle.

Trade-off: it's exact-symbol lookup, not semantic search. You can't ask "find the auth logic" and get a fuzzy match the way you can with embeddings. You *can* fuzzy-match on symbol names though (`okf lookup repo` finds `UserRepository`), and there's an optional `ask` command that layers an LLM on top for the natural-language case.

Genuinely curious if anyone's hit the same RAG-imprecision wall and solved it differently.

---

A is friendlier/relatable, B baits technical discussion (better for HN comment engagement). Pick B if you want debate in the thread, A if you want warmth. My call: **B** — HN rewards "here's a tradeoff I made, argue with me" way more than origin stories.