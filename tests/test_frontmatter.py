"""Round-trip tests for the fast OKF frontmatter serializer.

Every test fixture serializes with dump_frontmatter(), then parses back
with yaml.safe_load() — the parsed dict MUST equal the original.
"""

import yaml
import pytest
from okf.frontmatter import dump_frontmatter


def _roundtrip(fm: dict):
    """Serialize *fm* and assert it round-trips through yaml.safe_load."""
    raw = dump_frontmatter(fm)
    # Strip the leading/trailing --- delimiters before parsing
    body = raw.strip().removeprefix("---").removesuffix("---").strip()
    parsed = yaml.safe_load(body) if body else {}
    assert parsed == fm, f"\n  expected: {fm}\n  got:      {parsed}\n  raw:      {raw!r}"


# ── Standard OKF frontmatter shapes ─────────────────────────────────

def test_minimal():
    _roundtrip({"okf_version": "0.2", "type": "Module"})


def test_typical_class():
    _roundtrip({
        "okf_version": "0.2",
        "type": "Class",
        "title": "WorldBankConnector",
        "description": "Connects to the World Bank API for economic indicators",
        "resource": "StockAI/RnD/python/connectors/economic_data.py",
        "tags": ["lang:python", "type:Class", "module:StockAI", "domain:RnD"],
        "timestamp": "2026-07-19T12:00:00Z",
        "concept_id": "StockAI/RnD/python/connectors/economic_data/WorldBankConnector",
        "language": "python",
    })


def test_function():
    _roundtrip({
        "okf_version": "0.2",
        "type": "Function",
        "title": "get_indicator",
        "resource": "StockAI/RnD/python/connectors/economic_data.py",
        "tags": ["lang:python", "type:Function", "module:StockAI"],
        "language": "python",
        "status": "active",
    })


def test_dependency():
    _roundtrip({
        "okf_version": "0.2",
        "type": "Dependency",
        "title": "requests",
        "resource": "requirements.txt",
        "tags": ["ecosystem:pip", "type:Dependency", "module:StockAI"],
        "language": "manifest",
    })


def test_module_index():
    _roundtrip({
        "type": "Index",
        "title": "WSpace — Knowledge Summary",
        "description": "Top-level OKF summary: 41146 concepts across 28 domains",
        "okf_version": "0.2",
        "timestamp": "2026-07-19T12:00:00Z",
    })


# ── Adversarial strings (must be quoted) ────────────────────────────

@pytest.mark.parametrize("val", [
    # Colons inside strings
    "Function: _init_",
    "time:out",
    # Leading special characters
    "@decorator",
    "#comment",
    "- leading dash",
    "*bold*",
    "? what",
    "!important",
    # Quotes inside strings
    'Print("Hello")',
    "it's",
    # YAML 1.1 keywords
    "true",
    "True",
    "false",
    "yes",
    "no",
    "null",
    "Null",
    "~",
    # Numeric-looking strings
    "0.2",
    "42",
    "3.14",
    "1e10",
    # Empty and whitespace
    "",
    # Unicode
    "こんにちは",
    "🚀",
    "café",
    # Multiline
    "line1\nline2",
    # Special chars
    "abc # def",
    "foo & bar",
    "list: [1, 2]",
    "dict: {a: 1}",
    # Windows-style path (backslash)
    "C:\\Users\\test\\file.py",
    # Backslash in general
    "namespace\\sub\\module",
])
def test_adversarial_title(val):
    _roundtrip({
        "okf_version": "0.2",
        "type": "Function",
        "title": val,
        "resource": "test.py",
        "tags": ["lang:python"],
        "language": "python",
    })


@pytest.mark.parametrize("desc", [
    "",
    "A" * 1000,  # very long description
    "line1\nline2\nline3",
    "Description with: colons and # hashes",
    'Description with "quotes"',
    "  leading spaces",
    "trailing spaces  ",
    "Unicode: こんにちは世界 🚀",
])
def test_adversarial_description(desc):
    _roundtrip({
        "okf_version": "0.2",
        "type": "Class",
        "title": "Foo",
        "description": desc,
        "resource": "foo.py",
        "tags": ["lang:python"],
        "language": "python",
    })


