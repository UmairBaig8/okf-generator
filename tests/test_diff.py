"""Tests for okf/diff.py — bundle comparison against real versioned projects."""

import json
from pathlib import Path

V1 = Path(__file__).parent / "fixtures" / "realworld" / "python" / "easy"
V2 = Path(__file__).parent / "fixtures" / "realworld" / "python" / "easy_v2"


def _scan_and_write(src, dest):
    from okf.generator import scan_codebase, write_bundle
    concepts = scan_codebase(src)
    write_bundle(concepts, dest, "project", ["test"])
    return concepts


def test_diff_identical_bundles(tmp_path):
    """Two copies of the same bundle should have no differences."""
    from okf.diff import diff_bundles
    _scan_and_write(V1, tmp_path / "a")
    _scan_and_write(V1, tmp_path / "b")
    result = diff_bundles(tmp_path / "a", tmp_path / "b")
    assert len(result["added"]) == 0
    assert len(result["removed"]) == 0
    assert len(result["changed"]) == 0


def test_diff_v1_to_v2_adds_concepts(tmp_path):
    """Diff between v1 and v2 shows added concepts (new function, new file)."""
    from okf.diff import diff_bundles
    _scan_and_write(V1, tmp_path / "a")
    _scan_and_write(V2, tmp_path / "b")
    result = diff_bundles(tmp_path / "a", tmp_path / "b")
    assert len(result["added"]) >= 2, f"Expected >=2 added, got {len(result['added'])}"
    added_titles = [c["title"] for c in result["added"]]
    assert "batched" in added_titles, f"batched not in added: {added_titles}"
    assert "validate_email" in added_titles, f"validate_email not in added: {added_titles}"


def test_diff_v1_to_v2_changes_concepts(tmp_path):
    """Diff between v1 and v2 shows changed concepts (module doc updated)."""
    from okf.diff import diff_bundles
    _scan_and_write(V1, tmp_path / "a")
    _scan_and_write(V2, tmp_path / "b")
    result = diff_bundles(tmp_path / "a", tmp_path / "b")
    assert len(result["changed"]) >= 1, f"Expected >=1 changed, got {len(result['changed'])}"


def test_diff_json_output(tmp_path):
    """JSON output is valid and contains expected keys."""
    from okf.diff import diff_bundles, fmt_json
    _scan_and_write(V1, tmp_path / "a")
    _scan_and_write(V1, tmp_path / "b")
    result = diff_bundles(tmp_path / "a", tmp_path / "b")
    raw = fmt_json(result)
    data = json.loads(raw)
    assert "old_count" in data
    assert "new_count" in data
    assert "added" in data
    assert "removed" in data
    assert "changed" in data


def test_diff_concept_hash_stable(tmp_path):
    """Same content produces same hash."""
    from okf.diff import _concept_hash
    c1 = {"description": "test", "sections": {"signature": "fn"}, "tags": ["a", "b"], "body_extra": {}}
    c2 = {"description": "test", "sections": {"signature": "fn"}, "tags": ["b", "a"], "body_extra": {}}
    assert _concept_hash(c1) == _concept_hash(c2)
    c3 = {"description": "other", "sections": {"signature": "fn"}, "tags": ["a", "b"], "body_extra": {}}
    assert _concept_hash(c1) != _concept_hash(c3)


# ---------------------------------------------------------------------------
# Impact analysis tests
# ---------------------------------------------------------------------------


def _make_dep(
    title: str,
    cid: str,
    used_by: list[str],
    version: str = "==1.0.0",
    ecosystem: str = "pip",
) -> dict:
    """Build a mock Dependency concept dict with a ## Used By section."""
    used_by_lines = "\n".join(f"- [Mod](/{mid}.md)" for mid in used_by)
    raw = (
        f"---\ntitle: {title}\ntype: Dependency\n"
        f"resource: requirements.txt\ntags: [ecosystem:{ecosystem}, version:{version}]\n---\n"
        f"| Version constraint | `{version}` |\n"
        f"## Used By\n{used_by_lines}"
    )
    sections = {}
    if used_by:
        used_by_body = "\n".join(f"- [Mod](/{mid}.md)" for mid in used_by)
        sections["used by"] = used_by_body
    return {
        "type": "Dependency",
        "title": title,
        "concept_id": cid,
        "resource": "requirements.txt",
        "tags": [f"ecosystem:{ecosystem}", f"version:{version}"],
        "sections": sections,
        "raw": raw,
    }


def _make_module(title: str, cid: str, resource: str) -> dict:
    """Build a mock Module concept."""
    return {
        "type": "Module",
        "title": title,
        "concept_id": cid,
        "resource": resource,
        "tags": [],
        "sections": {},
        "raw": "",
    }


def _make_code(title: str, ctype: str, resource: str, cid: str | None = None) -> dict:
    """Build a mock Function or Class concept."""
    return {
        "type": ctype,
        "title": title,
        "concept_id": cid or f"{resource.replace('.py', '')}/{title}",
        "resource": resource,
        "tags": [],
        "sections": {},
        "raw": "",
    }


def test_parse_used_by():
    """_parse_used_by extracts module concept_ids from ## Used By."""
    from okf.diff import _parse_used_by

    dep = _make_dep("requests", "_dependencies/pip/requests", ["app", "worker"])
    ids = _parse_used_by(dep)
    assert "app" in ids
    assert "worker" in ids
    assert len(ids) == 2


