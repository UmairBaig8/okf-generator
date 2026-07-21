from abc import ABC, abstractmethod
from pathlib import Path


class BundleStore(ABC):
    @abstractmethod
    def close(self):
        ...

    @abstractmethod
    def get(self, concept_id: str) -> dict | None:
        ...

    @abstractmethod
    def search(
        self,
        query: str = "",
        type_filter: str = "",
        tag_filters: list[str] | None = None,
        limit: int = 80,
        offset: int = 0,
    ) -> list[dict]:
        ...

    @abstractmethod
    def count(self, type_filter: str = "", tag_filter: str = "") -> int:
        ...

    @abstractmethod
    def stream_all(self):
        """Yield every concept dict. For dump/export. Use with caution on large bundles."""
        ...

    @abstractmethod
    def get_neighbors(self, concept_id: str) -> list[dict]:
        """Return neighbor concepts (edges where concept_id is source or target)."""
        ...

    @abstractmethod
    def get_graph(self, max_nodes: int = 200, center: str | None = None) -> dict:
        """Return {nodes, edges, total, shown}."""
        ...

    @abstractmethod
    def get_types(self) -> list[dict]:
        ...

    @abstractmethod
    def get_languages(self) -> list[dict]:
        ...

    @abstractmethod
    def get_info(self) -> dict:
        ...

    @abstractmethod
    def transaction(self):
        """Context manager for bulk writes."""
        ...

    @abstractmethod
    def rebuild(self, bundle_dir: Path):
        """Rebuild store from markdown bundle."""
        ...

    @abstractmethod
    def update_file(self, path: Path):
        """Re-parse and upsert a single file."""
        ...

    @abstractmethod
    def remove_file(self, path: Path):
        """Delete concept(s) derived from a file."""
        ...
