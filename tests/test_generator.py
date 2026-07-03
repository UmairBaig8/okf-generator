"""Tests for okf.generator — scan, write, summary."""

import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures" / "realworld" / "python" / "easy"
REALWORLD_SQL = Path(__file__).parent / "fixtures" / "realworld" / "sql" / "easy"


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
    assert "slugify" in names
    assert "chunk_list" in names


def test_scan_finds_python_classes():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    classes = [c for c in concepts if c.type == "Class"]
    names = [c.title for c in classes]
    assert "User" in names


def test_scan_extracts_docstrings():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    slug = next((c for c in concepts if c.title == "slugify"), None)
    assert slug is not None
    assert slug.description and len(slug.description) > 10


def test_scan_extracts_signatures():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    slug = next((c for c in concepts if c.title == "slugify" and c.type == "Function"), None)
    assert slug is not None
    assert "def slugify" in slug.signature


def test_scan_extracts_params():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    slug = next((c for c in concepts if c.title == "slugify" and c.type == "Function"), None)
    assert slug is not None
    param_names = [p["name"] for p in slug.params]
    assert "text" in param_names
    assert "max_length" in param_names


def test_scan_extracts_return_type():
    from okf.generator import scan_codebase
    concepts = scan_codebase(FIXTURES)
    slug = next((c for c in concepts if c.title == "slugify" and c.type == "Function"), None)
    assert slug is not None
    assert slug.returns == "str"


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
    concepts = scan_codebase(REALWORLD_SQL)
    sql_concepts = [c for c in concepts if "lang:sql" in c.tags]
    titles_by_type = {c.type: c.title for c in sql_concepts}
    assert "Table" in titles_by_type
    assert "View" in titles_by_type
    assert titles_by_type.get("Index")


def test_sql_parser_captures_preceding_comment_as_description():
    from okf.generator import scan_codebase
    concepts = scan_codebase(REALWORLD_SQL)
    users_table = next(c for c in concepts if c.type == "Table" and c.title == "categories")
    assert users_table.description and len(users_table.description) > 0


def test_sql_files_get_module_concept():
    from okf.generator import scan_codebase
    concepts = scan_codebase(REALWORLD_SQL)
    modules = [c for c in concepts if c.type == "Module" and "lang:sql" in c.tags]
    assert len(modules) == 1
    assert modules[0].title == "schema"


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
    expected = {"python", "javascript", "typescript", "go", "java", "rust", "ruby", "c", "cpp", "csharp", "sql", "swift", "kotlin", "manifest"}
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
    expected = {"pip", "npm", "cargo", "go", "composer", "maven", "rubygems", "gradle", "swiftpm", "clojars", "hex", "docker"}
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


def test_swift_parser_extracts_classes_methods_and_functions():
    """Swift parser creates Class and Function concepts."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.swift").write_text(
        "import Foundation\n"
        "/** A simple greeter. */\n"
        "public class Greeter {\n"
        "    private let greeting: String\n"
        "    public init(greeting: String) { self.greeting = greeting }\n"
        "    public func greet(name: String) -> String { return \"\\(greeting), \\(name)!\" }\n"
        "}\n"
        "/** Adds two integers. */\n"
        "public func add(a: Int, b: Int) -> Int { a + b }\n"
    )
    concepts = scan_codebase(tmp)
    classes = {c.title for c in concepts if c.type == "Class"}
    funcs = {c.title for c in concepts if c.type == "Function"}
    assert "Greeter" in classes, f"Swift class 'Greeter' not found in {classes}"
    assert "greet" in funcs, f"Swift method 'greet' not found in {funcs}"
    assert "add" in funcs, f"Swift function 'add' not found in {funcs}"
    import shutil; shutil.rmtree(tmp)


def test_kotlin_parser_extracts_classes_methods_and_functions():
    """Kotlin parser creates Class and Function concepts."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.kt").write_text(
        "package com.okfgen.test\n"
        "/** A simple greeter. */\n"
        "class Greeter(private val greeting: String) {\n"
        "    fun greet(name: String): String = \"$greeting, $name!\"\n"
        "}\n"
        "/** Adds two integers. */\n"
        "fun add(a: Int, b: Int): Int = a + b\n"
    )
    concepts = scan_codebase(tmp)
    classes = {c.title for c in concepts if c.type == "Class"}
    funcs = {c.title for c in concepts if c.type == "Function"}
    assert "Greeter" in classes, f"Kotlin class 'Greeter' not found in {classes}"
    assert "greet" in funcs, f"Kotlin method 'greet' not found in {funcs}"
    assert "add" in funcs, f"Kotlin function 'add' not found in {funcs}"
    import shutil; shutil.rmtree(tmp)


# ── Generics / type parameters extraction (Tier 1) ──────────────────────────

def test_typescript_generic_class_and_function():
    """TypeScript generic classes and functions extract type_params."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "lib.ts").write_text(
        "export class Box<T> {\n"
        "  value: T;\n"
        "  constructor(v: T) { this.value = v; }\n"
        "  get(): T { return this.value; }\n"
        "}\n"
        "export function first<T>(items: T[]): T | undefined {\n"
        "  return items[0];\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    box = next((c for c in concepts if c.title == "Box"), None)
    assert box is not None, "Box class not found"
    assert box.type_params == ["T"], f"Box type_params should be ['T'], got {box.type_params}"
    fn = next((c for c in concepts if c.title == "first"), None)
    assert fn is not None, "first() not found"
    assert fn.type_params == ["T"], f"first type_params should be ['T'], got {fn.type_params}"
    import shutil; shutil.rmtree(tmp)


def test_java_generic_class_and_method():
    """Java generic classes and methods extract type_params."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "DataStore.java").write_text(
        "public class DataStore<T, U extends Comparable> {\n"
        "    public void put(T key, U value) { }\n"
        "    public <V> V transform(T key, Class<V> type) { return null; }\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    ds = next((c for c in concepts if c.type == "Class" and c.title == "DataStore"), None)
    assert ds is not None, "DataStore class not found"
    assert "T" in ds.type_params, f"DataStore type_params should contain 'T', got {ds.type_params}"
    assert any("U extends" in tp for tp in ds.type_params), \
        f"DataStore should have 'U extends Comparable', got {ds.type_params}"
    transform = next((c for c in concepts if c.type == "Function" and c.title == "transform"), None)
    assert transform is not None, "transform() not found"
    assert transform.type_params == ["V"], f"transform type_params should be ['V'], got {transform.type_params}"
    import shutil; shutil.rmtree(tmp)


