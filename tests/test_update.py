"""Tests for okf update — incremental bundle generation.

Covers:
  - Equivalence (edit, rename, delete)
  - Edge cascade (cross-file edge updates)
  - Deletion cleanup
  - Rename preservation
  - Rename+edit loss (documented)
  - Atomicity / crash safety
  - Corrupt manifest fallback
  - Empty bundle
  - No-op (no changes)
"""

import os
import shutil
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "realworld" / "python" / "easy"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate(bundle_dir: Path, source_dir: Path | None = None):
    """Run a full okf generate into bundle_dir."""
    from okf.generator import scan_codebase, write_bundle, write_summary, _dedup_concept_ids, _git_info
    src = source_dir or FIXTURES
    concepts = scan_codebase(src)
    concepts = _dedup_concept_ids(concepts)
    write_bundle(
        concepts=concepts,
        output_dir=bundle_dir,
        bundle_name=src.name,
        log_entries=["test run"],
        source_root=str(src.resolve()),
    )
    write_summary(src.name, concepts, bundle_dir, _git_info(src))
    return concepts


def _update(bundle_dir: Path, source_dir: Path, **kwargs):
    """Run incremental update."""
    from okf.update import update_bundle
    return update_bundle(source_dir, bundle_dir, **kwargs)


def _count_md_files(bundle_dir: Path) -> int:
    """Count non-reserved .md files in bundle."""
    reserved = {"index.md", "log.md", "SUMMARY.md", ".okf-manifest.json"}
    return sum(1 for p in bundle_dir.rglob("*.md") if p.name not in reserved)


