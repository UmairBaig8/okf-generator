# Troubleshooting

## Common errors

### `ERROR: OKF bundle not found`

The lookup or diff command can't find the bundle at the expected path.

**Fix:** Pass `--bundle /path/to/okf_bundle` explicitly, or generate one first:

```bash
okf generate ./my_project ./okf_bundle
```

### `No concepts found`

The scanner didn't recognize any files in the source directory.

**Check:**
- Files have recognized extensions (`.py`, `.js`, `.ts`, `.go`, `.java`, `.rs`, etc.)
- Directory is not empty
- Files are not in a skipped directory (`node_modules`, `.venv`, `.git`, etc.)

### Tree-sitter parser crashes

Some language grammars may throw errors on unusual syntax:

```bash
Failed to parse src/weird.py: ...
```

**Fix:** This is usually non-fatal — the scanner creates a minimal Module concept for the file. If the file is important and should parse, check for syntax errors in the source.

### `okf generate` is slow

Large codebases with thousands of files can take a while.

**Tips:**
- Scope generation to a subdirectory: `okf generate ./src/app ./okf_bundle`
- The scanner is single-threaded for AST parsing (per-file)
- Manifest scanning (dependencies) is fast — most time is in file I/O

### LLM enrichment fails / API key errors

**Check:**
- Did you set `llm.api_key` in `.okfconfig` or `OKF_API_KEY` env?
- Is your endpoint reachable? Test with `curl http://localhost:8080/v1/chat/completions`
- Does the model name exist? Check your provider's model list
- Enrichment without a key skips gracefully with a warning — no crash

### `okf diff --impact` shows no dependencies

Dependencies only appear if the scanned codebase has manifest files (`requirements.txt`, `Cargo.toml`, etc.) AND the code imports from those packages. If your project uses only stdlib, there will be no dependency concepts.

## Getting help

- **GitHub Issues:** [github.com/UmairBaig8/okf-generator/issues](https://github.com/UmairBaig8/okf-generator/issues)
- **Discussions:** [github.com/UmairBaig8/okf-generator/discussions](https://github.com/UmairBaig8/okf-generator/discussions)
- **Quick check:** Run `okf generate` on `tests/fixtures/realworld` to verify your installation works end-to-end

## Known limitations

- Python parser uses stdlib `ast` — some syntax from Python 3.13+ may not be fully supported
- Dynamic languages (Ruby, JS) have best-effort call graph resolution
- Very large monorepos (>50K files) may need targeted subdirectory scoping
