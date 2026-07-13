"""
okf/enrich/__init__.py

Orchestrates LSP and/or LLM enrichment passes against an already-generated
OKF bundle.  Each enricher is wrapped in try/finally for subprocess
cleanup -- no global signal handlers.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from ..parsers.base import Concept
from .base import EnrichResult

log = logging.getLogger("okf_gen")


def _parse_source_line_range(source_text: str) -> tuple[int, int]:
    """Parse 'Lines 42-89 in `path/to/file.py`' → (42, 89)."""
    m = re.search(r"Lines\s+(\d+)\s*[–\-—−]\s*(\d+)", source_text)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return (0, 0)


def _dict_to_concept(d: dict) -> Concept:
    """Convert a raw bundle dict (from ``load_bundle``) to a Concept object."""
    s = d.get("sections", {})
    source_lines = _parse_source_line_range(s.get("source", "")) or d.get("source_lines", (0, 0))
    return Concept(
        type=d.get("type", ""),
        title=d.get("title", ""),
        description=d.get("description", ""),
        resource=d.get("resource", ""),
        tags=d.get("tags", []),
        concept_id=d.get("concept_id", ""),
        signature=s.get("signature", ""),
        docstring=s.get("docstring", ""),
        params=[dict(zip(["name", "annotation", "default"], [x.strip().strip("`") for x in p.split("|")[1:4]])) for p in s.get("parameters", "").splitlines() if "|" in p and "Name" not in p and "---" not in p] or d.get("params", []),
        returns=s.get("returns", "").strip("`").strip(),
        source_lines=source_lines,
        calls=d.get("calls", []),
        called_by=d.get("called_by", []),
        related=d.get("related", []),
        body_extra=d.get("body_extra", {}),
        # Preserve LLM-injected fields (orthogonal to LSP fields)
        security=s.get("security", ""),
        complexity=s.get("complexity", ""),
        design_pattern=s.get("design_pattern", ""),
        usage_example=s.get("usage_example", ""),
        side_effects=s.get("side_effects", ""),
        deprecation_notes=s.get("deprecation_notes", ""),
        methods=d.get("methods", []),
    )


def run_enrich(
    bundle_dir: Path,
    concepts_raw: list[dict],
    source_dir: Path,
    enable_lsp: bool = False,
    enable_llm: bool = False,
    llm_mode: str = "base",
) -> list[tuple[str, EnrichResult]]:
    """Run one or more enrichment passes against a bundle.

    Parameters
    ----------
    bundle_dir : Path
        Path to the OKF bundle directory (concept .md files live here).
    concepts_raw : list[dict]
        Deserialized concept dicts (from ``okf.pairs.load_bundle``).
    source_dir : Path
        Absolute path to the source code root (used by LSP for file resolution).
    enable_lsp : bool
        If True, run LSP enrichment (resolve caller/callee edges).
    enable_llm : bool
        If True, run LLM enrichment (summaries, deep analysis, security).
    llm_mode : str
        One of ``"base"``, ``"deep"``, or ``"security"``.

    Returns
    -------
    list[tuple[str, EnrichResult]]
        Each entry is ``(name, result)``.
    """
    results: list[tuple[str, EnrichResult]] = []

    # Convert once, share between enrichers
    concepts = [_dict_to_concept(d) for d in concepts_raw]

    if enable_lsp:
        from .lsp import LspEnricher

        enricher = LspEnricher(source_dir)
        try:
            if enricher.start(bundle_dir, concepts):
                log.info("LSP enrichment starting (discovery + references)...")
                result = enricher.run(bundle_dir, concepts)
                results.append(("lsp", result))
                log.info("LSP enrich done: %s (partial=%s)", result, result.is_partial)
            else:
                skipped = getattr(enricher, "_skipped_languages", [])
                log.info("LSP enrichment skipped; no servers available: %s", skipped)
        finally:
            enricher.stop()

    if enable_llm:
        from .llm import LlmEnricher

        enricher = LlmEnricher(source_dir, mode=llm_mode)
        try:
            if enricher.start(bundle_dir, concepts):
                log.info("LLM enrichment starting (mode=%s)...", llm_mode)
                result = enricher.run(bundle_dir, concepts)
                results.append(("llm", result))
                log.info("LLM enrich done: %s", result)
        finally:
            enricher.stop()

    if not results:
        log.info("No enrichment passes were enabled -- bundle unchanged.")

    return results
