# Codebase Q&A (`okf ask`)

`okf ask` lets you ask natural language questions about your codebase. It uses your configured LLM to extract key search terms from your question, finds the most relevant concepts in the bundle, and answers based on that context.

## Quick start

```bash
# Configure an LLM provider first
okf config llm.api_key=sk-...
okf config llm.base_url=https://api.deepseek.com/v1
okf config llm.model=deepseek-v4-flash

# Ask questions
okf ask "how does the payment service work"
okf ask "what dependencies does this project use"
```

## How it works

```
Your question
    │
    ▼
┌─────────────────┐
│  1. LLM extracts │  LLM reads the question and extracts
│     search terms │  2-5 key search terms
└────────┬────────┘
         │ terms: ["payment", "service", "api"]
         ▼
┌─────────────────┐
│  2. Search       │  Fuzzy match against concept titles,
│     bundle       │  descriptions, and tags
└────────┬────────┘
         │ top 8 relevant concepts
         ▼
┌─────────────────┐
│  3. Build        │  Pack title, type, signature, description
│     context      │  into a text block
└────────┬────────┘
         │ context + question → LLM
         ▼
┌─────────────────┐
│  4. LLM answers  │  Uses only the provided context
└────────┬────────┘
         │ answer + token usage
         ▼
      Q: what does slugify do?
      Converts text to a URL-safe slug...
      Tokens: 635 total · 395 reasoning
```

## Token usage

Each response shows token consumption:

```
  Tokens: 635 total · 395 reasoning
```

This includes both the term extraction step and the answer generation. Reasoning tokens (for models like DeepSeek) are shown separately. In chat mode, a session total is printed when you exit.

## Interactive chat mode

Run `okf ask` without a question to enter interactive chat:

```
$ okf ask
OKF Ask — interactive chat. Type your questions or /exit.

>>> what does slugify do

Converts text to a URL-safe slug...

Sources:
  [1] Function: slugify — utils.py
  Tokens: 635 total · 395 reasoning

>>> how is it different from chunk_list

slugify transforms strings, chunk_list splits sequences...

  Session total: 1240 total · 780 reasoning
```

Chat history is preserved across turns for follow-up questions. Type `/exit` or `Ctrl+C` to quit.

## Controlling token usage

Set `llm.max_tokens` in `.okfconfig` to cap the maximum tokens per LLM call:

```json
{
  "llm": {
    "max_tokens": 1000
  }
}
```

Default is 2000. Lower values are cheaper and faster but may truncate responses.

## Requirements

- A configured LLM provider (see [Configuration](../getting-started/configuration.md))
- A generated bundle (`okf generate`)
- `openai` package installed (`pip install "okf-generator[llm]"`)

## How it's different from `okf lookup`

| | `okf lookup` | `okf ask` |
|---|---|---|
| Query type | Symbol name (exact/fuzzy) | Natural language question |
| LLM needed | No | Yes |
| Speed | Milliseconds | Seconds |
| Output | Structured concept card | Natural language answer |
| Token usage | — | Displayed per answer |
| Use case | "Find this function" | "How does this work?" |

## Privacy

`okf ask` only sends concept cards from the bundle to the LLM — no raw source code. The question is sent alongside the concept context. With a local LLM (Ollama, llama.cpp), nothing leaves your machine.
