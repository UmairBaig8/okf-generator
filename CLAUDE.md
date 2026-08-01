# OKF Generator

Generates OKF v0.2 knowledge bundles from codebases. 18 languages, 20 manifest formats, ~100× fewer tokens than raw source.

## Quick commands

```bash
pip install -e ".[dev]"       # editable install
pytest tests/ -q               # 415 tests
okf generate ./src ./bundle    # generate bundle
okf lookup <Name>              # look up concept
okf enrich --lsp               # LSP enrichment (needs pyright on $PATH)
```

## Architecture

```
okf/
├── enrich/          # Enricher contract → LspEnricher + LlmEnricher
│   ├── base.py      # Enricher ABC (start/run/stop), EnrichResult
│   ├── lsp.py       # LspEnricher — hand-rolled LSP client over stdio
│   ├── llm.py       # LlmEnricher — base/deep/security LLM modes
│   ├── _lsp_map.py  # LSP server registry (pyright, gopls, rust-analyzer, typescript)
│   └── _llm_prompts.py
├── cli.py            # 19 commands
├── generator.py      # Core scanner + bundle writer
├── linker.py          # Cross-reference pass (deps + call graph)
├── parsers/           # 18 language parsers
│   ├── base.py       # Concept dataclass + TreeSitterParser ABC
│   └── python.js go java rust ruby c cpp csharp dart kotlin php scala julia swift sql yaml
├── domains/           # Domain classification engine
├── lsp.py             # `okf lsp status|resolve|map` CLI
├── mcp_server.py      # MCP server (stdio/HTTP)
├── visualize.py       # HTML graph explorer (Cytoscape.js + tree-sitter WASM)
├── config.py          # Config from .okfconfig + env
└── pairs.py           # JSONL training pair generator
```

## Enricher contract

```python
class Enricher(ABC):
    def start(self, bundle_dir, concepts) -> bool    # prepare; return False to skip
    def run(self, bundle_dir, concepts) -> EnrichResult  # execute; never raise on partial failure
    def stop(self) -> None                             # always safe to call
```

LspEnricher and LlmEnricher both implement this. Wrapped in try/finally by `run_enrich()`.

## LSP enrichment

```
okf enrich --lsp                # LSP only
okf enrich --full               # LSP + LLM deep (shortcut)
okf enrich --lsp --llm          # LSP + LLM base
okf lsp status                  # table: which servers installed
okf lsp resolve file.py:42:5    # one-shot definition lookup
```

4 servers mapped: pyright (Python), gopls (Go), rust-analyzer (Rust), typescript-language-server (TS/JS).
Hand-rolled JSON-RPC client over stdio (~150 lines). 3s startup timeout per server.

## LLM enrichment

```
okf enrich --llm               # base mode (description/docstring, no source code sent)
okf enrich --llm --mode deep   # deep (reads source body)
okf enrich --llm --mode security
```

All 4 prompts in `_llm_prompts.py`. Shared `_SECURITY_FIELD_SPEC`. Body truncated at 120 lines.

## Linker

Runs after scan, before write. Two passes:
1. `link_dependencies()` — import statements → manifest dependency edges
2. `link_calls()` — function calls → caller/callee edges (conservative: same-file → same-domain → unique → ambiguous)

## Project files

- `AGENTS.md` — agent instructions
- `TEST.md` — integration test spec
- `RELEASE.md` — release checklist
- `FUTURE.md` — roadmap (SAST enrichment, MkDocs replacement, IDE plugins)
- `CHANGELOG.md` — versions
- `tests/` — 415 tests (pytest), 17-phase test.sh, realworld fixtures

## Config

`.okfconfig` or `~/.config/okf/config.json`. Sections: `llm`, `providers`, `enrich`, `serve`, `lookup`, `mcp`, `pairs`.

## Version

0.1.51 — MIT License — OKF v0.2 schema
