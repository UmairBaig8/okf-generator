"""Tests for okf.ignore — .gitignore/.okfignore/.okf-exclude parsing and matching."""

from pathlib import Path
import pytest


# ── Pattern matching ─────────────────────────────────────────────────────────

def test_load_no_files(tmp_path):
    from okf.ignore import load_patterns, matches
    pats = load_patterns(tmp_path)
    assert pats == []
    assert not matches("foo.py", pats)


def test_ignore_simple_pattern(tmp_path):
    from okf.ignore import load_patterns, matches
    (tmp_path / ".gitignore").write_text("*.log\n")
    pats = load_patterns(tmp_path)
    assert matches("debug.log", pats)
    assert not matches("main.py", pats)


def test_ignore_directory_pattern(tmp_path):
    from okf.ignore import load_patterns, matches
    (tmp_path / ".okfignore").write_text("build/\n")
    pats = load_patterns(tmp_path)
    assert matches("build", pats)
    assert matches("build/output.o", pats)
    assert not matches("src/main.c", pats)


def test_ignore_negation(tmp_path):
    from okf.ignore import load_patterns, matches
    (tmp_path / ".gitignore").write_text("*.log\n!important.log\n")
    pats = load_patterns(tmp_path)
    assert matches("debug.log", pats)
    assert not matches("important.log", pats)


def test_ignore_anchored_pattern(tmp_path):
    from okf.ignore import load_patterns, matches
    (tmp_path / ".gitignore").write_text("/build\n")
    pats = load_patterns(tmp_path)
    assert matches("build", pats)
    assert not matches("src/build", pats)


def test_ignore_comments_and_blanks(tmp_path):
    from okf.ignore import load_patterns, matches
    (tmp_path / ".gitignore").write_text("# comments\n\n*.pyc\n\n# blank lines above\n")
    pats = load_patterns(tmp_path)
    assert matches("test.pyc", pats)
    assert not matches("test.py", pats)


def test_ignore_recursive_star(tmp_path):
    from okf.ignore import load_patterns, matches
    (tmp_path / ".gitignore").write_text("a/**/b\n")
    pats = load_patterns(tmp_path)
    assert matches("a/b", pats)
    assert matches("a/x/b", pats)
    assert matches("a/x/y/b", pats)


def test_ignore_subdir_pattern(tmp_path):
    from okf.ignore import load_patterns, matches
    (tmp_path / ".okfignore").write_text("tests/\n")
    pats = load_patterns(tmp_path)
    assert matches("tests/test_foo.py", pats)
    assert matches("tests/sub/test_bar.py", pats)


def test_ignore_okf_exclude_file(tmp_path):
    from okf.ignore import load_patterns, matches
    (tmp_path / ".okf-exclude").write_text("legacy/\n*.bak\n")
    pats = load_patterns(tmp_path)
    assert matches("legacy/old.py", pats)
    assert matches("file.bak", pats)
    assert not matches("src/main.py", pats)


def test_ignore_multiple_files_union(tmp_path):
    from okf.ignore import load_patterns, matches
    (tmp_path / ".gitignore").write_text("*.log\n")
    (tmp_path / ".okfignore").write_text("*.tmp\n")
    pats = load_patterns(tmp_path)
    assert matches("trace.log", pats)
    assert matches("temp.tmp", pats)


def test_ignore_leading_dot_slash(tmp_path):
    from okf.ignore import load_patterns, matches
    (tmp_path / ".gitignore").write_text("./foo\n")
    pats = load_patterns(tmp_path)
    assert matches("foo", pats)
    assert not matches("foo/bar.py", pats)  # unanchored foo matches name segment only


def test_ignore_endswith_suffix(tmp_path):
    from okf.ignore import load_patterns, matches
    (tmp_path / ".okfignore").write_text("*.test\n")
    pats = load_patterns(tmp_path)
    assert matches("output.test", pats)
    assert matches("dir/output.test", pats)


# ── Integration: scan_codebase with .okfignore ───────────────────────────────

def test_scan_respects_okfignore(tmp_path):
    from okf.generator import scan_codebase
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("x = 1\n")
    (src / "debug.log").write_text("ERROR: test\n")
    (src / "legacy").mkdir()
    (src / "legacy" / "old.py").write_text("y = 2\n")
    (src / ".okfignore").write_text("*.log\nlegacy/\n")
    concepts = scan_codebase(src)
    names = {c.title for c in concepts}
    assert "main" in names
    assert "debug" not in names
    assert "old" not in names


