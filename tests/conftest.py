"""Shared pytest fixtures for the okf-generator test suite."""

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "realworld"


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    """Generate a real OKF bundle once per module from the realworld fixtures."""
    tmp = tmp_path_factory.mktemp("bundle")
    from okf.generator import _dedup_concept_ids, scan_codebase, write_bundle
    concepts = scan_codebase(FIXTURES)
    concepts = _dedup_concept_ids(concepts)
    write_bundle(concepts, tmp, "sample", ["test"])
    return tmp


@pytest.fixture(scope="module")
def source_dir() -> Path:
    """The realworld fixtures directory (valid source root for enrichment/lsp tests)."""
    return FIXTURES
