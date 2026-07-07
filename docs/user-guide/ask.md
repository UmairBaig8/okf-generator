# Codebase Q&A (`okf ask`)

`okf ask` lets you ask natural language questions about your codebase. It searches the knowledge bundle for relevant concepts and uses your configured LLM to answer — no more grepping through files or guessing function names.

## Quick start

```bash
# Configure an LLM provider first
okf config llm.api_key=sk-...
okf config llm.base_url=https://api.deepseek.com/v1
okf config llm.model=deepseek-v4-flash

# Ask questions
okf ask "how does the payment service work"
okf ask "what dependencies does this project use"
okf ask "find all API endpoints"
```

## How it works

```
Your question
    │
    ▼
┌─────────────────┐
│  1. Parse query  │  Remove stop words (how, does, the, what...)
└────────┬────────┘
         │ tokens: ["slugify", "function"]
         ▼
┌─────────────────┐
│  2. Search       │  Fuzzy match against concept titles,
│     bundle       │  descriptions, and tags via okf.lookup
└────────┬────────┘
         │ top 8 relevant concepts
         ▼
┌─────────────────┐
│  3. Build        │  Pack title, type, signature, description,
│     context      │  related links into a text block
└────────┬────────┘
         │ context + question → LLM
         ▼
┌─────────────────┐
│  4. LLM answers  │  Uses only the provided context —
│                  │  no internet, no training data
└────────┬────────┘
         │ natural language answer
         ▼
      You see the answer
```

## Examples

```bash
# Architecture questions
okf ask "how does the payment service work"
okf ask "what classes handle user authentication"

# Dependency questions
okf ask "what dependencies does this project use"
okf ask "which packages use serde"

# API discovery
okf ask "find all API endpoints"
okf ask "what functions are available in the utils module"

# Specific file questions
okf ask "what does slugify do"
okf ask "how is the database configured"
```

## Requirements

- A configured LLM provider (see [Configuration](../getting-started/configuration.md))
- A generated bundle (`okf generate`)
- `openai` package installed (`pip install "okf-generator[llm]"`)

## No LLM? Use `okf lookup`

If you don't have an LLM configured, `okf ask` will tell you. Use `okf lookup` instead for exact-symbol search — it's faster and works offline:

```bash
okf lookup slugify
okf lookup --type Function --tag lang:rust
okf lookup --file src/payment/handler.py
```

## How it's different from `okf lookup`

| | `okf lookup` | `okf ask` |
|---|---|---|
| Query type | Symbol name (exact/fuzzy) | Natural language question |
| LLM needed | No | Yes |
| Speed | Milliseconds | Seconds |
| Output | Structured concept card | Natural language answer |
| Use case | "Find this function" | "How does this work?" |

## Privacy

`okf ask` only sends concept cards from the bundle to the LLM — these are the same markdown files that are already stored in your bundle directory. No raw source code is sent. The question is sent alongside the concept context.

If you use a local LLM (Ollama, llama.cpp), nothing leaves your machine.