def test_rust_generic_struct_and_fn():
    """Rust generic structs and functions extract type_params."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "lib.rs").write_text(
        "pub struct Pair<T, U> {\n"
        "    pub first: T,\n"
        "    pub second: U,\n"
        "}\n"
        "impl<T, U> Pair<T, U> {\n"
        "    pub fn new(first: T, second: U) -> Self { Pair { first, second } }\n"
        "}\n"
        "pub fn id<T>(x: T) -> T { x }\n"
    )
    concepts = scan_codebase(tmp)
    pair = next((c for c in concepts if c.type == "Class" and c.title == "Pair"), None)
    assert pair is not None, "Pair struct not found"
    assert len(pair.type_params) == 2, f"Pair should have 2 type params, got {pair.type_params}"
    assert "T" in pair.type_params, f"Pair type_params should contain 'T', got {pair.type_params}"
    fn_id = next((c for c in concepts if c.type == "Function" and c.title == "id"), None)
    assert fn_id is not None, "id() not found"
    assert fn_id.type_params == ["T"], f"id type_params should be ['T'], got {fn_id.type_params}"
    new_fn = next((c for c in concepts if c.type == "Function" and c.title == "new"), None)
    assert new_fn is not None, "Pair::new() not found"
    assert len(new_fn.type_params) == 2, f"new() should have 2 type params, got {new_fn.type_params}"
    import shutil; shutil.rmtree(tmp)


def test_go_generic_func_and_type():
    """Go generic functions and types extract type_params (Go 1.18+)."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "lib.go").write_text(
        "package lib\n"
        "\n"
        "func Map[T any, R any](items []T, fn func(T) R) []R {\n"
        "    result := make([]R, len(items))\n"
        "    for i, item := range items {\n"
        "        result[i] = fn(item)\n"
        "    }\n"
        "    return result\n"
        "}\n"
        "\n"
        "type Stack[T any] struct {\n"
        "    items []T\n"
        "}\n"
        "\n"
        "func (s *Stack[T]) Push(item T) {}\n"
    )
    concepts = scan_codebase(tmp)
    map_fn = next((c for c in concepts if c.type == "Function" and c.title == "Map"), None)
    assert map_fn is not None, "Map function not found"
    assert len(map_fn.type_params) >= 2, f"Map should have >=2 type params, got {map_fn.type_params}"
    stack = next((c for c in concepts if c.type == "Class" and c.title == "Stack"), None)
    assert stack is not None, "Stack type not found"
    assert any("T" in tp for tp in stack.type_params), f"Stack type_params should contain 'T', got {stack.type_params}"
    import shutil; shutil.rmtree(tmp)


def test_cpp_template_class_and_function():
    """C++ template classes and functions extract type_params."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.cpp").write_text(
        "template<typename T>\n"
        "class Container {\n"
        "public:\n"
        "    void add(T val) {}\n"
        "    T get() { return T(); }\n"
        "};\n"
        "\n"
        "template<typename T, typename U>\n"
        "T convert(U val) { return T(); }\n"
    )
    concepts = scan_codebase(tmp)
    container = next((c for c in concepts if c.title == "Container"), None)
    assert container is not None, "Container class not found"
    assert container.type_params, f"Container type_params should not be empty"
    assert any("T" in tp for tp in container.type_params), \
        f"Container should have 'T' param, got {container.type_params}"
    convert_fn = next((c for c in concepts if c.title == "convert"), None)
    assert convert_fn is not None, "convert() not found"
    assert len(convert_fn.type_params) >= 2, \
        f"convert should have >=2 type params, got {convert_fn.type_params}"
    import shutil; shutil.rmtree(tmp)


def test_csharp_generic_class_and_method():
    """C# generic classes and methods extract type_params."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.cs").write_text(
        "using System.Collections.Generic;\n"
        "class Repository<T> {\n"
        "    public T GetById(int id) { return default(T); }\n"
        "    public List<T> GetAll() { return new List<T>(); }\n"
        "    public K Transform<T, K>(T input) { return default(K); }\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    repo = next((c for c in concepts if c.type == "Class" and c.title == "Repository"), None)
    assert repo is not None, "Repository class not found"
    assert repo.type_params == ["T"], f"Repository type_params should be ['T'], got {repo.type_params}"
    transform = next((c for c in concepts if c.type == "Function" and c.title == "Transform"), None)
    assert transform is not None, "Transform method not found"
    assert len(transform.type_params) >= 2, \
        f"Transform should have >=2 type params, got {transform.type_params}"
    import shutil; shutil.rmtree(tmp)


