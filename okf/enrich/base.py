"""
okf/enrich/base.py

Abstract contract that both LspEnricher and LlmEnricher implement, so
okf/enrich/__init__.py can orchestrate them uniformly without knowing
which one it's talking to.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class EnrichResult:
    """Outcome of a single enrich pass, returned by run()."""

    def __init__(
        self,
        enriched_count: int,
        skipped_count: int,
        total_count: int,
        warnings: list[str] | None = None,
    ):
        self.enriched_count = enriched_count
        self.skipped_count = skipped_count
        self.total_count = total_count
        self.warnings = warnings or []

    @property
    def is_partial(self) -> bool:
        return self.skipped_count > 0

    def __repr__(self) -> str:
        return (
            f"EnrichResult({self.enriched_count}/{self.total_count} enriched, "
            f"{self.skipped_count} skipped)"
        )


class Enricher(ABC):
    """
    Base contract. Concrete enrichers (LspEnricher, LlmEnricher) must:
      - be safe to call run() on a bundle that's already been enriched
        (idempotent — overwrite own fields, never duplicate/append)
      - never raise on partial failure; collect warnings and keep going,
        write whatever succeeded, report skipped_count honestly
      - clean up any subprocess/connection state in stop(), and stop()
        must be safe to call even if start() was never called or failed
    """

    @abstractmethod
    def start(self, bundle_dir: Path, concepts: list[Any]) -> bool:
        """
        Prepare the enricher (e.g. boot LSP servers, resolve LLM client).
        Returns False if the enricher can't run at all (e.g. no LSP
        binaries found, no API key configured) — caller should log and
        skip this enricher entirely, not treat it as a fatal error.
        """
        raise NotImplementedError

    @abstractmethod
    def run(self, bundle_dir: Path, concepts: list[Any]) -> EnrichResult:
        """
        Do the enrichment and write updated bundle files. Must only be
        called after a successful start(). Must not raise on individual
        concept failures — record them and continue.
        """
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """Release any resources. Always safe to call, even after a failed start()."""
        raise NotImplementedError

    def __enter__(self) -> "Enricher":
        return self

    def __exit__(self, *exc_info) -> None:
        self.stop()
