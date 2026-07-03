"""Tests for okf.lookup — load_bundle, search, formatters."""

import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures" / "realworld"


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    """Generate a bundle once for all lookup tests."""
    tmp = tmp_path_factory.mktemp("bundle")
    from okf.generator import scan_codebase, write_bundle, _dedup_concept_ids
    concepts = scan_codebase(FIXTURES)
    concepts = _dedup_concept_ids(concepts)
    write_bundle(concepts, tmp, "sample", ["test"])
    return tmp


# ── load_bundle ───────────────────────────────────────────────────────────────

def test_load_bundle_returns_concepts(bundle):
    from okf.lookup import load_bundle
    concepts = load_bundle(bundle)
    assert len(concepts) > 0


def test_load_bundle_skips_index_files(bundle):
    from okf.lookup import load_bundle
    concepts = load_bundle(bundle)
    types = {c["type"] for c in concepts}
    assert "Index" not in types
    assert "Log" not in types


def test_load_bundle_concept_has_required_fields(bundle):
    from okf.lookup import load_bundle
    concepts = load_bundle(bundle)
    for c in concepts:
        assert "type" in c
        assert "title" in c
        assert "concept_id" in c
        assert "resource" in c


def test_load_bundle_concept_id_from_path(bundle):
    from okf.lookup import load_bundle
    concepts = load_bundle(bundle)
    for c in concepts:
        # concept_id must be a relative path, no leading slash
        assert not c["concept_id"].startswith("/"), f"Bad concept_id: {c['concept_id']}"
        assert ".md" not in c["concept_id"], f"concept_id should not have .md: {c['concept_id']}"


# ── search ────────────────────────────────────────────────────────────────────

def test_search_exact_name(bundle):
    from okf.lookup import load_bundle, search
    concepts = load_bundle(bundle)
    results = search(concepts, tokens=["Calculator"])
    assert len(results) > 0
    assert results[0]["title"] == "Calculator"


def test_search_fuzzy_name(bundle):
    from okf.lookup import load_bundle, search
    concepts = load_bundle(bundle)
    results = search(concepts, tokens=["calc"])
    titles = [r["title"] for r in results]
    assert "Calculator" in titles


def test_search_by_file(bundle):
    from okf.lookup import load_bundle, search
    concepts = load_bundle(bundle)
    results = search(concepts, tokens=[], file_filter="utils.py")
    assert len(results) > 0
    for r in results:
        assert "utils" in r["resource"].lower()


def test_search_by_type(bundle):
    from okf.lookup import load_bundle, search
    concepts = load_bundle(bundle)
    results = search(concepts, tokens=[], type_filter="Class")
    for r in results:
        assert r["type"] == "Class"


def test_search_by_tag(bundle):
    from okf.lookup import load_bundle, search
    concepts = load_bundle(bundle)
    results = search(concepts, tokens=[], tag_filters=["lang:python"])
    assert len(results) > 0
    for r in results:
        assert "lang:python" in r["tags"]


def test_search_empty_query_returns_all(bundle):
    from okf.lookup import load_bundle, search
    concepts = load_bundle(bundle)
    results = search(concepts, tokens=[], limit=1000)
    assert len(results) == len(concepts)


def test_search_limit(bundle):
    from okf.lookup import load_bundle, search
    concepts = load_bundle(bundle)
    results = search(concepts, tokens=[], limit=2)
    assert len(results) <= 2


def test_search_no_results(bundle):
    from okf.lookup import load_bundle, search
    concepts = load_bundle(bundle)
    results = search(concepts, tokens=["ZZZZ_NOT_FOUND_12345"])
    assert len(results) == 0


def test_search_paginated_generic(bundle):
    """Search for a known Rust generic concept from realworld fixtures."""
    from okf.lookup import load_bundle, search
    concepts = load_bundle(bundle)
    results = search(concepts, tokens=["Paginated"])
    assert len(results) > 0
    assert results[0]["title"] == "Paginated"


def test_search_camelcase_breaks_into_tokens(bundle):
    """CamelCase names match snake_case queries via tokenization."""
    from okf.lookup import load_bundle, search
    concepts = load_bundle(bundle)
    # "user" should find "UserService", "UserRepository", "UserStore" etc.
    results = search(concepts, tokens=["user"])
    titles = [r["title"].lower() for r in results]
    assert any("user" in t for t in titles), f"No user-related found: {titles[:10]}"


def test_search_camelcase_token_matches_subword(bundle):
    """Tokenized query matches camelCase subwords (e.g. 'repo' finds 'UserRepository')."""
    from okf.lookup import load_bundle, search
    concepts = load_bundle(bundle)
    results = search(concepts, tokens=["repo"])
    titles = [r["title"].lower() for r in results]
    assert any("repo" in t for t in titles), f"No repo matches: {titles[:10]}"


def test_search_acronym_matches_title_initials(bundle):
    """Acronym query matches initials of camelCase words."""
    from okf.lookup import load_bundle, search
    concepts = load_bundle(bundle)
    # "ur" should match "UserRepository"
    results = search(concepts, tokens=["ur"])
    titles = [r["title"].lower() for r in results]
    assert any("userrepo" in t.replace("_","") for t in titles), f"No acronym match: {titles[:10]}"


def test_search_exact_flag_requires_high_score(bundle):
    """--exact flag (min_score=0.9) rejects fuzzy matches."""
    from okf.lookup import load_bundle, search
    concepts = load_bundle(bundle)
    # "calc" would normally fuzzy-match "Calculator", but with exact it won't
    results = search(concepts, tokens=["calc"], min_score=0.9)
    titles = [r["title"] for r in results]
    # Calculator should NOT appear with exact match on "calc"
    assert "Calculator" not in titles


def test_search_tokenize_helper():
    """_tokenize correctly splits camelCase and snake_case."""
    from okf.lookup import _tokenize
    toks = _tokenize("UserRepository")
    assert "user" in toks
    assert any("repo" in t for t in toks), f"Expected 'repo' in {toks}"
    toks2 = _tokenize("user_repo")
    assert "user" in toks2
    assert "repo" in toks2
    toks3 = _tokenize("CreateUserDto")
    assert "create" in toks3
    assert "user" in toks3


# ── formatters ────────────────────────────────────────────────────────────────

def test_fmt_compact(bundle):
    from okf.lookup import load_bundle, search, fmt_compact
    concepts = load_bundle(bundle)
    results = search(concepts, tokens=["Paginated"])
    assert len(results) > 0
    line = fmt_compact(results[0])
    assert "Paginated" in line
    assert len(line.split("\n")) == 1   # single line


def test_fmt_detail(bundle):
    from okf.lookup import load_bundle, search, fmt_detail
    concepts = load_bundle(bundle)
    results = search(concepts, tokens=["User"], type_filter="Class")
    assert len(results) > 0
    detail = fmt_detail(results[0])
    assert "User" in detail


def test_fmt_json(bundle):
    import json
    from okf.lookup import load_bundle, search, fmt_json
    concepts = load_bundle(bundle)
    results = search(concepts, tokens=["Paginated"])
    assert len(results) > 0
    out = fmt_json(results)
    parsed = json.loads(out)
    assert isinstance(parsed, list)
    assert len(parsed) > 0
    assert "title" in parsed[0]
    assert "type" in parsed[0]
    assert "concept_id" in parsed[0]
