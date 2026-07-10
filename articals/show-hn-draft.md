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