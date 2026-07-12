"""Tests against 22 real-world fixture projects (easy + complex per language).

Fixtures at tests/fixtures/realworld/ — 96 files, ~4,500 lines, 13 languages.
Covers all extraction features: generics, inheritance, decorators, visibility,
fields, interfaces, enums, type aliases, SQL columns, manifests.
"""

import pytest
from pathlib import Path

REALWORLD = Path(__file__).parent / "fixtures" / "realworld"

# ── Language directories ────────────────────────────────────────────────────

LANGUAGE_DIRS = {
    "python":     REALWORLD / "python",
    "javascript": REALWORLD / "javascript",
    "typescript": REALWORLD / "typescript",
    "go":         REALWORLD / "go",
    "java":       REALWORLD / "java",
    "rust":       REALWORLD / "rust",
    "ruby":       REALWORLD / "ruby",
    "c":          REALWORLD / "c",
    "cpp":        REALWORLD / "cpp",
    "csharp":     REALWORLD / "csharp",
    "sql":        REALWORLD / "sql",
    "swift":      REALWORLD / "swift",
    "kotlin":     REALWORLD / "kotlin",
    "php":        REALWORLD / "php",
    "dart":       REALWORLD / "dart",
    "scala":      REALWORLD / "scala",
    "julia":      REALWORLD / "julia",
    "yaml":       REALWORLD / "yaml",
}


def scan(path: Path):
    from okf.generator import scan_codebase
    return scan_codebase(path)


def lang_tag(c):
    for t in c.tags:
        if t.startswith("lang:"):
            return t[5:]
    return ""


# ── Global coverage ─────────────────────────────────────────────────────────

def test_realworld_all_languages_detected():
    """Every supported language produces concepts from realworld fixtures."""
    concepts = scan(REALWORLD)
    langs = set()
    for c in concepts:
        tag = lang_tag(c)
        if tag:
            langs.add(tag)
    expected = {"python", "javascript", "typescript", "go", "java", "rust",
                "ruby", "c", "cpp", "csharp", "sql", "swift", "kotlin", "yaml", "manifest"}
    missing = expected - langs
    assert not missing, f"Languages missing from realworld: {missing}"


def test_realworld_total_concepts():
    """Realworld scans produce at least 400 concepts."""
    concepts = scan(REALWORLD)
    assert len(concepts) >= 400, f"Only {len(concepts)} concepts"


def test_realworld_all_concept_types_present():
    """All major concept types appear in realworld scan."""
    concepts = scan(REALWORLD)
    types = {c.type for c in concepts}
    for t in ("Function", "Class", "Module", "Dependency", "Table", "View",
              "Interface", "Index", "Trigger", "Type"):
        assert t in types, f"Concept type {t} missing from realworld"


# ── Feature coverage ────────────────────────────────────────────────────────

def test_realworld_generics():
    """At least 15 concepts with type_params across all languages."""
    concepts = scan(REALWORLD)
    with_tp = [c for c in concepts if c.type_params]
    assert len(with_tp) >= 15, f"Only {len(with_tp)} concepts with type_params"
    # Verify specific known generics exist (titles may include signatures like Vector<T>::push_back)
    titles = {c.title for c in with_tp}
    assert "Paginated" in titles, f"Rust Paginated<T> missing: {titles}"
    has_vect = any("Vector" in t for t in titles)
    assert has_vect, f"No Vector<T> found in C++ templates: {titles}"


def test_realworld_inheritance():
    """At least 8 concepts with inheritance across all languages."""
    concepts = scan(REALWORLD)
    with_inh = [c for c in concepts if c.inheritance]
    assert len(with_inh) >= 8, f"Only {len(with_inh)} concepts with inheritance"


def test_realworld_decorators():
    """At least 20 concepts with decorators/attributes/annotations."""
    concepts = scan(REALWORLD)
    with_dec = [c for c in concepts if c.decorators]
    assert len(with_dec) >= 20, f"Only {len(with_dec)} concepts with decorators"