def test_complex_fixture_has_generic_concepts():
    """The complex fixture's TypeScript generic code extracts type_params."""
    from okf.generator import scan_codebase
    from .test_generator import COMPLEX
    concepts = scan_codebase(COMPLEX)
    ts_generic = [c for c in concepts if c.type_params and "lang:typescript" in c.tags]
    assert len(ts_generic) >= 2, f"Expected >=2 generic TS concepts, got {len(ts_generic)}"
    titles = {c.title for c in ts_generic}
    assert "DataService" in titles, f"DataService not in generic concepts: {titles}"
    assert "wrapResponse" in titles, f"wrapResponse not in generic concepts: {titles}"
    ds = next(c for c in ts_generic if c.title == "DataService")
    assert ds.type_params == ["T"], f"DataService type_params should be ['T'], got {ds.type_params}"


# ── Inheritance chain extraction (Tier 1) ────────────────────────────────

def test_python_class_inheritance():
    """Python class extracts base classes."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "models.py").write_text(
        "class Animal:\n    pass\n"
        "class Dog(Animal):\n    pass\n"
        "class Pet:\n    pass\n"
        "class Golden(Dog, Pet):\n    pass\n"
    )
    concepts = scan_codebase(tmp)
    dog = next((c for c in concepts if c.type == "Class" and c.title == "Dog"), None)
    assert dog is not None
    assert "Animal" in dog.inheritance, f"Dog should inherit Animal, got {dog.inheritance}"
    golden = next((c for c in concepts if c.type == "Class" and c.title == "Golden"), None)
    assert golden is not None
    assert len(golden.inheritance) >= 2, f"Golden should have >=2 bases, got {golden.inheritance}"
    import shutil; shutil.rmtree(tmp)


def test_java_class_inheritance():
    """Java class extracts superclass and interfaces."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "Test.java").write_text(
        "interface Pet {}\n"
        "class Animal {}\n"
        "class Dog extends Animal implements Pet {}\n"
    )
    concepts = scan_codebase(tmp)
    dog = next((c for c in concepts if c.type == "Class" and c.title == "Dog"), None)
    assert dog is not None, "Dog class not found"
    assert "Animal" in dog.inheritance, f"Dog should inherit Animal, got {dog.inheritance}"
    assert "Pet" in dog.inheritance, f"Dog should implement Pet, got {dog.inheritance}"
    import shutil; shutil.rmtree(tmp)


def test_typescript_class_heritage():
    """TypeScript class extracts extends/implements bases."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "lib.ts").write_text(
        "interface Animal {}\n"
        "interface Pet {}\n"
        "class Dog extends Animal implements Pet {}\n"
    )
    concepts = scan_codebase(tmp)
    dog = next((c for c in concepts if c.type == "Class" and c.title == "Dog"), None)
    assert dog is not None, "Dog class not found"
    assert "Animal" in dog.inheritance, f"Dog should extend Animal, got {dog.inheritance}"
    assert "Pet" in dog.inheritance, f"Dog should implement Pet, got {dog.inheritance}"
    import shutil; shutil.rmtree(tmp)


def test_cpp_class_inheritance():
    """C++ class extracts base classes."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.cpp").write_text(
        "class Animal {};\n"
        "class Dog : public Animal {};\n"
    )
    concepts = scan_codebase(tmp)
    dog = next((c for c in concepts if c.type == "Class" and c.title == "Dog"), None)
    assert dog is not None, "Dog class not found"
    assert "Animal" in dog.inheritance, f"Dog should inherit Animal, got {dog.inheritance}"
    import shutil; shutil.rmtree(tmp)


def test_csharp_class_inheritance():
    """C# class extracts base types from base_list."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.cs").write_text(
        "interface Animal {}\n"
        "interface Pet {}\n"
        "class Dog : Animal, Pet {}\n"
    )
    concepts = scan_codebase(tmp)
    dog = next((c for c in concepts if c.type == "Class" and c.title == "Dog"), None)
    assert dog is not None, "Dog class not found"
    assert "Animal" in dog.inheritance, f"Dog should inherit Animal, got {dog.inheritance}"
    assert "Pet" in dog.inheritance, f"Dog should inherit Pet, got {dog.inheritance}"
    import shutil; shutil.rmtree(tmp)


def test_ruby_class_inheritance():
    """Ruby class extracts superclass."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.rb").write_text(
        "class Animal\nend\n"
        "class Dog < Animal\nend\n"
    )
    concepts = scan_codebase(tmp)
    dog = next((c for c in concepts if c.type == "Class" and c.title == "Dog"), None)
    assert dog is not None, "Dog class not found"
    assert "Animal" in dog.inheritance, f"Dog should inherit Animal, got {dog.inheritance}"
    import shutil; shutil.rmtree(tmp)


# ── Decorators / Attributes extraction (Tier 1) ──────────────────────────

def test_python_function_decorators():
    """Python functions extract decorator list."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "app.py").write_text(
        "import functools\n"
        "@functools.cache\n"
        "def get_data(): return 42\n"
        "\n"
        "@app.route('/api', methods=['GET'])\n"
        "def handle(): pass\n"
    )
    concepts = scan_codebase(tmp)
    get_data = next((c for c in concepts if c.type == "Function" and c.title == "get_data"), None)
    assert get_data is not None
    assert get_data.decorators, f"get_data should have decorators, got {get_data.decorators}"
    assert any("cache" in d for d in get_data.decorators), f"cache decorator missing: {get_data.decorators}"
    import shutil; shutil.rmtree(tmp)


def test_python_class_decorators():
    """Python classes extract decorator list."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "models.py").write_text(
        "from dataclasses import dataclass\n"
        "@dataclass\n"
        "class User:\n    name: str\n"
    )
    concepts = scan_codebase(tmp)
    user = next((c for c in concepts if c.type == "Class" and c.title == "User"), None)
    assert user is not None
    assert user.decorators, f"User should have decorators, got {user.decorators}"
    assert any("dataclass" in d for d in user.decorators), f"dataclass missing: {user.decorators}"
    import shutil; shutil.rmtree(tmp)


