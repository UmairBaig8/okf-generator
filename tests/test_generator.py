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
    assert (out / "truly_empty" / "index.md").exists()
    assert (out / "only_docs" / "index.md").exists()


# ── Comprehensive fixture: all languages + all manifests ────────────────────

COMPLEX = Path(__file__).parent / "fixtures" / "complex"


def test_complex_all_languages_detected():
    """Every supported language produces concepts."""
    from okf.generator import scan_codebase
    concepts = scan_codebase(COMPLEX)
    tags = set()
    for c in concepts:
        for t in c.tags:
            if t.startswith("lang:"):
                tags.add(t[5:])
    expected = {"python", "javascript", "typescript", "go", "java", "rust", "ruby", "c", "cpp", "csharp", "sql", "manifest"}
    assert expected.issubset(tags), f"Missing langs: {expected - tags}"


def test_complex_all_concept_types_present():
    """Every concept type (including Dependency) is produced."""
    from okf.generator import scan_codebase
    concepts = scan_codebase(COMPLEX)
    types = {c.type for c in concepts}
    for t in ("Function", "Class", "Module", "Dependency", "Table", "View"):
        assert t in types, f"Missing type: {t}"


def test_complex_dependency_count():
    """At least 40 dependencies across all manifest types."""
    from okf.generator import scan_codebase
    concepts = scan_codebase(COMPLEX)
    deps = [c for c in concepts if c.type == "Dependency"]
    assert len(deps) >= 40, f"Only {len(deps)} dependencies"


def test_complex_all_manifest_ecosystems():
    """Every manifest parser produces concepts with correct ecosystem tag."""
    from okf.generator import scan_codebase
    concepts = scan_codebase(COMPLEX)
    ecosystems = set()
    for c in concepts:
        for t in c.tags:
            if t.startswith("ecosystem:"):
                ecosystems.add(t[10:])
    expected = {"pip", "npm", "cargo", "go", "composer", "maven", "rubygems", "gradle", "swiftpm", "clojars", "hex"}
    assert expected.issubset(ecosystems), f"Missing ecosystems: {expected - ecosystems}"


def test_complex_bundle_has_dependencies_folder(tmp_path):
    """Generated bundle contains _dependencies/ with per-ecosystem subdirs."""
    from okf.generator import scan_codebase, write_bundle, _walk_source_dirs
    concepts = scan_codebase(COMPLEX)
    write_bundle(
        concepts=concepts,
        output_dir=tmp_path,
        bundle_name="complex",
        log_entries=["test"],
        source_dirs=_walk_source_dirs(COMPLEX),
    )
    dep_root = tmp_path / "_dependencies"
    assert dep_root.is_dir(), "_dependencies/ missing"
    assert (dep_root / "index.md").exists(), "_dependencies/index.md missing"
    # spot-check a few ecosystems
    for eco in ("pip", "npm", "cargo", "go", "maven"):
        assert (dep_root / eco).is_dir(), f"_dependencies/{eco}/ missing"
        assert (dep_root / eco / "index.md").exists(), f"_dependencies/{eco}/index.md missing"


def test_complex_summary_has_dependencies_section(tmp_path):
    """SUMMARY.md includes a Dependencies table with ecosystem counts."""
    from okf.generator import scan_codebase, write_bundle, write_summary
    concepts = scan_codebase(COMPLEX)
    write_bundle(concepts=concepts, output_dir=tmp_path, bundle_name="complex", log_entries=["test"])
    write_summary("complex", concepts, tmp_path, {})
    summary = (tmp_path / "SUMMARY.md").read_text()
    assert "## Dependencies" in summary, "Missing Dependencies section"
    assert "| Ecosystem | Packages |" in summary, "Missing ecosystem count table"
    assert "| pip |" in summary, "pip count missing"


def test_complex_summary_domain_map_no_manifest_domains(tmp_path):
    """Domain map should not list manifest files as domains."""
    from okf.generator import scan_codebase, write_bundle, write_summary
    concepts = scan_codebase(COMPLEX)
    write_bundle(concepts=concepts, output_dir=tmp_path, bundle_name="complex", log_entries=["test"])
    write_summary("complex", concepts, tmp_path, {})
    summary = (tmp_path / "SUMMARY.md").read_text()
    for bad in ("pyproject.toml", "requirements.txt", "package.json"):
        assert bad not in summary, f"Domain map should not contain {bad}"


def test_complex_deep_directory_structure(tmp_path):
    """Deeply nested source dirs are mirrored in the bundle."""
    from okf.generator import scan_codebase, write_bundle, _walk_source_dirs
    concepts = scan_codebase(COMPLEX)
    write_bundle(
        concepts=concepts,
        output_dir=tmp_path,
        bundle_name="complex",
        log_entries=["test"],
        source_dirs=_walk_source_dirs(COMPLEX),
    )
    assert (tmp_path / "src" / "sub" / "dir" / "index.md").exists(), "Deep dir index.md missing"
    index_content = (tmp_path / "src" / "sub" / "dir" / "index.md").read_text()
    assert "deep.md" in index_content, "Deep module concept missing from index"


def test_complex_python_concepts_have_signatures():
    """Python Function and Class concepts include signatures."""
    from okf.generator import scan_codebase
    concepts = scan_codebase(COMPLEX)
    py_fns = [c for c in concepts if c.type == "Function" and "lang:python" in c.tags]
    assert len(py_fns) >= 2, f"Expected >=2 Python functions, got {len(py_fns)}"
    for fn in py_fns:
        assert fn.signature, f"Python function {fn.title} missing signature"
        assert fn.params is not None, f"Python function {fn.title} missing params"


