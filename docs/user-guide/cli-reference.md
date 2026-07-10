# CLI Reference

## Global

```bash
okf --help              Show available commands
okf <command> --help    Show options for a specific command
okf --version           Show version and exit
```

---

## `okf generate`

```bash
okf generate <source_dir> [output_dir] [--exclude <dir> ...]
```

Scans a source directory and produces an OKF v0.2 knowledge bundle.

| Option | Description |
|--------|-------------|
| `--summarize <bundle_dir>` | Regenerate SUMMARY.md only (no re-scan) |
| `--exclude <dir>` | Skip directories matching this name (repeatable) |

**Environment variables (LLM enrichment):**

| Variable | Default | Description |
|----------|---------|-------------|
| `OKF_ENRICH=1` | — | Enable LLM enrichment |
| `OKF_BASE_URL` | `https://api.anthropic.com/v1` | OpenAI-compat endpoint |
| `OKF_API_KEY` | — | API key |
| `OKF_MODEL` | `claude-sonnet-4-6` | Model name |
| `OKF_MAX_WORKERS` | `2` | Parallel workers |

---

## `okf lookup`

```bash
okf lookup [query] [options]
```

Search for concepts in a bundle.

| Option | Description |
|--------|-------------|
| `--bundle PATH` | Bundle directory (default: `./okf_bundle`) |
| `--file PATH` | Filter by source file |
| `--type TYPE` | Filter by concept type: `Function`, `Class`, `Module`, `Dependency` |
| `--tag TAG` | Filter by tag, repeatable (e.g. `--tag lang:python`) |
| `--limit N` | Max results (default: 10) |
| `--compact` | One-line output per result |
| `--json` | JSON output for programmatic use |
| `--full` | Raw `.md` file content |
| `--min-score N` | Minimum relevance score 0–1 (default: 0.1) |
| `--no-cache` | Bypass and skip writing the lookup cache |

---

## `okf diff`

```bash
okf diff <old_bundle> <new_bundle>
```

Compare two bundles — shows added, removed, and changed concepts.
Changes are detected via content hash (description, signature, tags).

| Option | Description |
|--------|-------------|
| `--compact` | One-line output per concept |
| `--json` | JSON output |

---

## `okf pairs`

```bash
okf pairs <bundle_dir> [output_file]
```

Convert bundle to JSONL training pairs.

**Environment variables:**

| Variable | Description |
|----------|-------------|
| `SKIP_SYNTH=1` | Static pairs only (no LLM) |
| `SYNTH_BASE_URL` | API endpoint |
| `SYNTH_API_KEY` | API key |
| `SYNTH_MODEL` | Model name |
| `MAX_WORKERS` | Parallel workers (default: 3) |
| `QA_PER_CONCEPT` | Q&A pairs per concept (default: 3) |
| `PAIR_TYPES` | Comma-separated: `codegen`, `qa`, `doc`, `summarize`, `crosslink` |

---

## `okf summarize`

```bash
okf summarize <bundle_dir>
```

Regenerate SUMMARY.md from an existing bundle (no re-scan).

---

## `okf agent`

```bash
okf agent [--bundle <path>] [--resume <session_id>]
```

Interactive REPL over an OKF bundle with persistent sessions and slash commands.

| Command | Description |
|---------|-------------|
| `/lookup <name>` | Full concept detail card |
| `/source <name>` | Show source code lines |
| `/calls [name]` | Show what this calls |
| `/called-by [name]` | Show what calls this |
| `/related [name]` | Show relationships |
| `/save` | Save session to disk |
| `/export [json\|md]` | Export session |
| `/sessions` | List saved sessions |
| `/resume <id>` | Resume a previous session |
| `/history` | Show conversation history |
| `/clear` | Clear context |

Sessions stored in `~/.okf/sessions/`. Requires LLM configured in `.okfconfig` for Q&A.

---

## `okf migrate`

```bash
okf migrate v0.1-to-v0.2 <bundle_dir> [--dry-run]
```

Convert OKF v0.1 bundles to v0.2 format in-place. Adds `okf_version`, `concept_id`, `language` to frontmatter and merges relationship sections. Use `--dry-run` to preview changes.

---

## `okf install`

```bash
okf install [agent] [agent ...]
```

Install integration for AI coding agents.

| Agent | What it does |
|-------|-------------|
| `claude` | Copies SKILL.md to Claude Code skills directory |
| `opencode` | Creates `.opencode/commands/lookup.md` |
| `copilot` | Creates `.github/copilot-instructions.md` |
| `cursor` | Creates `.cursorrules` |
| `windsurf` | Creates `.windsurfrules` |
| `cline` | Creates `.clinerules` |
| `all` | Runs all of the above |

---

## `okf visualize`

```bash
okf visualize <bundle_dir> [output.html]
```

Generate an interactive HTML explorer for an OKF bundle. Features:
- **Knowledge graph** — Cytoscape.js force-directed layout, color-coded by type
- **Concept detail panel** — signature, docstring, params, relationships, source code snippet
- **Source code viewer** — relevant lines from source file, Prism.js syntax highlighting
- **Parse tree viewer** — tree-sitter WASM-powered AST browser (Python, JS, TS, Go, Java, Ruby, Rust, C, C++, PHP)
- **Ego graph** — local neighborhood around any concept
- **Global graph** — full network overview with vis.js
- **Glass UI** — frosted glass cards, breathing gradient, theme toggle

Output is a self-contained HTML file (no server, no install).

---

## `okf serve`

```bash
okf serve [bundle_dir] [options]
```

Launch a local HTTP server for browsing an OKF bundle.

| Option | Description |
|--------|-------------|
| `--port, -p PORT` | Port (default: 8000) |
| `--open, -o` | Open browser automatically |
| `--quiet, -q` | Suppress request logs |
| `--host HOST` | Host (default: 127.0.0.1) |