def test_java_annotations():
    """Java classes and methods extract annotations."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "Test.java").write_text(
        "@Deprecated\n"
        "class LegacyService {\n"
        "    @SuppressWarnings(\"unchecked\")\n"
        "    public void run() {}\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    svc = next((c for c in concepts if c.type == "Class" and c.title == "LegacyService"), None)
    assert svc is not None
    assert svc.decorators, f"LegacyService should have annotations, got {svc.decorators}"
    assert any("Deprecated" in d for d in svc.decorators), f"@Deprecated missing: {svc.decorators}"
    run = next((c for c in concepts if c.type == "Function" and c.title == "run"), None)
    assert run is not None
    assert any("SuppressWarnings" in d for d in run.decorators), f"@SuppressWarnings missing: {run.decorators}"
    import shutil; shutil.rmtree(tmp)


def test_csharp_attributes():
    """C# classes and methods extract attributes."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.cs").write_text(
        "[Serializable]\n"
        "class Config {\n"
        "    [Obsolete(\"use v2\")]\n"
        "    public string OldPath { get; set; }\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    cfg = next((c for c in concepts if c.type == "Class" and c.title == "Config"), None)
    assert cfg is not None
    assert cfg.decorators, f"Config should have attributes, got {cfg.decorators}"
    assert any("Serializable" in d for d in cfg.decorators), f"[Serializable] missing: {cfg.decorators}"
    import shutil; shutil.rmtree(tmp)


def test_rust_attributes():
    """Rust structs and functions extract #[attribute] items."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "lib.rs").write_text(
        "#[derive(Debug, Clone)]\n"
        "struct Config {\n    name: String,\n}\n"
        "\n"
        "#[tokio::main]\n"
        "async fn run() {}\n"
    )
    concepts = scan_codebase(tmp)
    cfg = next((c for c in concepts if c.type == "Class" and c.title == "Config"), None)
    assert cfg is not None
    assert cfg.decorators, f"Config should have attributes, got {cfg.decorators}"
    assert any("derive" in d for d in cfg.decorators), f"#[derive] missing: {cfg.decorators}"
    fn_run = next((c for c in concepts if c.type == "Function" and c.title == "run"), None)
    assert fn_run is not None
    assert any("tokio" in d for d in fn_run.decorators), f"#[tokio::main] missing: {fn_run.decorators}"
    import shutil; shutil.rmtree(tmp)


# ── Visibility modifiers (Tier 2) ────────────────────────────────────────

def test_java_visibility():
    """Java classes and methods capture visibility modifiers."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "Test.java").write_text(
        "public class Service {\n"
        "    public void start() {}\n"
        "    private void stop() {}\n"
        "    protected static int count() { return 0; }\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    svc = next((c for c in concepts if c.type == "Class" and c.title == "Service"), None)
    assert svc is not None
    assert "public" in svc.visibility, f"Service missing public: {svc.visibility}"
    start = next((c for c in concepts if c.type == "Function" and c.title == "start"), None)
    assert start is not None
    assert "public" in start.visibility, f"start missing public: {start.visibility}"
    count = next((c for c in concepts if c.type == "Function" and c.title == "count"), None)
    assert count is not None
    assert "static" in count.visibility, f"count missing static: {count.visibility}"
    assert "protected" in count.visibility, f"count missing protected: {count.visibility}"
    import shutil; shutil.rmtree(tmp)


def test_csharp_visibility():
    """C# classes and methods capture visibility modifiers."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.cs").write_text(
        "public class Service {\n"
        "    public void Start() {}\n"
        "    private static int Count() { return 0; }\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    svc = next((c for c in concepts if c.type == "Class" and c.title == "Service"), None)
    assert svc is not None
    assert "public" in svc.visibility, f"Service missing public: {svc.visibility}"
    count = next((c for c in concepts if c.type == "Function" and c.title == "Count"), None)
    assert count is not None
    assert "private" in count.visibility, f"Count missing private: {count.visibility}"
    assert "static" in count.visibility, f"Count missing static: {count.visibility}"
    import shutil; shutil.rmtree(tmp)


def test_typescript_visibility():
    """TypeScript methods capture accessibility modifiers."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "service.ts").write_text(
        "class Service {\n"
        "    public start(): void {}\n"
        "    private stop(): void {}\n"
        "    protected static count(): number { return 0; }\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    start = next((c for c in concepts if c.type == "Function" and c.title == "start"), None)
    assert start is not None
    assert "public" in start.visibility, f"start missing public: {start.visibility}"
    count = next((c for c in concepts if c.type == "Function" and c.title == "count"), None)
    assert count is not None
    assert "static" in count.visibility, f"count missing static: {count.visibility}"
    assert "protected" in count.visibility, f"count missing protected: {count.visibility}"
    import shutil; shutil.rmtree(tmp)