def test_scan_respects_gitignore(tmp_path):
    from okf.generator import scan_codebase
    src = tmp_path / "src"
    src.mkdir()
    (src / "app.py").write_text("z = 3\n")
    (src / ".gitignore").write_text("*.pyc\n")
    (src / "cache.pyc").write_text("...")
    concepts = scan_codebase(src)
    names = {c.title for c in concepts}
    assert "app" in names
    assert "cache" not in names


def test_scan_negation_overrides_gitignore(tmp_path):
    from okf.generator import scan_codebase
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("a = 1\n")
    (src / "data.json").write_text("{}")
    (src / ".gitignore").write_text("*.json\n!data.json\n")
    concepts = scan_codebase(src)
    names = {c.title for c in concepts}
    assert "main" in names


# ── Git URL helpers in serve.py ──────────────────────────────────────────────

def test_is_git_url_https():
    from okf.serve import _is_git_url
    assert _is_git_url("https://github.com/user/repo.git")
    assert _is_git_url("https://github.com/user/repo.git@main")


def test_is_git_url_ssh():
    from okf.serve import _is_git_url
    assert _is_git_url("git@github.com:user/repo.git")


def test_is_git_url_bare():
    from okf.serve import _is_git_url
    assert _is_git_url("github.com/user/repo.git@main")


def test_is_not_git_url_local_path():
    from okf.serve import _is_git_url
    assert not _is_git_url("./okf_bundle")
    assert not _is_git_url("/absolute/path")
    assert not _is_git_url("okf_bundle")


def test_parse_git_url_with_ref():
    from okf.serve import _parse_git_url
    url, ref = _parse_git_url("https://github.com/user/repo.git@main")
    assert "github.com/user/repo.git" in url
    assert ref == "main"


def test_parse_git_url_default_ref():
    from okf.serve import _parse_git_url
    url, ref = _parse_git_url("https://github.com/user/repo.git")
    assert ref == "HEAD"


def test_parse_git_url_bare_domain():
    from okf.serve import _parse_git_url
    url, ref = _parse_git_url("github.com/user/repo@v1")
    assert url.startswith("https://")
    assert "user/repo.git" in url
    assert ref == "v1"


def test_cache_dir_deterministic():
    from okf.serve import _cache_dir
    d1 = _cache_dir("https://github.com/user/repo.git")
    d2 = _cache_dir("https://github.com/user/repo.git")
    assert d1 == d2
    assert "repos" in str(d1)


def test_has_bundle_marker_false(tmp_path):
    from okf.serve import _has_bundle_marker
    assert not _has_bundle_marker(tmp_path)


def test_has_bundle_marker_true(tmp_path):
    from okf.serve import _has_bundle_marker
    (tmp_path / "okf_bundle").mkdir(parents=True)
    (tmp_path / "okf_bundle" / "index.md").write_text("# test\n")
    assert _has_bundle_marker(tmp_path)


def test_resolve_bundle_existing(tmp_path):
    from okf.serve import _resolve_bundle
    (tmp_path / "okf_bundle").mkdir(parents=True)
    (tmp_path / "okf_bundle" / "index.md").write_text("# test\n")
    result = _resolve_bundle(tmp_path, generate=False)
    assert result == tmp_path / "okf_bundle"


def test_resolve_bundle_no_generate(tmp_path):
    from okf.serve import _resolve_bundle
    result = _resolve_bundle(tmp_path, generate=False)
    assert result is None


def test_resolve_bundle_generate_no_okf(tmp_path, monkeypatch):
    from okf.serve import _resolve_bundle
    import subprocess
    orig_run = subprocess.run

    def _mock_run(*args, **kwargs):
        raise FileNotFoundError("okf not found")

    monkeypatch.setattr(subprocess, "run", _mock_run)
    result = _resolve_bundle(tmp_path, generate=True)
    assert result is None


def test_resolve_bundle_generate_fails(tmp_path, monkeypatch):
    from okf.serve import _resolve_bundle
    import subprocess

    def _mock_run(*args, **kwargs):
        class Result:
            returncode = 1
            stdout = ""
            stderr = "error"
        return Result()

    monkeypatch.setattr(subprocess, "run", _mock_run)
    result = _resolve_bundle(tmp_path, generate=True)
    assert result is None


def test_resolve_bundle_generate_succeeds(tmp_path, monkeypatch):
    from okf.serve import _resolve_bundle
    import subprocess

    def _mock_run(*args, **kwargs):
        class Result:
            returncode = 0
            stdout = "done"
            stderr = ""
        return Result()

    monkeypatch.setattr(subprocess, "run", _mock_run)
    # Create the bundle dir as if generate did its work
    (tmp_path / "okf_bundle").mkdir(parents=True)
    (tmp_path / "okf_bundle" / "index.md").write_text("# test\n")
    result = _resolve_bundle(tmp_path, generate=True)
    assert result == tmp_path / "okf_bundle"
