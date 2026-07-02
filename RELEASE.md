# Release Process

## Prerequisites

- **All unit tests pass:** `pytest tests/ -q` (173+ green)
- **Canonical test suite passes:** `bash tests/test.sh` (generates `TEST_REPORT.html`, must have 0 failures)
- **Realworld fixture coverage:** `python -m pytest tests/test_realworld_fixtures.py -q` (43 tests)
- **CHANGELOG.md** has an up-to-date `[Unreleased]` section
- **Ruff lint passes:** `ruff check okf/ --select E,F,W --ignore E501`

For a quick confidence check:

```bash
bash tests/test.sh        # 17 phases, CLI + unit + edge cases
pytest tests/ -q          # 173+ unit tests
```

## AI-Assisted Pre-Release Audit

Hand this prompt to any LLM-powered coding agent before cutting a release:

> **Act as an expert open-source maintainer. Audit this project for release readiness:**
>
> 1. **Code quality** — Run `ruff check okf/ --select E,F,W --ignore E501`. Report any errors.
> 2. **Test coverage** — Run `pytest tests/ -q`. Report count and any failures.
> 3. **Changelog completeness** — Read `CHANGELOG.md`. Compare `git log --oneline <last_tag>..HEAD` against the `[Unreleased]` section. Flag any missing entries.
> 4. **Version consistency** — Verify `okf/__init__.py` and `pyproject.toml` have the same version string.
> 5. **README freshness** — Scan `README.md`. Ensure new features are documented (CLI flags, manifest formats, language support, extraction fields). Flag undocumented additions.
> 6. **Realworld fixture coverage** — Run `pytest tests/test_realworld_fixtures.py -q`. Verify every extraction feature (generics, inheritance, decorators, visibility, fields) has >0 concepts in the realworld corpus.
> 7. **Dead code check** — Identify any unused imports, orphaned files, or stale test fixtures. Verify `tests/fixtures/sample_codebase/` is gone.
> 8. **Image rendering** — Verify all README images use absolute `raw.githubusercontent.com` URLs (not relative paths), so they render on PyPI.
> 9. **Dependency audit** — Run `pip list --outdated` and flag any major-version-skewed dependencies.
> 10. **Produce report** — Concise summary of issues found, severity (blocker/minor/nit), and suggested fixes.

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

### 3. Update documentation

- **README**: New CLI flags? Update CLI Reference + Language table. New extraction features? Add to per-language table.
- **TEST.md**: If new CLI commands were added, add corresponding test phases.
- **RELEASE.md**: If release process changed, update this file.

### 4. Update fixtures (if new languages/features)

If new languages or extraction features were added:
- Add fixture files to `tests/fixtures/realworld/<language>/easy/` and `complex/`
- Add test cases to `tests/test_realworld_fixtures.py`
- Verify with `pytest tests/test_realworld_fixtures.py`

### 5. Run final verification

```bash
bash tests/test.sh            # 0 failures
pytest tests/ -q              # 173+ passed
ruff check okf/ --select E,F,W --ignore E501  # clean
```

### 6. Commit and tag

```bash
git add -A
git commit -m "chore: bump vx.y.z"
git tag vx.y.z
git push && git push --tags
```

### 7. CI handles the rest

The `publish.yml` workflow automatically:

| Step | What it does |
|------|-------------|
| Build | `python -m build` → wheel + sdist |
| Publish to PyPI | `pypa/gh-action-pypi-publish` |
| Smoke test | Installs published wheel, generates from realworld fixtures, runs lookup + pairs + summarize |
| Full test report | Runs `tests/test.sh`, attaches `TEST_REPORT.html` + `TEST_REPORT.md` to release |
| GitHub Release | Creates release from CHANGELOG section, includes test report artifacts |

### 8. Verify

```bash
# Wait for CI, then:
pip install okf-generator==x.y.z
okf --version
# Download TEST_REPORT.html from the release and verify 0 failures
```

## Rollback

If a release is broken:
- **PyPI**: `pip install okf-generator==<previous-version>` (no yank unless security)
- **Git tag**: Delete remote tag: `git push --delete origin vx.y.z`
- **GitHub Release**: Delete via `gh release delete vx.y.z`
