"""
okf/enrich/llm.py

LLM enrichment pass for an existing OKF bundle.  Implements the Enricher
contract so okf/enrich/__init__.py can run it alongside LspEnricher.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..parsers.base import Concept
from .base import Enricher, EnrichResult

log = logging.getLogger("okf_gen")


def _read_source_root(bundle_dir: Path) -> Path | None:
    from ..generator import _read_source_root as _read
    return _read(bundle_dir)


def _read_body(concept: Concept, source_dir: Path | None = None, bundle_dir: Path | None = None) -> str:
    from ..generator import _read_body as _read
    return _read(concept, source_dir, bundle_dir)


def _detect_deprecation(concept: Concept) -> str:
    from ..generator import _detect_deprecation as _detect
    return _detect(concept)


def _resolve_client(cfg: dict, mode: str):
    """Create an LLM client for the given enrich mode.

    Delegates to generator._resolve_client (single source of truth) so the
    anthropic-provider support and error handling live in one place.
    """
    from okf.generator import _resolve_client as _resolve
    return _resolve(cfg, mode)


def _concept_output_path(concept: Concept, output_dir: Path) -> Path:
    from ..generator import _concept_output_path as _path
    return _path(concept, output_dir)




class LlmEnricher(Enricher):
    """LLM enrichment pass.  Wraps base/deep/security enrichment functions
    in the Enricher contract so run_enrich() can drive it uniformly."""

    def __init__(self, source_dir: Path, mode: str = "base"):
        self.source_dir = source_dir
        self.mode = mode
        self._client = None
        self._config = None
        self._model = ""

    def start(self, bundle_dir: Path, concepts: list[Any]) -> bool:
        from okf.config import load as load_config
        cfg = load_config()
        try:
            self._client, self._config = _resolve_client(cfg, "description" if self.mode in ("base",) else "deep")
            self._model = self._config["model"]
            log.info("LLM client ready: %s/%s", self._config["provider"], self._model)
            return True
        except ImportError as e:
            log.warning("LLM enrichment unavailable: %s. Install openai: pip install openai", e)
            return False

    def run(self, bundle_dir: Path, concepts: list[Any]) -> EnrichResult:
        warnings: list[str] = []

        if self.mode == "base":
            return self._run_base(bundle_dir, concepts)
        elif self.mode == "security":
            return self._run_security(bundle_dir, concepts)
        elif self.mode in ("deep", "full"):
            return self._run_deep(bundle_dir, concepts)
        else:
            warnings.append(f"Unknown LLM mode: {self.mode}")
            return EnrichResult(0, len(concepts), len(concepts), warnings)

    def stop(self) -> None:
        self._client = None
        self._config = None

    # -- mode implementations -----------------------------------------------

    def _run_base(self, bundle_dir: Path, concepts: list[Concept]) -> EnrichResult:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        from tqdm import tqdm

        enriched = 0
        skipped = 0
        max_workers = self._config.get("max_workers", 2)

        def _enrich_one(c: Concept) -> Concept:
            return enrich_concept(c, self._client, self._model, max_tokens=self._config.get("max_tokens", 2000))

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(_enrich_one, c): c for c in concepts}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Enriching"):
                try:
                    c = future.result()
                    md = self._render(c, concepts)
                    out = _concept_output_path(c, bundle_dir)
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_text(md, encoding="utf-8")
                    enriched += 1
                except Exception as e:
                    skipped += 1
                    log.debug(f"Enrich error: {e}")

        return EnrichResult(enriched, skipped, len(concepts))

    def _run_deep(self, bundle_dir: Path, concepts: list[Concept]) -> EnrichResult:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        from tqdm import tqdm

        enriched = 0
        skipped = 0
        max_workers = self._config.get("max_workers", 2)

        def _deep_one(c: Concept) -> Concept:
            c = enrich_concept(c, self._client, self._model, max_tokens=self._config.get("max_tokens", 2000))
            c = enrich_concept_deep(c, self._client, self._model, self.source_dir, max_tokens=self._config.get("max_tokens", 2000))
            return c

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(_deep_one, c): c for c in concepts}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Deep enrich"):
                try:
                    c = future.result()
                    md = self._render(c, concepts)
                    out = _concept_output_path(c, bundle_dir)
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_text(md, encoding="utf-8")
                    enriched += 1
                except Exception as e:
                    skipped += 1
                    log.debug(f"Deep enrich error: {e}")

        return EnrichResult(enriched, skipped, len(concepts))

    def _run_security(self, bundle_dir: Path, concepts: list[Concept]) -> EnrichResult:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        from tqdm import tqdm

        enriched = 0
        skipped = 0

        targets = []
        for c in concepts:
            if c.type not in {"Function", "Class", "Method"}:
                continue
            if not c.source_lines or c.source_lines[0] < 1:
                continue
            body = _read_body(c, self.source_dir)
            if not body:
                continue
            targets.append(c)

        def _audit_one(c: Concept) -> str:
            enrich_security(c, self._client, self._model, self.source_dir, max_tokens=self._config.get("max_tokens", 2000))
            return "done"

        with ThreadPoolExecutor(max_workers=self._config.get("max_workers", 2)) as pool:
            futures = {pool.submit(_audit_one, c): c for c in targets}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Security audit"):
                try:
                    future.result()
                    enriched += 1
                except Exception:
                    skipped += 1

        return EnrichResult(enriched, skipped, len(concepts))

    @staticmethod
    def _render(concept: Concept, all_concepts: list[Concept]) -> str:
        from ..generator import render_concept
        all_map = {c.concept_id: c for c in all_concepts}
        return render_concept(concept, all_map)


# ---------------------------------------------------------------------------
# Standalone enrichment functions — delegated to generator.py (single source
# of truth; generator's versions carry the JSON-fallback + robustness fixes).
# ---------------------------------------------------------------------------

def enrich_concept(concept: Concept, client, model: str, max_tokens: int = 2000) -> Concept:
    from ..generator import enrich_concept as _enrich
    return _enrich(concept, client, model, max_tokens=max_tokens)


def enrich_concept_deep(concept: Concept, client, model: str, source_dir: Path, max_tokens: int = 2000) -> Concept:
    from ..generator import enrich_concept_deep as _enrich
    return _enrich(concept, client, model, source_dir, max_tokens=max_tokens)


def enrich_security(concept: Concept, client, model: str, source_dir: Path, max_tokens: int = 2000) -> Concept:
    from ..generator import enrich_security as _enrich
    return _enrich(concept, client, model, source_dir, max_tokens=max_tokens)
