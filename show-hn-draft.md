# Show HN draft — okf-generator

## Title (pick one, HN caps effective length ~80 chars)

Option A (recommended — leads with the mechanism, not a claim):
> Show HN: okf-generator – turn any codebase into an agent-readable knowledge graph

Option B (leads with the pain point):
> Show HN: I got tired of AI agents re-reading whole files, so I built this

Option C (shortest, most literal):
> Show HN: okf-generator – zero-LLM code indexing for AI agents (10 languages)

Avoid superlatives ("revolutionary", "blazing fast", "game-changing") — HN
downvotes hype on sight. Option A is safest: it states the mechanism and lets
readers judge if it's useful.

---

## Post body

I built this because I was indexing a large multi-domain codebase (Python
data connectors, ML pipelines, SQL schemas) and kept hitting the same wall:
giving an AI agent the whole repo as context is slow and burns tokens, and
local SLMs (Gemma, Llama, Phi) on a laptop just run out of memory if you try.

okf-generator scans a repo with tree-sitter AST parsers and writes one
markdown file per function, class, module, and dependency — cross-referenced
(calls, called-by, imports). Instead of an agent reading a 600-line file to
find one method signature, it runs `okf lookup <Name>` and gets back ~140
tokens of exact, typed context instead of ~14,000.

A few specifics:

- Extraction is fully deterministic and offline — no LLM call unless you
  explicitly turn on enrichment (works with any OpenAI-compatible endpoint,
  including local llama.cpp/Ollama).
- 10 languages (Python, JS/TS, Go, Java, Rust, Ruby, C, C++, C#, SQL), 17
  manifest formats (pip, npm, cargo, go.mod, maven, etc.) for dependency
  queries like "which services still depend on this vulnerable package."
- Ships an MCP server (`okf mcp`) and one-line installs for Claude Code,
  Cursor, Copilot, Windsurf, Cline, OpenCode.
- Output is plain markdown mirroring your source tree — diffs cleanly, safe
  to commit alongside the code it describes.

Honest limitations: it's early (v0.1.x), the cross-reference linker doesn't
yet resolve dynamic dispatch or reflection-heavy code well, and a couple of
the 10 language parsers are more battle-tested than others (Python and
JS/TS the most; C#/SQL the newest). I'd rather say that upfront than have
people find out the hard way.

MIT licensed, independent implementation of the OKF v0.1 spec (not affiliated
with or endorsed by Google).

GitHub: https://github.com/UmairBaig8/okf-generator
Site: https://umairbaig8.github.io/okf-generator/

Feedback on the linker accuracy or missing language support especially
welcome — that's where I'd focus next.

---

## Timing notes (this affects outcome more than the copy does)

- Post Tuesday–Thursday, ~8–10am US Eastern. Weekend and Friday posts get
  much less traffic — HN's active crowd is smallest then.
- Reply to every comment in the first hour, especially critical ones.
  Defensive replies kill threads; "good catch, opening an issue for that"
  keeps them alive.
- Don't ask friends to upvote in the first hour — HN's ranking algorithm
  penalizes suspicious vote velocity and can flag/kill the post.
- Have `okf generate` runnable in under 2 minutes for someone who just
  cloned the repo. The first comment is often "tried it, here's what broke."