def test_rust_visibility():
    """Rust functions and structs capture visibility modifiers."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "lib.rs").write_text(
        "pub struct Service {}\n"
        "pub fn run() {}\n"
        "fn internal() {}\n"
    )
    concepts = scan_codebase(tmp)
    svc = next((c for c in concepts if c.type == "Class" and c.title == "Service"), None)
    assert svc is not None
    assert svc.visibility, f"Service should have visibility: {svc.visibility}"
    assert any("pub" in v for v in svc.visibility), f"Service missing pub: {svc.visibility}"
    internal = next((c for c in concepts if c.type == "Function" and c.title == "internal"), None)
    assert internal is not None
    assert not internal.visibility, f"internal should have no visibility: {internal.visibility}"
    import shutil; shutil.rmtree(tmp)


def test_cpp_visibility_modifiers():
    """C++ functions capture static/virtual/const modifiers."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.cpp").write_text(
        "static int run() { return 0; }\n"
        "virtual void stop() {}\n"
        "int normal() { return 1; }\n"
    )
    concepts = scan_codebase(tmp)
    run = next((c for c in concepts if c.type == "Function" and c.title == "run"), None)
    assert run is not None
    assert "static" in run.visibility, f"run missing static: {run.visibility}"
    normal = next((c for c in concepts if c.type == "Function" and c.title == "normal"), None)
    assert normal is not None
    assert not normal.visibility, f"normal should have no visibility: {normal.visibility}"
    import shutil; shutil.rmtree(tmp)


# ── Class fields / properties (Tier 2) ───────────────────────────────────

def test_python_class_fields():
    """Python classes extract annotated fields."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "models.py").write_text(
        "from dataclasses import dataclass\n"
        "@dataclass\n"
        "class User:\n"
        "    name: str\n"
        "    age: int = 0\n"
    )
    concepts = scan_codebase(tmp)
    user = next((c for c in concepts if c.type == "Class" and c.title == "User"), None)
    assert user is not None
    field_names = {f["name"] for f in user.fields}
    assert "name" in field_names, f"field 'name' missing: {user.fields}"
    assert "age" in field_names, f"field 'age' missing: {user.fields}"
    import shutil; shutil.rmtree(tmp)


def test_typescript_class_fields():
    """TypeScript classes extract field definitions."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "models.ts").write_text(
        "class User {\n"
        "    name: string;\n"
        "    age: number = 0;\n"
        "    private email: string;\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    user = next((c for c in concepts if c.type == "Class" and c.title == "User"), None)
    assert user is not None
    field_names = {f["name"] for f in user.fields}
    assert "name" in field_names, f"field 'name' missing: {user.fields}"
    assert "email" in field_names, f"field 'email' missing: {user.fields}"
    email_field = next(f for f in user.fields if f["name"] == "email")
    assert email_field.get("visibility") == "private", f"email visibility: {email_field}"
    import shutil; shutil.rmtree(tmp)


def test_java_class_fields():
    """Java classes extract field declarations."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "User.java").write_text(
        "class User {\n"
        "    private String name;\n"
        "    public int age;\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    user = next((c for c in concepts if c.type == "Class" and c.title == "User"), None)
    assert user is not None
    field_names = {f["name"] for f in user.fields}
    assert "name" in field_names, f"field 'name' missing: {user.fields}"
    assert "age" in field_names, f"field 'age' missing: {user.fields}"
    import shutil; shutil.rmtree(tmp)


def test_csharp_class_fields():
    """C# classes extract field and property declarations."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "User.cs").write_text(
        "class User {\n"
        "    private string name;\n"
        "    public int Age { get; set; }\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    user = next((c for c in concepts if c.type == "Class" and c.title == "User"), None)
    assert user is not None
    field_names = {f["name"] for f in user.fields}
    assert "name" in field_names, f"field 'name' missing: {user.fields}"
    assert "Age" in field_names, f"property 'Age' missing: {user.fields}"
    import shutil; shutil.rmtree(tmp)


# ── TypeScript completeness: interfaces, type aliases, enums (Tier 2) ────

def test_typescript_interface():
    """TypeScript interface declarations are extracted."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "types.ts").write_text(
        "interface User {\n"
        "    name: string;\n"
        "    age: number;\n"
        "}\n"
        "interface Admin extends User {\n"
        "    role: string;\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    user = next((c for c in concepts if c.type == "Interface" and c.title == "User"), None)
    assert user is not None, f"Interface 'User' not found"
    assert "name" in user.methods, f"Interface User should list 'name': {user.methods}"
    admin = next((c for c in concepts if c.type == "Interface" and c.title == "Admin"), None)
    assert admin is not None
    assert "User" in admin.inheritance, f"Admin should extend User: {admin.inheritance}"
    import shutil; shutil.rmtree(tmp)


def test_typescript_type_alias():
    """TypeScript type alias declarations are extracted."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "types.ts").write_text(
        "type UserID = string;\n"
        "type Callback<T> = (data: T) => void;\n"
    )
    concepts = scan_codebase(tmp)
    uid = next((c for c in concepts if c.type == "Type" and c.title == "UserID"), None)
    assert uid is not None, f"Type alias 'UserID' not found"
    cb = next((c for c in concepts if c.type == "Type" and c.title == "Callback"), None)
    assert cb is not None, f"Type alias 'Callback' not found"
    import shutil; shutil.rmtree(tmp)


def test_typescript_enum():
    """TypeScript enum declarations are extracted."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "types.ts").write_text(
        "enum Color {\n"
        "    Red,\n"
        "    Green,\n"
        "    Blue\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    color = next((c for c in concepts if c.type == "Class" and c.title == "Color"), None)
    assert color is not None, f"Enum 'Color' not found"
    assert "Red" in color.methods, f"Enum Color should list Red: {color.methods}"
    assert "Green" in color.methods, f"Enum Color should list Green: {color.methods}"
    import shutil; shutil.rmtree(tmp)


# ── SQL column/constraint extraction (Tier 2) ────────────────────────────

def test_sql_table_columns():
    """SQL CREATE TABLE extracts column definitions with types and constraints."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "schema.sql").write_text(
        "CREATE TABLE users (\n"
        "    id INTEGER PRIMARY KEY,\n"
        "    name TEXT NOT NULL,\n"
        "    email TEXT UNIQUE,\n"
        "    age INTEGER DEFAULT 0\n"
        ");\n"
    )
    concepts = scan_codebase(tmp)
    users = next((c for c in concepts if c.type == "Table" and c.title == "users"), None)
    assert users is not None, "Table 'users' not found"
    assert users.fields, f"Table users should have fields: {users.fields}"
    col_names = {f["name"] for f in users.fields}
    assert "id" in col_names, f"Column 'id' missing: {col_names}"
    assert "name" in col_names, f"Column 'name' missing: {col_names}"
    id_col = next(f for f in users.fields if f["name"] == "id")
    assert "PRIMARY KEY" in id_col.get("visibility", ""), f"id should have PRIMARY KEY: {id_col}"
    name_col = next(f for f in users.fields if f["name"] == "name")
    assert "NOT" in name_col.get("visibility", ""), f"name should have NOT NULL: {name_col}"
    import shutil; shutil.rmtree(tmp)


