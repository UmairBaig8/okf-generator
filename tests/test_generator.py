"""Tests for okf.generator — scan, write, summary."""

import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures" / "sample_codebase"


@pytest.fixture
def bundle_dir(tmp_path):
    """Generate a fresh OKF bundle into a temp dir."""
    from okf.generator import scan_codebase, write_bundle, write_summary, _dedup_concept_ids
    concepts = scan_codebase(FIXTURES)
    concepts = _dedup_concept_ids(concepts)
    write_bundle(
        concepts=concepts,
        output_dir=tmp_path,
        bundle_name="sample",
        log_entries=["test run"],
    )
    write_summary("sample", concepts, tmp_path, {})
    return tmp_path, concepts


# ── scan_codebase ────────────────────────────────────────────────────────────

def test_scan_finds_concepts():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    assert len(concepts) > 0


def test_scan_finds_python_functions():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    funcs = [c for c in concepts if c.type == "Function"]
    names = [c.title for c in funcs]
    assert "add" in names
    assert "greet" in names


def test_scan_finds_python_classes():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    classes = [c for c in concepts if c.type == "Class"]
    names = [c.title for c in classes]
    assert "Calculator" in names
    assert "WorldBankConnector" in names


def test_scan_extracts_docstrings():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    calc = next((c for c in concepts if c.title == "Calculator"), None)
    assert calc is not None
    assert "calculator" in calc.description.lower() or "calculator" in calc.docstring.lower()


def test_scan_extracts_signatures():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    add_fn = next((c for c in concepts if c.title == "add" and c.type == "Function"), None)
    assert add_fn is not None
    assert "def add" in add_fn.signature
    assert "int" in add_fn.signature


def test_scan_extracts_params():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    add_fn = next((c for c in concepts if c.title == "add" and c.type == "Function"), None)
    assert add_fn is not None
    param_names = [p["name"] for p in add_fn.params]
    assert "a" in param_names
    assert "b" in param_names


def test_scan_extracts_return_type():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    add_fn = next((c for c in concepts if c.title == "add" and c.type == "Function"), None)
    assert add_fn is not None
    assert add_fn.returns == "int"


def test_scan_concept_ids_are_path_based():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    for c in concepts:
        # concept_id must not use old flat layout
        assert not c.concept_id.startswith("functions/"), f"Old layout: {c.concept_id}"
        assert not c.concept_id.startswith("classes/"),   f"Old layout: {c.concept_id}"
        assert not c.concept_id.startswith("modules/"),   f"Old layout: {c.concept_id}"


def test_scan_tags_are_standardised():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    for c in concepts:
        tag_str = " ".join(c.tags)
        assert "lang:" in tag_str, f"Missing lang: tag on {c.title}: {c.tags}"
        assert "type:" in tag_str, f"Missing type: tag on {c.title}: {c.tags}"


# ── write_bundle ─────────────────────────────────────────────────────────────

def test_bundle_creates_index(bundle_dir):
    tmp, _ = bundle_dir
    assert (tmp / "index.md").exists()


def test_bundle_creates_summary(bundle_dir):
    tmp, _ = bundle_dir
    assert (tmp / "SUMMARY.md").exists()


def test_bundle_creates_log(bundle_dir):
    tmp, _ = bundle_dir
    assert (tmp / "log.md").exists()


def test_bundle_layout_mirrors_source(bundle_dir):
    tmp, _ = bundle_dir
    # concept files should live under a path mirroring the source
    md_files = list(tmp.rglob("*.md"))
    non_index = [f for f in md_files if f.name not in {"index.md", "log.md", "SUMMARY.md"}]
    assert len(non_index) > 0


def test_bundle_concept_files_have_frontmatter(bundle_dir):
    tmp, _ = bundle_dir
    import yaml
    md_files = list(tmp.rglob("*.md"))
    non_index = [f for f in md_files if f.name not in {"index.md", "log.md", "SUMMARY.md"}]
    for f in non_index[:5]:   # check first 5
        text = f.read_text()
        assert text.startswith("---"), f"{f} missing frontmatter"
        parts = text.split("---", 2)
        fm = yaml.safe_load(parts[1])
        assert fm.get("type"), f"{f} missing type in frontmatter"
        assert fm.get("title"), f"{f} missing title in frontmatter"