def test_realworld_visibility():
    """At least 80 concepts with visibility modifiers."""
    concepts = scan(REALWORLD)
    with_vis = [c for c in concepts if c.visibility]
    assert len(with_vis) >= 80, f"Only {len(with_vis)} concepts with visibility"


def test_realworld_fields():
    """At least 20 concepts with fields."""
    concepts = scan(REALWORLD)
    with_fields = [c for c in concepts if c.fields]
    assert len(with_fields) >= 20, f"Only {len(with_fields)} concepts with fields"


# ── Per-language easy vs complex ────────────────────────────────────────────

@pytest.mark.parametrize("lang,dirpath", list(LANGUAGE_DIRS.items()))
def test_language_easy_and_complex_produce_concepts(lang, dirpath):
    """Each language has easy/ and complex/ dirs that both produce concepts."""
    for variant in ("easy", "complex"):
        p = dirpath / variant
        if not p.exists():
            pytest.skip(f"{p} does not exist")
        concepts = scan(p)
        assert len(concepts) >= 3, (
            f"{lang}/{variant} produced only {len(concepts)} concepts"
        )


@pytest.mark.parametrize("lang,dirpath", list(LANGUAGE_DIRS.items()))
def test_complex_richer_than_easy(lang, dirpath):
    """Complex projects produce more concepts than easy for each language."""
    easy_p = dirpath / "easy"
    complex_p = dirpath / "complex"
    if not easy_p.exists() or not complex_p.exists():
        pytest.skip(f"Missing easy or complex for {lang}")
    easy_c = len(scan(easy_p))
    complex_c = len(scan(complex_p))
    assert complex_c >= easy_c, (
            f"{lang}: complex ({complex_c}) should be >= easy ({easy_c})"
        )


# ── Language-specific feature depth ─────────────────────────────────────────

def test_python_complex_has_decorators():
    """Python complex project has @decorators on functions and classes."""
    concepts = scan(REALWORLD / "python" / "complex")
    with_dec = [c for c in concepts if c.decorators]
    assert len(with_dec) >= 3, f"Python complex: only {len(with_dec)} decorators"


def test_java_complex_has_generics_and_annotations():
    """Java complex project has generics and @Override/@Deprecated."""
    concepts = scan(REALWORLD / "java" / "complex")
    with_tp = [c for c in concepts if c.type_params]
    assert len(with_tp) >= 1, f"Java complex: no generics found"
    with_dec = [c for c in concepts if c.decorators]
    assert len(with_dec) >= 2, f"Java complex: only {len(with_dec)} annotations"


def test_typescript_complex_has_enums_interfaces_generics():
    """TypeScript complex has enums, interfaces, generics, visibility."""
    concepts = scan(REALWORLD / "typescript" / "complex")
    types = {c.type for c in concepts}
    assert "Interface" in types, "No interfaces in TS complex"
    assert any(c.type_params for c in concepts), "No generics in TS complex"
    with_vis = [c for c in concepts if c.visibility]
    assert len(with_vis) >= 3, f"Only {len(with_vis)} with visibility in TS complex"


def test_rust_complex_has_traits_generics_attributes():
    """Rust complex has traits, generics, derive attributes, enums."""
    concepts = scan(REALWORLD / "rust" / "complex")
    with_tp = [c for c in concepts if c.type_params]
    assert len(with_tp) >= 2, f"Rust complex: only {len(with_tp)} generics"
    with_dec = [c for c in concepts if c.decorators]
    assert len(with_dec) >= 2, f"Rust complex: only {len(with_dec)} attributes"
    # Traits are emitted as Class with methods
    trait_names = {c.title for c in concepts if c.type == "Class" and "Repository" in c.title}
    assert trait_names, f"No traits found in Rust complex: {[c.title for c in concepts if c.type == 'Class']}"


def test_cpp_complex_has_templates():
    """C++ complex has template class with type_params."""
    concepts = scan(REALWORLD / "cpp" / "complex")
    with_tp = [c for c in concepts if c.type_params]
    assert len(with_tp) >= 1, f"C++ complex: no templates found"


