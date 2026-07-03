---
title: Stop feeding your AI agent the whole codebase
published: false
tags: ai, opensource, python, productivity
cover_image: https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/images/banner.png
---

If you've used Claude Code, Cursor, or Copilot on anything bigger than a
toy repo, you've felt this: you ask it to touch one function, and it reads
three files end-to-end to find the thing. That's thousands of tokens spent
just *locating* code, before any actual work happens.

It gets worse with local models. Point Gemma or Llama at a real repo on
a laptop and it just runs out of context before it's read half of it.

So I built **okf-generator** — a CLI that turns a codebase into a
structured knowledge bundle your agent can query instead of grep-and-read.

## The idea

Instead of this:

```
Agent reads economic_data.py (14,000 tokens)
  → finds WorldBankConnector somewhere in the middle
  → still has to find its callers separately
```

You get this:

```bash
$ okf lookup WorldBankConnector
```
```
CLASS: WorldBankConnector
Source    : connectors/economic_data.py  line 51
Methods   : get_indicator, search
Called by : DataPipeline.fetch_economic
```

~140 tokens. Exact. No re-reading, no grep, no guessing.

## How it works

1. **Scan** — tree-sitter (and native `ast` for Python) parses every
   function, class, module, and manifest dependency across 10 languages.
2. **Link** — cross-references get resolved: imports → dependencies,
   calls → callers/callees.
3. **Write** — outputs plain markdown, one file per concept, mirroring
   your source tree. Diffs cleanly, safe to commit.
4. **Consume** — `okf lookup`, or expose the whole thing over MCP with
   `okf mcp ./okf_bundle` if your agent speaks that.

None of the extraction requires an LLM call. It's deterministic — same
input, same output, every time. LLM enrichment is opt-in, for teams that
want richer descriptions, and it works with any OpenAI-compatible
endpoint (including local llama.cpp/Ollama).

## Try it

```bash
pip install okf-generator
okf generate ./your_project ./okf_bundle
okf lookup <SomeFunctionOrClass>
```

One-line agent setup:

```bash
okf install claude    # or cursor, copilot, windsurf, cline, opencode
```

## What it's not

It's not RAG. There's no embedding step, no vector DB, no similarity
search — `okf lookup` does exact symbol matching, not "closest chunk."
That's a deliberate tradeoff: for finding "what does this class do and
who calls it," exact beats approximate.

It's also young (v0.1.x). The linker doesn't yet handle dynamic dispatch
well, and some of the 10 language parsers are newer than others. If you
hit a language edge case, that's exactly the kind of issue I want.

10 languages, 17 manifest formats, MIT licensed, independent
implementation of Google's [OKF v0.1 spec](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

Repo: https://github.com/UmairBaig8/okf-generator
Site: https://umairbaig8.github.io/okf-generator/

Would genuinely like to hear what breaks if you point it at your own repo.