def test_parse_used_by_empty():
    """_parse_used_by returns [] when ## Used By is empty or absent."""
    from okf.diff import _parse_used_by

    dep = _make_dep("requests", "_dependencies/pip/requests", [])
    assert _parse_used_by(dep) == []

    dep_no_section = {"type": "Dependency", "sections": {}}
    assert _parse_used_by(dep_no_section) == []


def test_impact_analysis_changed_dep():
    """impact_analysis traces a changed dep to affected modules and code."""
    from okf.diff import impact_analysis

    old_list = [
        _make_dep("requests", "_dependencies/pip/requests", ["app", "worker"], "==2.31.0"),
        _make_dep("click", "_dependencies/pip/click", ["app"], "==8.1.7"),
    ]
    new_list = [
        _make_dep("requests", "_dependencies/pip/requests", ["app", "worker"], "==2.32.0"),
        _make_dep("click", "_dependencies/pip/click", ["app"], "==8.1.7"),
        _make_module("app", "app", "app.py"),
        _make_module("worker", "worker", "worker.py"),
        _make_code("fetch_user", "Function", "app.py"),
        _make_code("process_data", "Function", "worker.py"),
    ]

    diff_result = {
        "old_path": "/old",
        "new_path": "/new",
        "old_count": 2,
        "new_count": 6,
        "added": [],
        "removed": [],
        "changed": [
            {
                "type": "Dependency",
                "title": "requests",
                "concept_id": "_dependencies/pip/requests",
                "resource": "requirements.txt",
                "description": "",
            }
        ],
    }

    impact = impact_analysis(old_list, new_list, diff_result)
    assert len(impact["changed_deps"]) == 1
    assert impact["changed_deps"][0]["title"] == "requests"
    assert impact["changed_deps"][0]["old_version"] == "==2.31.0"
    assert impact["changed_deps"][0]["new_version"] == "==2.32.0"
    assert len(impact["changed_deps"][0]["affected_modules"]) == 2
    modules = {m["title"] for m in impact["changed_deps"][0]["affected_modules"]}
    assert modules == {"app", "worker"}
    assert impact["total_impacted_modules"] == 2
    assert impact["total_impacted_code_concepts"] == 2


def test_impact_analysis_added_dep():
    """impact_analysis shows added deps (even with no current usage)."""
    from okf.diff import impact_analysis

    old_list = []
    new_list = [
        _make_dep("newpkg", "_dependencies/pip/newpkg", [], "==1.0.0"),
    ]
    diff_result = {
        "old_path": "/old", "new_path": "/new", "old_count": 0, "new_count": 1,
        "added": [{"type": "Dependency", "title": "newpkg", "concept_id": "_dependencies/pip/newpkg", "resource": "requirements.txt", "description": ""}],
        "removed": [],
        "changed": [],
    }
    impact = impact_analysis(old_list, new_list, diff_result)
    assert len(impact["added_deps"]) == 1
    assert impact["added_deps"][0]["title"] == "newpkg"


def test_impact_analysis_removed_dep():
    """impact_analysis traces a removed dep to modules that used it."""
    from okf.diff import impact_analysis

    old_list = [
        _make_dep("oldpkg", "_dependencies/pip/oldpkg", ["legacy_module"], "==1.0.0"),
        _make_module("legacy_module", "legacy_module", "legacy.py"),
        _make_code("do_stuff", "Function", "legacy.py"),
    ]
    new_list = [
        _make_module("legacy_module", "legacy_module", "legacy.py"),
        _make_code("do_stuff", "Function", "legacy.py"),
    ]
    diff_result = {
        "old_path": "/old", "new_path": "/new", "old_count": 3, "new_count": 2,
        "added": [],
        "removed": [{"type": "Dependency", "title": "oldpkg", "concept_id": "_dependencies/pip/oldpkg", "resource": "requirements.txt", "description": ""}],
        "changed": [],
    }
    impact = impact_analysis(old_list, new_list, diff_result)
    assert len(impact["removed_deps"]) == 1
    assert impact["removed_deps"][0]["title"] == "oldpkg"
    assert len(impact["removed_deps"][0]["affected_modules"]) == 1
    assert impact["removed_deps"][0]["affected_modules"][0]["title"] == "legacy_module"


def test_fmt_impact():
    """fmt_impact produces well-formed output with headers and summary."""
    from okf.diff import fmt_impact

    impact = {
        "changed_deps": [
            {
                "title": "requests", "concept_id": "_d/pip/requests",
                "ecosystem": "pip", "old_version": "==2.31.0", "new_version": "==2.32.0",
                "affected_modules": [
                    {"concept_id": "app", "title": "app", "resource": "app.py",
                     "code_concepts": [{"title": "fetch", "type": "Function"}]}
                ],
                "total_modules": 1, "total_code_concepts": 1,
            }
        ],
        "removed_deps": [],
        "added_deps": [],
        "total_impacted_modules": 1,
        "total_impacted_code_concepts": 1,
    }
    diff_result = {"old_path": "/old", "new_path": "/new", "old_count": 5, "new_count": 6}

    output = fmt_impact(impact, diff_result)
    assert "okf diff --impact" in output
    assert "requests" in output
    assert "→ 1 module(s), 1 concept(s)" in output
    assert "app (app.py)" in output
    assert "Impact:" in output