def test_sql_table_foreign_key():
    """SQL CREATE TABLE extracts foreign key references."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "schema.sql").write_text(
        "CREATE TABLE orders (\n"
        "    id INTEGER PRIMARY KEY,\n"
        "    user_id INTEGER REFERENCES users(id)\n"
        ");\n"
    )
    concepts = scan_codebase(tmp)
    orders = next((c for c in concepts if c.type == "Table" and c.title == "orders"), None)
    assert orders is not None, "Table 'orders' not found"
    user_id_col = next((f for f in orders.fields if f["name"] == "user_id"), None)
    assert user_id_col is not None, f"Column 'user_id' missing: {orders.fields}"
    assert "REFERENCES" in user_id_col.get("visibility", ""), f"FK ref missing: {user_id_col}"
    import shutil; shutil.rmtree(tmp)


# ── Method emission as individual concepts (Tier 1) ──────────────────────

def test_python_methods_emitted():
    """Python class methods are emitted as individual Function concepts."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "service.py").write_text(
        "class Service:\n"
        "    def start(self): pass\n"
        "    async def stop(self): pass\n"
    )
    concepts = scan_codebase(tmp)
    methods = {c.title for c in concepts if c.type == "Function"}
    assert "start" in methods, f"method 'start' not emitted: {methods}"
    assert "stop" in methods, f"method 'stop' not emitted: {methods}"
    import shutil; shutil.rmtree(tmp)


def test_typescript_methods_emitted():
    """TypeScript class methods are emitted as individual Function concepts."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "service.ts").write_text(
        "class Service {\n"
        "    start(): void {}\n"
        "    stop(): void {}\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    methods = {c.title for c in concepts if c.type == "Function"}
    assert "start" in methods, f"method 'start' not emitted: {methods}"
    assert "stop" in methods, f"method 'stop' not emitted: {methods}"
    import shutil; shutil.rmtree(tmp)


def test_cpp_methods_emitted():
    """C++ class methods are emitted as individual Function concepts."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.cpp").write_text(
        "class Counter {\n"
        "public:\n"
        "    int get() const { return val; }\n"
        "    void inc() { val++; }\n"
        "private:\n"
        "    int val = 0;\n"
        "};\n"
    )
    concepts = scan_codebase(tmp)
    methods = {c.title for c in concepts if c.type == "Function"}
    assert "get" in methods, f"method 'get' not emitted: {methods}"
    assert "inc" in methods, f"method 'inc' not emitted: {methods}"
    import shutil; shutil.rmtree(tmp)


def test_ruby_methods_emitted():
    """Ruby class methods are emitted as individual Function concepts."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.rb").write_text(
        "class Service\n"
        "  def start\n"
        "  end\n"
        "  def stop\n"
        "  end\n"
        "end\n"
    )
    concepts = scan_codebase(tmp)
    methods = {c.title for c in concepts if c.type == "Function"}
    assert "start" in methods, f"method 'start' not emitted: {methods}"
    assert "stop" in methods, f"method 'stop' not emitted: {methods}"
    import shutil; shutil.rmtree(tmp)


# ── Structured doc tag parsing: Javadoc @param / @return (Tier 3) ────────

def test_java_doc_tags_populate_params_and_returns():
    """Javadoc @param and @return tags populate structured params/returns."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "Test.java").write_text(
        "public class Test {\n"
        "    /**\n"
        "     * Greets a user.\n"
        "     * @param name the person to greet\n"
        "     * @return a greeting string\n"
        "     */\n"
        "    public String greet(String name) { return \"Hi \" + name; }\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    greet = next((c for c in concepts if c.type == "Function" and c.title == "greet"), None)
    assert greet is not None, "greet() not found"
    assert len(greet.params) >= 1, f"greet should have params from @param, got {greet.params}"
    assert greet.params[0]["name"] == "name", f"param should be 'name', got {greet.params}"
    import shutil; shutil.rmtree(tmp)


