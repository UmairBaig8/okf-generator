# Troubleshooting

Common issues and fixes, grouped by command. If your issue isn't listed, [open an issue on GitHub](https://github.com/UmairBaig8/okf-generator/issues) with your OS, Python version, and the full error output.

## Installation

### `pip install okf-generator` fails with a build error

Usually a missing tree-sitter grammar wheel for your platform.

```bash
pip install --upgrade pip
pip install okf-generator --no-cache-dir
```

If it still fails, install without LLM extras first to isolate the problem:

```bash
pip install okf-generator  # core only, no [llm] extra
```

### `okf: command not found` after install

Your install location isn't on `PATH`. Check where pip put it:

```bash
python -m okf --version   # confirms the package is importable
python -m site --user-base  # shows the base dir to add to PATH
```

Add `<user-base>/bin` (Linux/macOS) or `<user-base>\Scripts` (Windows) to `PATH`, or reinstall inside a virtualenv and activate it.

## `okf generate`

### Scan finds 0 concepts / empty bundle

Most common causes, in order of likelihood:

- You pointed it at the wrong directory — `okf generate` expects a source root, not a single file.
- All your files are in an excluded path. Check `SKIP_DIRS` isn't matching your source tree (e.g. a folder literally named `test` or `build` gets skipped by default).
- Your language isn't supported yet — check [Language Coverage](user-guide/languages.md).

Run with verbose output to see what was scanned:

```bash
okf generate ./src ./bundle --verbose
```

### `migrations/` or SQL files are being skipped

Known gotcha: some default exclude lists treat `migrations/` as a build artifact directory. If your SQL lives there and isn't showing up in the bundle, confirm your okf-generator version includes the fix (v0.1.15+), or explicitly include it:

```bash
okf generate ./src ./bundle --include migrations
```

### Generation is slow on a large monorepo

- Scope to a subdirectory instead of the whole repo: `okf generate ./services/api ./bundle`.
- Delete `.okf_lookup_cache.json` if it's stale and causing repeated re-parses — it's mtime-invalidated automatically, but a corrupted cache file can force full rescans. Safe to delete anytime; it regenerates.

### Tree-sitter node type errors (`Unknown node type: X`)

This means the installed tree-sitter grammar version doesn't match what the parser expects. Grammar APIs shift between versions. Fix:

```bash
pip install --upgrade okf-generator
```

If it persists after upgrading, [open an issue](https://github.com/UmairBaig8/okf-generator/issues) with the exact node type and language — this is a parser bug on our end, not something to work around locally.

## `okf lookup`

### Lookup returns nothing for a symbol you know exists

- Confirm the bundle was regenerated after the symbol was added — `okf lookup` reads from the bundle, not live source.
- Lookup is exact-match by design (not fuzzy/semantic). Check the exact casing and whether it's `ClassName.method_name` vs just `method_name`.
- Delete and regenerate the lookup cache if it seems stale: `rm .okf_lookup_cache.json`.

### `--json` output is empty but non-JSON mode works

Usually means the match found a concept with missing required fields (malformed manual edit to a bundle file). Validate the frontmatter against the [Bundle Format Reference](user-guide/bundle-format.md).

## `okf enrich`

### Enrichment doesn't add anything / silently no-ops

Enrichment is resumable and skips already-enriched concepts. If you want to re-run it:

```bash
okf enrich ./bundle --mode deep --force
```

### `deep` or `security` mode fails with "source body not found"

These tiers need access to original source, not just the bundle. Pass `--src`:

```bash
okf enrich ./bundle --mode deep --src ./my_project
```

### API key errors during enrichment

Enrichment tiers other than `base` structural cleanup may call an LLM provider. Confirm your key is set:

```bash
export ANTHROPIC_API_KEY=sk-...   # or your configured provider's env var
```

See [Configuration](getting-started/configuration.md) for the full list of supported provider env vars.

## `okf visualize` / `okf dashboard`

### Blank page when opening the generated HTML

- Open via `okf serve` instead of double-clicking the file — some browsers block local `file://` JS execution for security reasons.
- Confirm the bundle path passed to `visualize` actually contains `.md` files, not an empty directory.

### Dashboard won't start / port already in use

```bash
okf dashboard ./bundle --port 8081   # pick a free port
```

## CI/CD

### GitHub Action fails on `okf generate` but works locally

- Check the runner's Python version matches what you test locally — pin it explicitly in your workflow.
- Large repos may hit the runner's default timeout — increase `timeout-minutes` on the job.

### PR comment from the Action isn't posting

Confirm the workflow has `pull-requests: write` permission set:

```yaml
permissions:
  pull-requests: write
```

## Still stuck?

- Check [existing GitHub issues](https://github.com/UmairBaig8/okf-generator/issues) — many edge cases are already tracked.
- Open a new issue with: OS, Python version, `okf --version` output, the exact command run, and full error text.