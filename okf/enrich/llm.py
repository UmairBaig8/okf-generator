"""
okf/enrich/llm.py

LLM enrichment pass for an existing OKF bundle.  Implements the Enricher
contract so okf/enrich/__init__.py can run it alongside LspEnricher.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from ..parsers.base import Concept
from .base import EnrichResult, Enricher
from ._llm_prompts import DEEP_ENRICH_PROMPT, ENRICH_PROMPT, SECURITY_PROMPT

log = logging.getLogger("okf_gen")

_MAX_BODY_LINES = 120
_DEPRECATED_RE = re.compile(r"@deprecated|\bdeprecated\b", re.IGNORECASE)


def _read_source_root(bundle_dir: Path) -> Path | None:
    try:
        raw = (bundle_dir / "index.md").read_text(encoding="utf-8")
        parts = raw.split("---", 2)
        if len(parts) >= 2:
            import yaml
            fm = yaml.safe_load(parts[1]) or {}
            src = fm.get("source_root")
            if src:
                return Path(str(src)).resolve()
    except Exception:
        pass
    return None


def _read_body(concept: Concept, source_dir: Path | None = None, bundle_dir: Path | None = None) -> str:
    if not concept.resource or not concept.source_lines:
        return ""
    start, end = concept.source_lines
    if not start or not end or end < start:
        return ""
    if source_dir is None and bundle_dir is not None:
        src = _read_source_root(bundle_dir)
        if src is None:
            return ""
        source_dir = src
    if source_dir is None:
        return ""
    try:
        path = (source_dir / concept.resource).resolve()
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        snippet = lines[start - 1:end]
        if len(snippet) > _MAX_BODY_LINES:
            snippet = snippet[:_MAX_BODY_LINES] + ["# ... truncated ..."]
        return "\n".join(snippet)
    except Exception as e:
        log.debug(f"Could not read body for {concept.title}: {e}")
        return ""


def _detect_deprecation(concept: Concept) -> str:
    haystack = " ".join([concept.docstring or "", " ".join(concept.decorators or [])])
    if _DEPRECATED_RE.search(haystack):
        for line in (concept.docstring or "").splitlines():
            if _DEPRECATED_RE.search(line):
                return line.strip()
        return "Marked deprecated (see decorators)."
    return ""


_log_usage_calls: list[int] = []
_ENRICH_TOKENS: dict[str, int] = {}


def _log_usage(resp) -> None:
    try:
        u = resp.usage
        name = u.model or "unknown"
        _ENRICH_TOKENS[name] = _ENRICH_TOKENS.get(name, 0) + (u.total_tokens or 0)
    except Exception:
        pass


def _resolve_client(cfg: dict, mode: str):
    from openai import OpenAI
    from okf.config import resolve_provider
    r = resolve_provider(cfg, mode)
    client = OpenAI(base_url=r["base_url"], api_key=r["api_key"] or "no-key")
    return client, r


def _concept_output_path(concept: Concept, output_dir: Path) -> Path:
    cid = concept.concept_id.replace("/", os.sep) if hasattr(concept, "concept_id") else concept.title
    return (output_dir / cid).with_suffix(".md")




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
# Standalone enrichment functions (also called from generator.py for compat)
# ---------------------------------------------------------------------------

def enrich_concept(concept: Concept, client, model: str, max_tokens: int = 2000) -> Concept:
    needs_desc = not concept.description or len(concept.description) <= 120
    needs_doc = not concept.docstring or len(concept.docstring) <= 80
    if not needs_desc and not needs_doc:
        return concept
    if concept.type not in {"Function", "Class", "Method"}:
        if needs_desc and concept.docstring:
            concept.description = concept.docstring.strip().splitlines()[0][:120]
        return concept

    dep_note = _detect_deprecation(concept)
    if dep_note:
        concept.deprecation_notes = dep_note

    params_summary = ", ".join(
        f"{p.get('name', '?')}: {p.get('annotation', '?')}" for p in (concept.params or [])[:6]
    )
    try:
        prompt = ENRICH_PROMPT.format(
            type=concept.type, title=concept.title,
            docstring=concept.docstring or "(none)",
            signature=concept.signature or "(none)",
            params=params_summary or "(none)",
            returns=concept.returns or "(none)",
            inheritance=", ".join(concept.inheritance) if concept.inheritance else "(none)",
        )
        resp = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens, temperature=0.1,
        )
        raw = (resp.choices[0].message.content or "").strip()
        _log_usage(resp)
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw).strip()
        data = json.loads(raw)
        if data.get("description"):
            concept.description = str(data["description"]).strip()
        if data.get("docstring"):
            concept.docstring = str(data["docstring"]).strip()
        if data.get("tags"):
            existing = set(concept.tags)
            for t in data["tags"]:
                if t and str(t).strip() not in existing:
                    concept.tags.append(str(t).strip())
        if data.get("design_pattern"):
            concept.design_pattern = str(data["design_pattern"]).strip()
    except (json.JSONDecodeError, Exception) as e:
        log.debug(f"Enrichment failed for {concept.title}: {e}")

    return concept


def enrich_concept_deep(concept: Concept, client, model: str, source_dir: Path, max_tokens: int = 2000) -> Concept:
    if concept.type not in {"Function", "Class", "Method"}:
        return concept
    if concept.usage_example and concept.side_effects and concept.security and concept.complexity:
        return concept

    body = _read_body(concept, source_dir)
    if not body:
        log.debug(f"No body available for {concept.title}, skipping deep enrichment")
        return concept

    prompt = DEEP_ENRICH_PROMPT.format(
        type=concept.type, title=concept.title,
        signature=concept.signature or "none", body=body,
    )
    try:
        resp = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}],
            max_tokens=2000, temperature=0.1,
        )
        raw = (resp.choices[0].message.content or "").strip()
        _log_usage(resp)
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw).strip()
        data = json.loads(raw)
        if data.get("usage_example"):
            concept.usage_example = str(data["usage_example"]).strip()
        if data.get("side_effects"):
            concept.side_effects = str(data["side_effects"]).strip()
        if data.get("security"):
            concept.security = str(data["security"]).strip()
        if data.get("complexity"):
            concept.complexity = str(data["complexity"]).strip()
    except (json.JSONDecodeError, Exception) as e:
        log.debug(f"Deep-enrich failed for {concept.title}: {e}")

    return concept


def enrich_security(concept: Concept, client, model: str, source_dir: Path, max_tokens: int = 2000) -> Concept:
    if concept.type not in {"Function", "Class", "Method"}:
        return concept

    body = _read_body(concept, source_dir)
    if not body:
        log.debug(f"No body available for {concept.title}, skipping security audit")
        return concept

    prompt = SECURITY_PROMPT.format(
        type=concept.type, title=concept.title,
        signature=concept.signature or "none", body=body,
    )
    try:
        resp = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}],
            max_tokens=300, temperature=0.1,
        )
        raw = (resp.choices[0].message.content or "").strip()
        _log_usage(resp)
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw).strip()
        data = json.loads(raw)
        if data.get("security"):
            concept.security = str(data["security"]).strip()
        if data.get("complexity"):
            concept.complexity = str(data["complexity"]).strip()
    except (json.JSONDecodeError, Exception) as e:
        log.debug(f"Security audit failed for {concept.title}: {e}")

    return concept