# ── Edge cases for tags (list of strings) ──────────────────────────

@pytest.mark.parametrize("tags", [
    [],
    [""],
    [" "],
    ["tag:with:colons"],
    ["tag#hash"],
    ["true", "false", "null"],
    ["2026"],
    ["-leading-dash"],
    ["@scoped/pkg"],
    ["namespace::sub"],
    ["a" * 500],  # very long tag
])
def test_adversarial_tags(tags):
    _roundtrip({
        "okf_version": "0.2",
        "type": "Function",
        "title": "foo",
        "resource": "foo.py",
        "tags": tags,
        "language": "python",
    })


# ── Edge cases for resource paths ──────────────────────────────────

@pytest.mark.parametrize("resource", [
    "",
    "file.py",
    "path/to/file.py",
    "path/to/file with spaces.py",
    "C:\\Users\\test\\file.py",
    "namespace:sub/module.py",
    "@org/repo/file.ts",
])
def test_adversarial_resource(resource):
    _roundtrip({
        "okf_version": "0.2",
        "type": "Module",
        "title": "module",
        "resource": resource,
        "tags": [],
        "language": "python",
    })


# ── Various dict shapes ────────────────────────────────────────────

def test_all_fields_populated():
    _roundtrip({
        "okf_version": "0.2",
        "type": "Class",
        "title": "MyClass",
        "description": "A class with all fields",
        "resource": "my_class.py",
        "tags": ["lang:python", "type:Class", "module:test"],
        "timestamp": "2026-01-01T00:00:00Z",
        "concept_id": "test/my_class/MyClass",
        "language": "python",
        "status": "active",
    })


def test_version_strings():
    """Version-like strings must not be misinterpreted as numbers."""
    for ver in ["0.1", "0.2", "1.0", "2.0.0", "v1.2.3"]:
        _roundtrip({"okf_version": ver, "type": "Module", "title": "m"})


def test_timestamp_variants():
    for ts in [
        "2026-07-19T12:00:00Z",
        "2026-07-19",
        "2026-07-19 12:00:00",
        "2026-07-19T12:00:00+00:00",
    ]:
        _roundtrip({
            "okf_version": "0.2",
            "type": "Module",
            "timestamp": ts,
        })


def test_concept_id_variants():
    for cid in [
        "test/Foo",
        "domain/subdomain/module/Foo",
        "a/b/c/d/e/f/g",
        "true/false/null",  # path segments that look like keywords
    ]:
        _roundtrip({
            "okf_version": "0.2",
            "type": "Class",
            "title": "Foo",
            "concept_id": cid,
            "tags": [],
        })


# ── Empty dict ─────────────────────────────────────────────────────

def test_empty_dict():
    raw = dump_frontmatter({})
    assert raw == "---\n---\n"
    body = raw.strip().removeprefix("---").removesuffix("---").strip()
    assert body == ""


# ── Full template rendering integration test ───────────────────────

def test_full_concept_roundtrip():
    """Simulate what generator._frontmatter does with a real Concept."""
    fm = {
        "okf_version": "0.2",
        "type": "Class",
        "title": "DataProcessor",
        "description": "Processes and transforms data pipelines with ETL support",
        "resource": "etl/processor.py",
        "tags": [
            "lang:python",
            "type:Class",
            "module:etl",
            "domain:core",
            "git:branch:main",
            "git:repo:myproject",
        ],
        "timestamp": "2026-07-19T12:34:56Z",
        "concept_id": "etl/processor/DataProcessor",
        "language": "python",
        "status": "active",
    }
    _roundtrip(fm)


# ── Fallback test: unsupported types delegate to yaml.safe_dump ────

def test_fallback_nested_dict():
    """A value that's a dict (not in our schema) must fall back."""
    raw = dump_frontmatter({"type": "Module", "nested": {"a": 1}})
    assert "a: 1" in raw  # yaml.safe_dump format
    body = raw.strip().removeprefix("---").removesuffix("---").strip()
    parsed = yaml.safe_load(body)
    assert parsed == {"type": "Module", "nested": {"a": 1}}