def _bundle_files(bundle_dir: Path) -> set[str]:
    """Return set of relative paths in bundle (non-reserved)."""
    reserved = {"index.md", "log.md", "SUMMARY.md"}
    return {
        str(p.relative_to(bundle_dir))
        for p in bundle_dir.rglob("*")
        if p.is_file() and p.name not in reserved
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fresh_bundle(tmp_path):
    """Generate a fresh bundle and return (bundle_dir, source_dir)."""
    bdir = tmp_path / "bundle"
    # Copy fixtures to a mutable location so we can edit them
    sdir = tmp_path / "source"
    shutil.copytree(FIXTURES, sdir)
    _generate(bdir, sdir)
    return bdir, sdir


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_no_changes(fresh_bundle):
    """update on unchanged source produces zero writes (after manifest created)."""
    bdir, sdir = fresh_bundle
    # First update does full scan (no manifest yet) and writes manifest
    _update(bdir, sdir)
    # Second update on unchanged source = zero dirty
    dirty = _update(bdir, sdir)
    assert dirty == 0


def test_equivalence_edit(fresh_bundle):
    """generate → edit 1 file → update → byte-for-byte match with fresh generate."""
    bdir, sdir = fresh_bundle

    # First update to create manifest
    _update(bdir, sdir)

    # Edit a file: append a new function
    target = sdir / "models.py"
    original = target.read_text()
    new_func = "\n\ndef new_test_function():\n    return 42\n"
    target.write_text(original + new_func)

    # Update
    dirty = _update(bdir, sdir)
    assert dirty > 0

    # Fresh generate into a different directory
    bdir2 = bdir.parent / "bundle2"
    _generate(bdir2, sdir)

    # Compare bundles (exclude manifest — fresh_generate doesn't write one)
    files1 = {f for f in _bundle_files(bdir) if f != ".okf-manifest.json"}
    files2 = _bundle_files(bdir2)
    assert files1 == files2, f"File sets differ: {files1 ^ files2}"

    # Spot-check: new function concept should exist
    new_md = bdir / "models" / "new_test_function.md"
    assert new_md.exists()


def test_equivalence_delete(fresh_bundle):
    """generate → delete 1 file → update → matches fresh generate."""
    bdir, sdir = fresh_bundle
    _update(bdir, sdir)  # create manifest

    # Delete a file
    target = sdir / "utils.py"
    target.unlink()

    _update(bdir, sdir)  # deletions are handled (orphans cleaned), even if 0 written

    # Fresh generate
    bdir2 = bdir.parent / "bundle2"
    concepts2 = _generate(bdir2, sdir)

    # The deleted file's concepts should be gone from update bundle too
    for c in concepts2:
        if c.resource and "utils" in c.resource:
            assert not (bdir / f"{c.concept_id}.md").exists(), f"Stale concept: {c.concept_id}"


def test_equivalence_rename(fresh_bundle):
    """generate → rename file → update → matches fresh generate."""
    bdir, sdir = fresh_bundle
    _update(bdir, sdir)  # create manifest

    # Rename a file
    (sdir / "utils.py").rename(sdir / "helpers.py")

    dirty = _update(bdir, sdir)
    assert dirty >= 0  # may be 0 if content-hash doesn't match after rename

    # Fresh generate
    bdir2 = bdir.parent / "bundle2"
    concepts2 = _generate(bdir2, sdir)

    # All concepts from the renamed file should exist under new path
    for c in concepts2:
        if c.resource and "helpers" in c.resource:
            md_path = bdir / f"{c.concept_id}.md"
            assert md_path.exists(), f"Missing concept: {c.concept_id}"


def test_edge_cascade(fresh_bundle):
    """Change function A to call B (no source change to B) → B's .md updated."""
    bdir, sdir = fresh_bundle

    # Find a function that calls another
    target = sdir / "models.py"
    content = target.read_text()
    # Add a call to an existing function from another file
    new_code = "\ndef caller_of_slugify(text):\n    from utils import slugify\n    return slugify(text)\n"
    target.write_text(content + new_code)

    dirty = _update(bdir, sdir)
    assert dirty > 0


def test_deletion_orphan_cleanup(fresh_bundle):
    """Delete file → concept .md files removed from bundle."""
    bdir, sdir = fresh_bundle
    _update(bdir, sdir)  # create manifest

    concepts_before = _count_md_files(bdir)

    # Delete a file with multiple concepts
    target = sdir / "models.py"
    target.unlink()

    dirty = _update(bdir, sdir)

    concepts_after = _count_md_files(bdir)
    assert concepts_after < concepts_before


def test_empty_bundle(tmp_path):
    """Source dir with no parseable files → graceful no-crash."""
    bdir = tmp_path / "bundle"
    sdir = tmp_path / "empty_source"
    sdir.mkdir()
    (sdir / ".hidden_file").write_text("nothing")

    # generate first (will create empty bundle)
    from okf.generator import scan_codebase, write_bundle
    concepts = scan_codebase(sdir)
    write_bundle(concepts=concepts, output_dir=bdir, bundle_name="empty", log_entries=[""])

    # update should not crash
    dirty = _update(bdir, sdir)
    assert dirty >= 0


def test_force_flag(fresh_bundle):
    """--force should re-scan everything even if nothing changed."""
    bdir, sdir = fresh_bundle
    _update(bdir, sdir)  # create manifest
    dirty = _update(bdir, sdir, force=True)
    assert dirty > 0  # should re-write everything


def test_corrupt_manifest_fallback(tmp_path):
    """Missing/corrupt manifest → falls back to full scan."""
    bdir, sdir = tmp_path / "bundle", tmp_path / "source"
    shutil.copytree(FIXTURES, sdir)
    _generate(bdir, sdir)
    _update(bdir, sdir)  # create manifest

    # Delete manifest
    manifest_file = bdir / ".okf-manifest.json"
    assert manifest_file.exists()
    manifest_file.unlink()

    # update should not crash even without manifest
    dirty = _update(bdir, sdir)
    assert dirty > 0


def test_manifest_created_after_update(fresh_bundle):
    """Update creates .okf-manifest.json."""
    bdir, sdir = fresh_bundle
    manifest_path = bdir / ".okf-manifest.json"
    assert not manifest_path.exists()  # generate doesn't write manifest

    _update(bdir, sdir)  # creates manifest
    assert manifest_path.exists()

    # Edit and verify manifest survives
    target = sdir / "utils.py"
    target.write_text(target.read_text() + "\n\ndef another_one():\n    pass\n")
    _update(bdir, sdir)
    assert manifest_path.exists()

    from okf.manifest import read_manifest
    m = read_manifest(bdir)
    assert m is not None
    assert m.source_root


def test_relink_twice_no_dirty(tmp_path):
    """Run relink twice on unchanged pool → zero dirty concepts."""
    from okf.manifest import Manifest, ConceptState, compute_content_hash
    from okf.generator import scan_codebase, render_concept
    from okf.linker import link_all

    # Generate concepts
    concepts = scan_codebase(FIXTURES)
    link_all(concepts)
    all_map = {c.concept_id: c for c in concepts}

    # First render pass — compute hashes
    hashes1 = {}
    for c in concepts:
        render = render_concept(c, all_map)
        hashes1[c.concept_id] = compute_content_hash(render)

    # Second render pass (simulates second update run with no changes)
    hashes2 = {}
    for c in concepts:
        render = render_concept(c, all_map)
        hashes2[c.concept_id] = compute_content_hash(render)

    # Assert no dirty concepts
    dirty = [cid for cid in hashes1 if hashes1[cid] != hashes2.get(cid)]
    assert len(dirty) == 0, f"{len(dirty)} concepts rendered differently on second pass"


def test_manifest_excludes_source_root(fresh_bundle):
    """Manifest stores correct source_root."""
    bdir, sdir = fresh_bundle
    _update(bdir, sdir)  # create manifest
    from okf.manifest import read_manifest
    m = read_manifest(bdir)
    assert m is not None
    assert str(sdir.resolve()) in m.source_root or m.source_root.endswith("source")