def test_go_complex_has_generics():
    """Go complex has Go 1.18+ generics."""
    concepts = scan(REALWORLD / "go" / "complex")
    with_tp = [c for c in concepts if c.type_params]
    assert len(with_tp) >= 1, f"Go complex: no generics found"


def test_csharp_complex_has_attributes_and_interfaces():
    """C# complex has [Serializable], interfaces, properties."""
    concepts = scan(REALWORLD / "csharp" / "complex")
    with_dec = [c for c in concepts if c.decorators]
    assert len(with_dec) >= 2, f"C# complex: only {len(with_dec)} attributes"
    types = {c.type for c in concepts}
    assert "Interface" in types, "No interface found in C# complex"


def test_sql_complex_has_fk_columns_views():
    """SQL complex has tables with FK refs, views, functions, triggers."""
    concepts = scan(REALWORLD / "sql" / "complex")
    with_fields = [c for c in concepts if c.fields]
    assert len(with_fields) >= 3, f"SQL complex: only {len(with_fields)} tables with fields"
    types = {c.type for c in concepts}
    assert "Trigger" in types, "No triggers in SQL complex"


def test_ruby_complex_has_inheritance():
    """Ruby complex has class inheritance."""
    concepts = scan(REALWORLD / "ruby" / "complex")
    with_inh = [c for c in concepts if c.inheritance]
    assert len(with_inh) >= 1, f"Ruby complex: no inheritance found"


def test_swift_complex_has_protocols_generics_enums():
    """Swift complex has protocols (Interfaces), generics, enums."""
    concepts = scan(REALWORLD / "swift" / "complex")
    types = {c.type for c in concepts}
    assert "Interface" in types, f"No protocols (Interface) in Swift complex: {types}"
    with_tp = [c for c in concepts if c.type_params]
    assert len(with_tp) >= 1, f"Swift complex: no generics found"
    # enums emit as Class with methods as enum cases
    enum_names = [c.title for c in concepts if c.type == "Class" and "Status" in c.title]
    assert enum_names, f"No enums found in Swift complex"


def test_kotlin_complex_has_interfaces_generics_data_classes():
    """Kotlin complex has interfaces, generics, data classes."""
    concepts = scan(REALWORLD / "kotlin" / "complex")
    types = {c.type for c in concepts}
    assert "Interface" in types, f"No interfaces in Kotlin complex: {types}"
    with_tp = [c for c in concepts if c.type_params]
    assert len(with_tp) >= 1, f"Kotlin complex: no generics found"
    # data classes emitted as Class with fields
    with_fields = [c for c in concepts if c.fields]
    assert len(with_fields) >= 2, f"Kotlin complex: only {len(with_fields)} with fields"
    # enums
    enum_names = [c.title for c in concepts if c.type == "Class" and "Status" in c.title]
    assert enum_names, f"No enums found in Kotlin complex"


def test_php_complex_has_interfaces_traits_enums():
    """PHP complex has interfaces, traits, enums, classes, methods."""
    concepts = scan(REALWORLD / "php" / "complex")
    types = {c.type for c in concepts}
    assert "Interface" in types, f"No interfaces in PHP complex: {types}"
    assert "Enum" in types, f"No enums in PHP complex: {types}"
    funcs = [c for c in concepts if c.type == "Function"]
    assert len(funcs) >= 4, f"PHP complex: only {len(funcs)} functions/methods"


def test_dart_complex_has_classes_mixins_enums():
    """Dart complex has classes, mixins, enums, top-level functions."""
    concepts = scan(REALWORLD / "dart" / "complex")
    types = {c.type for c in concepts}
    assert "Enum" in types, f"No enums in Dart complex: {types}"
    funcs = [c for c in concepts if c.type == "Function"]
    assert len(funcs) >= 4, f"Dart complex: only {len(funcs)} functions (expected >=4)"


