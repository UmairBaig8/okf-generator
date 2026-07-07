# Release Process

## Prerequisites

- **All unit tests pass:** `pytest tests/ -q` (173+ green)
- **Canonical test suite passes:** `bash tests/test.sh` (generates `TEST_REPORT.html`, must have 0 failures)
- **Realworld fixture coverage:** `python -m pytest tests/test_realworld_fixtures.py -q` (43 tests)
- **CHANGELOG.md** has an up-to-date `[Unreleased]` section
- **Ruff lint passes:** `ruff check okf/ --select E,F,W --ignore E501`
- **`.gitignore` is up to date** — `_build/`, `dist/`, `*.egg-info` must be listed to prevent CI auto-commits from polluting the repo
- **New languages fully wired** — Every new `tree-sitter-*` dependency is listed in `pyproject.toml`; if it lacks Linux wheels, all CI workflows include a Rust setup step

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
> 5. **README freshness** — Scan `README.md`. Ensure new features are documented (CLI flags, manifest formats, language support, extraction fields, config, pre-commit, Docker, fuzzy search). Flag undocumented additions.
> 6. **Landing page freshness** — Scan `docs/index.html`. Every feature in the release must have a corresponding entry in the feature grid, hero section, or comparison table. If a new feature is prominent, add it.
> 7. **Realworld fixture coverage** — Run `pytest tests/test_realworld_fixtures.py -q`. Verify every extraction feature (generics, inheritance, decorators, visibility, fields) has >0 concepts in the realworld corpus.
> 8. **Dead code check** — Identify any unused imports, orphaned files, or stale test fixtures. Verify `tests/fixtures/sample_codebase/` is gone.
> 9. **Image rendering** — Verify all README images use absolute `raw.githubusercontent.com` URLs (not relative paths), so they render on PyPI.
> 10. **Dependency audit** — Run `pip list --outdated` and flag any major-version-skewed dependencies.
> 11. **New language checklist** — For each new language parser added since last release:
>     - `pyproject.toml` has the corresponding `tree-sitter-<lang>` dependency in `[project.dependencies]`
>     - If the package lacks pre-built Linux wheels, all CI workflows have a Rust toolchain step before `pip install`
>     - `tests/fixtures/realworld/<language>/` exists with `easy/` and `complex/` fixtures
>     - `tests/test_realworld_fixtures.py` has an entry in `LANGUAGE_DIRS` and a language-specific feature test
>     - `README.md` language table and `docs/languages-and-manifests.md` include the new language
> 12. **Build artifact check** — Verify `_build/`, `dist/`, and `*.egg-info` are in `.gitignore` so CI auto-commits don't pollute the repo.
> 13. **CI workflow dry-run** — For any new `.github/workflows/*.yml` files, verify triggers, permissions, and absence of hardcoded local paths that differ between dev machines and CI runners.
> 14. **Feature validation** — For every new feature listed in CHANGELOG, run a manual end-to-end test:
>     - **Fuzzy search**: `okf lookup --bundle /tmp/okf_bundle repo` returns `UserRepository`. `okf lookup --exact calc` exits 1.
>     - **Dockerfile parsing**: `tests/fixtures/complex/Dockerfile` is scanned and produces `ecosystem:docker` + `ecosystem:pip` deps.
>     - **Containerfile**: `Containerfile` is detected (`is_manifest_file` returns True).
>     - **LLM enrich**: `okf generate --enrich` logs no-crash warning when no API key.
>     - **Pre-commit**: `.pre-commit-config.yaml` contains `okf-generate` hook with `files:` filter matching all 12 languages.
>     - **Docker build**: `docker build -t okf-generator .` exits 0 (CI only — skip if no Docker).
>     - **Config**: `okf config` shows sectioned output. `okf config serve.port=9090` writes `.okfconfig`. Re-reading with `okf config` shows updated value.
>     - **Init wizard**: `okf init --quick` generates bundle + `.okfconfig` without prompting.
>     - **Live demo viz**: `okf visualize /tmp/okf_bundle /tmp/viz.html` succeeds and HTML contains `View Source` button and `"code"` fields.
> 15. **Produce report** — Concise summary of issues found, severity (blocker/minor/nit), and suggested fixes.

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