def test_jsdoc_params_with_types_populate_annotations():
    """JSDoc @param {Type} tag populates param annotation."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "lib.js").write_text(
        "/**\n"
        " * Format a value.\n"
        " * @param {number} val - the value to format\n"
        " * @returns {string} formatted value\n"
        " */\n"
        "function format(val) { return String(val); }\n"
    )
    concepts = scan_codebase(tmp)
    fmt = next((c for c in concepts if c.type == "Function" and c.title == "format"), None)
    assert fmt is not None, "format() not found"
    assert len(fmt.params) >= 1, f"format should have params from @param, got {fmt.params}"
    assert fmt.params[0]["name"] == "val", f"param should be 'val', got {fmt.params}"
    assert fmt.params[0]["annotation"] == "number", f"annotation should be 'number', got {fmt.params[0]}"
    import shutil; shutil.rmtree(tmp)


def test_ts_method_doc_tags():
    """TypeScript method JSDoc @param populates method concept params."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "service.ts").write_text(
        "class Service {\n"
        "  /**\n"
        "   * Process data.\n"
        "   * @param {string} input - the input data\n"
        "   * @returns {boolean} success flag\n"
        "   */\n"
        "  process(input: string): boolean { return true; }\n"
        "}\n"
    )
    concepts = scan_codebase(tmp)
    proc = next((c for c in concepts if c.type == "Function" and c.title == "process"), None)
    assert proc is not None, "process() not found"
    assert len(proc.params) >= 1, f"process should have params from @param, got {proc.params}"
    assert proc.params[0]["name"] == "input", f"param should be 'input', got {proc.params}"
    assert proc.params[0]["annotation"] == "string", f"annotation should be 'string', got {proc.params[0]}"
    import shutil; shutil.rmtree(tmp)


# ── Go const / var declarations (Tier 3) ─────────────────────────────────

def test_go_const_declaration():
    """Go const declarations are extracted as Constant concepts."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "main.go").write_text(
        "package main\n"
        "const MAX_SIZE = 1024\n"
        "const AppName string = \"myapp\"\n"
    )
    concepts = scan_codebase(tmp)
    consts = {c.title for c in concepts if c.type == "Constant"}
    assert "MAX_SIZE" in consts, f"MAX_SIZE not in constants: {consts}"
    assert "AppName" in consts, f"AppName not in constants: {consts}"
    app = next((c for c in concepts if c.title == "AppName"), None)
    assert app is not None
    assert "string" in app.signature, f"AppName signature should mention string: {app.signature}"
    import shutil; shutil.rmtree(tmp)


def test_go_var_declaration():
    """Go var declarations are extracted as Variable concepts."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "main.go").write_text(
        "package main\n"
        "var count = 0\n"
        "var name string\n"
    )
    concepts = scan_codebase(tmp)
    vars_found = {c.title for c in concepts if c.type == "Variable"}
    assert "count" in vars_found, f"count not in vars: {vars_found}"
    assert "name" in vars_found, f"name not in vars: {vars_found}"
    import shutil; shutil.rmtree(tmp)


def test_go_grouped_const():
    """Go grouped const (with parens) extracts all specs."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "main.go").write_text(
        "package main\n"
        "const (\n"
        "    StatusOK = 200\n"
        "    StatusNotFound = 404\n"
        ")\n"
    )
    concepts = scan_codebase(tmp)
    consts = {c.title for c in concepts if c.type == "Constant"}
    assert "StatusOK" in consts, f"StatusOK not in constants: {consts}"
    assert "StatusNotFound" in consts, f"StatusNotFound not in constants: {consts}"
    import shutil; shutil.rmtree(tmp)


# ── Ruby singleton_method (def self.foo) (Tier 3) ─────────────────────────

def test_ruby_singleton_method():
    """Ruby def self.foo is extracted as a Function concept."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.rb").write_text(
        "class Service\n"
        "  def self.status\n"
        "    :ok\n"
        "  end\n"
        "  def instance_method\n"
        "  end\n"
        "end\n"
    )
    concepts = scan_codebase(tmp)
    funcs = {c.title for c in concepts if c.type == "Function"}
    assert "status" in funcs, f"singleton method 'status' not found in {funcs}"
    assert "instance_method" in funcs, f"instance method not found in {funcs}"
    status = next((c for c in concepts if c.title == "status"), None)
    assert status is not None
    assert "self.status" in status.signature, f"signature should show self.status: {status.signature}"
    assert "singleton" in status.visibility, f"visibility should include 'singleton': {status.visibility}"
    import shutil; shutil.rmtree(tmp)


def test_ruby_singleton_in_class_methods():
    """Singleton methods appear in the class method listing."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.rb").write_text(
        "class Service\n"
        "  def self.status\n"
        "    :ok\n"
        "  end\n"
        "end\n"
    )
    concepts = scan_codebase(tmp)
    svc = next((c for c in concepts if c.type == "Class" and c.title == "Service"), None)
    assert svc is not None, "Service class not found"
    assert "status" in svc.methods, f"Service.methods should include status: {svc.methods}"
    import shutil; shutil.rmtree(tmp)


# ── C++ full template<typename T> signatures (Tier 3) ─────────────────────

def test_cpp_template_signature_includes_prefix():
    """C++ template class signature includes 'template<typename T>' prefix."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.cpp").write_text(
        "template<typename T>\n"
        "class Container {\n"
        "public:\n"
        "    void add(T val) {}\n"
        "};\n"
    )
    concepts = scan_codebase(tmp)
    container = next((c for c in concepts if c.type == "Class" and c.title == "Container"), None)
    assert container is not None, "Container class not found"
    assert "template<" in container.signature, \
        f"Container signature should include template<: {container.signature}"
    assert "typename T" in container.signature, \
        f"Container signature should include 'typename T': {container.signature}"
    import shutil; shutil.rmtree(tmp)