def test_scala_complex_has_traits_enums_classes():
    """Scala complex has traits, enums, classes, case classes, functions."""
    concepts = scan(REALWORLD / "scala" / "complex")
    types = {c.type for c in concepts}
    assert "Interface" in types, f"No traits (Interface) in Scala complex: {types}"
    assert "Enum" in types, f"No enums in Scala complex: {types}"
    funcs = [c for c in concepts if c.type == "Function"]
    assert len(funcs) >= 3, f"Scala complex: only {len(funcs)} functions (expected >=3)"


def test_julia_complex_has_functions_structs_constants():
    """Julia complex has functions, structs, abstract types, constants."""
    concepts = scan(REALWORLD / "julia" / "complex")
    types = {c.type for c in concepts}
    assert "Function" in types, f"No functions in Julia complex: {types}"
    assert "Class" in types, f"No structs (Class) in Julia complex: {types}"
    assert "Constant" in types, f"No constants in Julia complex: {types}"
    funcs = [c for c in concepts if c.type == "Function"]
    assert len(funcs) >= 2, f"Julia complex: only {len(funcs)} functions (expected >=2)"


# ── Bundle generation ───────────────────────────────────────────────────────

def test_realworld_bundle_generation(tmp_path):
    """Generate a bundle from realworld fixtures."""
    from okf.generator import scan_codebase, write_bundle, write_summary
    concepts = scan_codebase(REALWORLD)
    write_bundle(
        concepts=concepts,
        output_dir=tmp_path,
        bundle_name="realworld",
        log_entries=["test"],
    )
    write_summary("realworld", concepts, tmp_path, {})
    assert (tmp_path / "SUMMARY.md").exists()
    assert (tmp_path / "index.md").exists()
    assert (tmp_path / "log.md").exists()
    assert (tmp_path / "_dependencies").is_dir()


def test_realworld_bundle_dependencies(tmp_path):
    """Realworld bundle has dependency concepts from manifests."""
    from okf.generator import scan_codebase, write_bundle
    concepts = scan_codebase(REALWORLD)
    write_bundle(
        concepts=concepts,
        output_dir=tmp_path,
        bundle_name="realworld",
        log_entries=["test"],
    )
    deps = [c for c in concepts if c.type == "Dependency"]
    assert len(deps) >= 30, f"Only {len(deps)} dependencies (expected >=30)"


# ── Lookup ──────────────────────────────────────────────────────────────────

def test_realworld_lookup_finds_concepts():
    """Lookup against realworld bundle finds matching concepts."""
    from okf.generator import scan_codebase, write_bundle
    from okf.lookup import load_bundle, search
    import tempfile, shutil
    tmp = Path(tempfile.mkdtemp())
    try:
        concepts = scan_codebase(REALWORLD)
        write_bundle(
            concepts=concepts,
            output_dir=tmp,
            bundle_name="realworld",
            log_entries=["test"],
        )
        bundle = load_bundle(tmp)
        results = search(bundle, tokens=["Paginated"])
        assert len(results) >= 1, "Paginated not found in lookup"
        results = search(bundle, tokens=["PaymentService"])
        assert len(results) >= 1, "PaymentService not found in lookup"
    finally:
        shutil.rmtree(tmp)


def test_realworld_lookup_by_type():
    """Lookup with type filter finds only matching concepts."""
    from okf.generator import scan_codebase, write_bundle
    from okf.lookup import load_bundle, search
    import tempfile, shutil
    tmp = Path(tempfile.mkdtemp())
    try:
        concepts = scan_codebase(REALWORLD)
        write_bundle(
            concepts=concepts,
            output_dir=tmp,
            bundle_name="realworld",
            log_entries=["test"],
        )
        bundle = load_bundle(tmp)
        deps = search(bundle, tokens=[], type_filter="Dependency", limit=200)
        assert len(deps) >= 30, f"Only {len(deps)} dependencies by type"
    finally:
        shutil.rmtree(tmp)