- **README**: New CLI flags? Update CLI Reference + Language table. New extraction features? Add to per-language table. New features like fuzzy search, Dockerfile parsing, config, pre-commit, `--enrich` must be called out in the feature sections and quickstart.
- **docs/index.html (landing page)**: If a prominent feature was added (new language, new manifest format, major UX improvement), add it to the hero section feature list, the feature grid, or the comparison table. The landing page must highlight every major capability. Also update: (a) language counts (search `N languages`), (b) CLI reference table (search `okf ` in table rows), (c) feature cards if adding new capabilities. Version badge auto-fetches from PyPI — no manual version update needed.
- **TEST.md**: If new CLI commands or flags were added, add corresponding test phases.
- **RELEASE.md**: If release process changed, update this file.
- **mkdocs docs-site**: If docs content changed, rebuild and commit the static site:
  ```bash
  mkdocs build
  rm -rf docs/docs-site && cp -r build/docs-site docs/docs-site
  rm -rf docs/docs-site/docs-site  # remove nested copy from site_url path
  git add docs/docs-site && git commit -m "docs: rebuild docs-site" && git push
  ```
  The docs-site is served at `https://umairbaig8.github.io/okf-generator/docs-site/`.

### 4. Update fixtures (if new languages/features)

If new languages or extraction features were added:
- Add fixture files to `tests/fixtures/realworld/<language>/easy/` and `complex/`
- Add test cases to `tests/test_realworld_fixtures.py`
- Verify with `pytest tests/test_realworld_fixtures.py`

### 5. Validate config system

- Run `okf config` — verify output is sectioned (`bundle_dir`, `llm.*`, `serve.*`, `lookup.*`, etc.)
- Run `okf config serve.port=9090` — verify `.okfconfig` is written
- Run `okf config` again — verify the change is reflected
- Run `okf init --quick` — verify `.okfconfig` + bundle are generated without prompts

### 6. Run final verification

```bash
bash tests/test.sh            # 0 failures
pytest tests/ -q              # 173+ passed
ruff check okf/ --select E,F,W --ignore E501  # clean
okf config                    # sectioned output, no errors
```

### 7. Update landing page live demo

If the viz template changed or new features affect the demo:
```bash
rm -rf _build && mkdir _build
okf generate tests/fixtures/realworld _build/okf_bundle
okf visualize _build/okf_bundle _build/viz.html
# Verify View Source button and code embedding
grep -c "View Source" _build/viz.html    # >= 1
grep -c '"code":"' _build/viz.html       # > 0
cp _build/viz.html docs/viz.html
```

### 8. Commit and tag

```bash
git add -A
git commit -m "chore: bump vx.y.z"
git tag vx.y.z
git push && git push --tags
```

### 9. CI handles the rest

The `publish.yml` workflow automatically:

| Step | What it does |
|------|-------------|
| Build | `python -m build` → wheel + sdist |
| Publish to PyPI | `pypa/gh-action-pypi-publish` |
| Smoke test | Installs published wheel, generates from realworld fixtures, runs lookup + pairs + summarize |
| Full test report | Runs `tests/test.sh`, attaches `TEST_REPORT.html` + `TEST_REPORT.md` to release |
| Docker image | `docker-publish.yml` builds and pushes `ghcr.io/umairbaig8/okf-generator/okf-generator` tagged with semver + `latest` |
| GitHub Release | Creates release from CHANGELOG section, includes test report artifacts |

### 10. Verify

```bash
# Wait for CI, then:
pip install okf-generator==x.y.z
okf --version

# Verify Docker image (if Docker is available)
docker pull ghcr.io/umairbaig8/okf-generator/okf-generator:latest
docker run ghcr.io/umairbaig8/okf-generator/okf-generator --version

# Download TEST_REPORT.html from the release and verify 0 failures
```

## Rollback

If a release is broken:
- **PyPI**: `pip install okf-generator==<previous-version>` (no yank unless security)
- **Git tag**: Delete remote tag: `git push --delete origin vx.y.z`
- **GitHub Release**: Delete via `gh release delete vx.y.z`