def test_cpp_template_function_signature():
    """C++ template function signature includes 'template<...>' prefix."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.cpp").write_text(
        "template<typename T, typename U>\n"
        "T convert(U val) { return T(); }\n"
    )
    concepts = scan_codebase(tmp)
    convert = next((c for c in concepts if c.type == "Function" and c.title == "convert"), None)
    assert convert is not None, "convert() not found"
    assert "template<" in convert.signature, \
        f"convert signature should include template<: {convert.signature}"
    assert "typename T, typename U" in convert.signature, \
        f"convert signature should include type params: {convert.signature}"
    import shutil; shutil.rmtree(tmp)


def test_okf_config_loads_defaults():
    """Config loader returns defaults when no file or env vars set."""
    import os
    from okf.config import load, _get
    saved = {}
    for e in ("OKF_API_KEY", "OKF_BASE_URL", "OKF_MODEL", "OKF_MAX_WORKERS"):
        saved[e] = os.environ.pop(e, None)
    try:
        cfg = load()
        assert _get(cfg, "llm.base_url", "") == "http://localhost:8080/v1"
        assert _get(cfg, "llm.model", "") == "local-model"
        assert _get(cfg, "llm.max_workers") == 2
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


def test_okf_config_env_var_overrides_file(tmp_path):
    """Env vars take precedence over config file values."""
    import os
    from okf.config import load, _get
    saved = os.environ.get("OKF_MODEL")
    try:
        os.environ["OKF_MODEL"] = "gpt-4"
        cfg = load()
        # Env vars no longer override config (removed by design)
        assert _get(cfg, "llm.model") == "local-model"
    finally:
        if saved:
            os.environ["OKF_MODEL"] = saved
        else:
            os.environ.pop("OKF_MODEL", None)


def test_okf_config_serve_defaults():
    """Config serve defaults are valid integers."""
    from okf.config import load, _get
    cfg = load()
    port = _get(cfg, "serve.port", 0)
    assert isinstance(port, int) and 0 < port < 65536
    host = _get(cfg, "serve.host", "")
    assert isinstance(host, str) and host


def test_okf_config_dump_and_read(tmp_path):
    """Written config file can be read back."""
    from okf.config import dump, load, _get
    import os
    saved = {e: os.environ.pop(e, None) for e in ("OKF_API_KEY", "OKF_BASE_URL", "OKF_MODEL", "OKF_MAX_WORKERS")}
    try:
        test_cfg = {"llm": {"api_key": "sk-test123", "model": "test-model"}}
        proj_file = tmp_path / ".okfconfig"
        dump(test_cfg, proj_file)
        assert proj_file.exists()
        # Temporarily replace CONFIG_FILES[0] to point to our tmp
        import okf.config as cfgmod
        orig = cfgmod.CONFIG_FILES[0]
        cfgmod.CONFIG_FILES[0] = proj_file
        try:
            loaded = load()
            assert _get(loaded, "llm.api_key") == "sk-test123"
            assert _get(loaded, "llm.model") == "test-model"
        finally:
            cfgmod.CONFIG_FILES[0] = orig
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


def test_dockerfile_syntax():
    """Dockerfile has valid commands."""
    from pathlib import Path
    lines = Path(__file__).parent.parent.joinpath("Dockerfile").read_text().splitlines()
    buf = ""
    joined = []
    for l in lines:
        s = l.strip()
        if not s or s.startswith("#"):
            continue
        buf += s
        if s.endswith("\\"):
            buf = buf[:-1]
        else:
            joined.append(buf)
            buf = ""
    keywords = {"FROM", "RUN", "WORKDIR", "ENTRYPOINT", "CMD", "COPY", "ENV", "EXPOSE"}
    for c in joined:
        kw = c.split()[0]
        assert kw in keywords, f"Unknown Dockerfile command: {c}"
    assert len(joined) >= 4, f"Too few commands: {joined}"


def test_docker_publish_workflow_yaml():
    """docker-publish.yml workflow is valid YAML."""
    import yaml
    wf = yaml.safe_load(Path(__file__).parent.parent.joinpath(".github/workflows/docker-publish.yml").read_text())
    assert wf.get("jobs", {}).get("build"), "Missing build job"
    steps = wf["jobs"]["build"]["steps"]
    step_ids = [s.get("uses", s.get("name", "")) for s in steps]
    assert any("docker/build-push-action" in u for u in step_ids), "Missing build-push step"


def test_pre_commit_hook_config_valid():
    """Pre-commit config YAML is parseable and contains okf hook."""
    import yaml
    cfg = yaml.safe_load(Path(__file__).parent.parent.joinpath(".pre-commit-config.yaml").read_text())
    local_hooks = [r for r in cfg.get("repos", []) if r.get("repo") == "local"]
    assert local_hooks, "No local hooks found"
    hook_ids = [h["id"] for h in local_hooks[0]["hooks"]]
    assert "okf-generate" in hook_ids, f"okf-generate hook missing: {hook_ids}"


def test_generate_accepts_enrich_flag(tmp_path):
    """--enrich flag does not crash (requires API key for actual enrichment)."""
    import subprocess, sys
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("def foo():\n    \"\"\"A test function.\"\"\"\n    pass\n")
    out = tmp_path / "bundle"
    # Without API key, --enrich should log a warning but not crash
    result = subprocess.run(
        [sys.executable, "-m", "okf.cli", "generate", str(src), str(out), "--enrich"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Enrich flag caused crash: stderr={result.stderr[:200]}"
    assert (out / "index.md").exists()
    output = (result.stdout + result.stderr).lower()
    assert "no api key" in output or "skipping" in output, f"Expected warning in output: {output[:300]}"


def test_cpp_template_type_params_still_populated():
    """C++ template type_params are populated alongside template prefix."""
    from okf.generator import scan_codebase
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "test.cpp").write_text(
        "template<typename T>\n"
        "class Container {\n"
        "public:\n"
        "    void add(T val) {}\n"
        "};\n"
    )
    concepts = scan_codebase(tmp)
    container = next((c for c in concepts if c.type == "Class" and c.title == "Container"), None)
    assert container is not None
    assert container.type_params, f"Container should have type_params"
    assert any("T" in tp for tp in container.type_params), \
        f"Container type_params should contain 'T': {container.type_params}"
    import shutil; shutil.rmtree(tmp)
