# Release Process

## Prerequisites

- All unit tests pass: `pytest tests/ -q` (70+ green)
- Full integration spec passes: `TEST.md` (generate, lookup, pairs, summarize, edge cases)
- CHANGELOG.md has an up-to-date `[Unreleased]` section
- Ruff lint passes: `ruff check okf/ --select E,F,W --ignore E501`

For a quick confidence check before starting, run `TEST.md` — it exercises every CLI command against AgentBox (TS/JS monorepo) and edge cases.

## AI-Assisted Pre-Release Audit

Hand this prompt to any LLM-powered coding agent before cutting a release:

> **Act as an expert open-source maintainer. Audit this project for release readiness:**
>
> 1. **Code quality** — Run `ruff check okf/ --select E,F,W --ignore E501`. Report any errors.
> 2. **Test coverage** — Run `pytest tests/ -q`. Report count and any failures.
> 3. **Changelog completeness** — Read `CHANGELOG.md`. Compare `git log --oneline <last_tag>..HEAD` against the `[Unreleased]` section. Flag any missing entries.
> 4. **Version consistency** — Verify `okf/__init__.py` and `pyproject.toml` have the same version string.
> 5. **README freshness** — Scan `README.md`. Ensure new features are documented (CLI flags, manifest formats, language support). Flag undocumented additions.
> 6. **Dead code check** — Identify any unused imports, orphaned files, or stale test fixtures.
> 7. **Image rendering** — Verify all README images use absolute `raw.githubusercontent.com` URLs (not relative paths), so they render on PyPI.
> 8. **Dependency audit** — Run `pip list --outdated` and flag any major-version-skewed dependencies.
> 9. **Produce report** — Concise summary of issues found, severity (blocker/minor/nit), and suggested fixes.

## Steps

### 1. Bump version

```bash
# Edit both files to match
vim pyproject.toml          # version = "x.y.z"
vim okf/__init__.py         # __version__ = "x.y.z"
```

### 2. Update CHANGELOG

- Promote `[Unreleased]` → `[x.y.z] — YYYY-MM-DD`
- Review for accuracy: every commit should have a line
- Update comparison URL at the bottom:
  ```
  [Unreleased]: https://github.com/UmairBaig8/okf-generator/compare/vx.y.z...HEAD
  [x.y.z]: https://github.com/UmairBaig8/okf-generator/releases/tag/vx.y.z
  ```

### 3. Update README (if new features)

- New CLI flags? Add to CLI Reference section.
- New manifest/language support? Update Supported Languages table + Features list.

### 4. Commit and tag

```bash
git add -A
git commit -m "chore: bump vx.y.z"
git tag vx.y.z
git push && git push --tags
```

### 5. CI handles the rest

The `publish.yml` workflow automatically:

| Step | What it does |
|------|-------------|
| Build | `python -m build` → wheel + sdist |
| Publish to PyPI | `pypa/gh-action-pypi-publish` |
| Smoke test | Installs published wheel in fresh venv, runs `generate` + `lookup` + `pairs` + `summarize` |
| GitHub Release | Creates release from CHANGELOG section |

### 6. Verify

```bash
# Wait for CI, then:
pip install okf-generator==x.y.z
okf --version
```

## Rollback

If a release is broken:
- **PyPI**: `pip install okf-generator==<previous-version>` (no yank unless security)
- **Git tag**: Delete remote tag: `git push --delete origin vx.y.z`
- **GitHub Release**: Delete via `gh release delete vx.y.z`