def test_bundle_summary_has_domain_map(bundle_dir):
    tmp, _ = bundle_dir
    summary = (tmp / "SUMMARY.md").read_text()
    assert "## Domain Map" in summary
    assert "## Stats" in summary


# ── SUMMARY.md standalone ────────────────────────────────────────────────────

def test_write_summary_standalone(tmp_path):
    from okf.generator import scan_codebase, write_summary, _dedup_concept_ids
    concepts = scan_codebase(FIXTURES)
    concepts = _dedup_concept_ids(concepts)
    out = write_summary("sample", concepts, tmp_path, {})
    assert out.exists()
    content = out.read_text()
    assert "sample" in content
    assert "## Stats" in content


# ── SQL parser ──────────────────────────────────────────────────────────────

def test_sql_parser_extracts_table_view_function_index():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    sql_concepts = [c for c in concepts if "lang:sql" in c.tags]
    titles_by_type = {c.type: c.title for c in sql_concepts}
    assert titles_by_type.get("Table") == "users"
    assert titles_by_type.get("View") == "active_users"
    assert titles_by_type.get("Function") == "days_since_signup"
    assert titles_by_type.get("Index") == "idx_users_email"


def test_sql_parser_captures_preceding_comment_as_description():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    users_table = next(c for c in concepts if c.type == "Table" and c.title == "users")
    assert "registered users" in users_table.description.lower()


def test_sql_files_get_module_concept():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    modules = [c for c in concepts if c.type == "Module" and "lang:sql" in c.tags]
    assert len(modules) == 1
    assert modules[0].title == "0001_init"


# ── Empty folder handling ────────────────────────────────────────────────────

def test_scan_empty_directory_returns_no_concepts_without_crashing(tmp_path):
    from okf.generator import scan_codebase
    empty_dir = tmp_path / "empty_project"
    empty_dir.mkdir()
    concepts = scan_codebase(empty_dir)
    assert concepts == []


def test_scan_nonexistent_directory_returns_empty_list(tmp_path):
    from okf.generator import scan_codebase
    concepts = scan_codebase(tmp_path / "does_not_exist")
    assert concepts == []


def test_write_bundle_on_empty_codebase_still_creates_valid_bundle(tmp_path):
    from okf.generator import scan_codebase, write_bundle, write_summary, _walk_source_dirs
    source = tmp_path / "src"
    source.mkdir()
    out = tmp_path / "bundle"
    concepts = scan_codebase(source)
    write_bundle(
        concepts=concepts,
        output_dir=out,
        bundle_name="empty",
        log_entries=["empty run"],
        source_dirs=_walk_source_dirs(source),
    )
    write_summary("empty", concepts, out, {})
    assert (out / "index.md").exists()
    assert (out / "log.md").exists()
    assert (out / "SUMMARY.md").exists()


def test_write_bundle_includes_empty_subfolders(tmp_path):
    """A subfolder with no parseable concepts (e.g. only .txt files, or
    genuinely empty) should still get an index.md and show up in its
    parent's subdirectory listing instead of vanishing from the bundle."""
    from okf.generator import scan_codebase, write_bundle, _walk_source_dirs
    source = tmp_path / "src"
    (source / "with_code").mkdir(parents=True)
    (source / "with_code" / "main.py").write_text("def foo():\n    pass\n")
    (source / "truly_empty").mkdir(parents=True)
    (source / "only_docs").mkdir(parents=True)
    (source / "only_docs" / "notes.txt").write_text("just notes, no code")

    out = tmp_path / "bundle"
    concepts = scan_codebase(source)
    write_bundle(
        concepts=concepts,
        output_dir=out,
        bundle_name="src",
        log_entries=["test"],
        source_dirs=_walk_source_dirs(source),
    )

    root_index = (out / "index.md").read_text()
    assert "truly_empty" in root_index
    assert "only_docs" in root_index
    assert "with_code" in root_index
    assert (out / "truly_empty" / "index.md").exists()
    assert (out / "only_docs" / "index.md").exists()