def test_complex_rust_concepts_have_doc_comments():
    """Rust parser extracts /// doc comments as docstrings."""
    from okf.generator import scan_codebase
    concepts = scan_codebase(COMPLEX)
    rust_fns = [c for c in concepts if c.type == "Function" and "lang:rust" in c.tags]
    add_fn = next((c for c in rust_fns if c.title == "add"), None)
    assert add_fn is not None, "Rust add() function not found"
    assert add_fn.docstring, "Rust add() missing docstring"
    assert "adds" in add_fn.docstring.lower(), "Rust docstring content mismatch"


def test_complex_sql_creates_table_view_function():
    """SQL parser extracts tables, views, and functions from .sql files."""
    from okf.generator import scan_codebase
    concepts = scan_codebase(COMPLEX)
    sql_tags = {c.type: c.title for c in concepts if "lang:sql" in c.tags}
    assert sql_tags.get("Table") == "users"
    assert sql_tags.get("View") == "active_users"
    assert sql_tags.get("Function") == "days_since_signup"


def test_complex_dependency_concept_body(tmp_path):
    """Dependency concepts have body_extra rendered as a table."""
    from okf.generator import scan_codebase, write_bundle
    concepts = scan_codebase(COMPLEX)
    write_bundle(concepts=concepts, output_dir=tmp_path, bundle_name="complex", log_entries=["test"])
    dep_file = tmp_path / "_dependencies" / "npm" / "express.md"
    assert dep_file.exists(), "express.md not found in _dependencies/npm/"
    content = dep_file.read_text()
    assert "Ecosystem" in content
    assert "Version constraint" in content
    assert "Source manifest" in content
    assert "Dev dependency" in content
    assert "npm" in content
    assert "^4.19.0" in content


def test_complex_dependency_dev_flag():
    """Dev dependencies are marked correctly across parsers."""
    from okf.manifest_scanner import parse_package_json, parse_pyproject_toml, parse_cargo_toml, parse_gemfile, parse_build_gradle, parse_go_mod
    from pathlib import Path
    import tempfile

    def _write(name, content):
        p = Path(tempfile.mktemp(suffix=name))
        p.write_text(content.strip())
        return p

    # npm devDeps
    p1 = _write("package.json", '{"devDependencies":{"vitest":"^1.0"}}')
    assert parse_package_json(p1)[0]["dev"] is True

    # pip optional-dependencies
    p2 = _write("pyproject.toml", '[project]\noptional-dependencies={dev=["pytest"]}')
    assert parse_pyproject_toml(p2)[0]["dev"] is True

    # cargo dev-dependencies
    p3 = _write("Cargo.toml", '[package]\nname="x"\n[dev-dependencies]\ncriterion="0.5"')
    assert parse_cargo_toml(p3)[0]["dev"] is True

    # go indirect
    p4 = _write("go.mod", 'module x\ngo 1.22\nrequire github.com/foo/bar v1.0.0 // indirect')
    assert parse_go_mod(p4)[0]["dev"] is True

    # Gemfile group :test
    p5 = _write("Gemfile", 'gem "x"\ngroup :test do\ngem "y", "1.0"\nend')
    deps = parse_gemfile(p5)
    assert deps[0]["dev"] is False
    assert deps[1]["dev"] is True

    # gradle testImplementation
    p6 = _write("build.gradle", 'deps { testImplementation "a:b:1.0" }')
    assert parse_build_gradle(p6)[0]["dev"] is True

    p1.unlink(); p2.unlink(); p3.unlink(); p4.unlink(); p5.unlink(); p6.unlink()


# ── New language parsers: C, C++, C# ─────────────────────────────────────────

def test_c_parser_extracts_functions_and_structs():
    """C parser creates Function and Class concepts."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.c").write_text("/** Adds two ints. */\nint add(int a, int b) { return a + b; }\n\n/** A 2D point. */\nstruct Point { int x; int y; };\n")
    concepts = scan_codebase(tmp)
    funcs = {c.title for c in concepts if c.type == "Function"}
    classes = {c.title for c in concepts if c.type == "Class"}
    assert "add" in funcs, f"C function 'add' not found in {funcs}"
    assert "Point" in classes, f"C struct 'Point' not found in {classes}"
    add_fn = next(c for c in concepts if c.title == "add")
    assert add_fn.docstring, "C add() missing docstring"
    assert "Adds two ints" in add_fn.docstring
    import shutil; shutil.rmtree(tmp)


def test_cpp_parser_extracts_classes_and_methods():
    """C++ parser creates Class concepts with methods."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.cpp").write_text("/** A simple counter. */\nclass Counter {\npublic:\n    int get() const { return val; }\n    void inc() { val++; }\nprivate:\n    int val = 0;\n};\n\nint add(int a, int b) { return a + b; }\n")
    concepts = scan_codebase(tmp)
    classes = {c.title for c in concepts if c.type == "Class"}
    funcs = {c.title for c in concepts if c.type == "Function"}
    assert "Counter" in classes
    assert "add" in funcs
    counter = next(c for c in concepts if c.title == "Counter")
    assert "get" in counter.methods, f"Counter should have method 'get', got {counter.methods}"
    import shutil; shutil.rmtree(tmp)


def test_csharp_parser_extracts_classes_and_methods():
    """C# parser creates Class and Function concepts."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.cs").write_text("using System;\nclass Greeter {\n    public void SayHello(string name) { }\n    public int Add(int a, int b) { return a + b; }\n}\n")
    concepts = scan_codebase(tmp)
    classes = {c.title for c in concepts if c.type == "Class"}
    funcs = {c.title for c in concepts if c.type == "Function"}
    assert "Greeter" in classes
    assert "SayHello" in funcs
    assert "Add" in funcs
    import shutil; shutil.rmtree(tmp)
