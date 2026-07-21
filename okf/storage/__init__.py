from pathlib import Path
from okf.lookup import load_bundle
from okf.storage.sqlite import SQLiteBundleStore
from okf.storage.memory import MemoryBundleStore


def open_store(bundle_dir: Path, prefer_memory: bool = False) -> MemoryBundleStore | SQLiteBundleStore:
    """Open a BundleStore for the given bundle directory.

    - If prefer_memory is True (or no SQLite available), returns MemoryBundleStore.
    - If a fresh .okf_db.sqlite exists, returns SQLiteBundleStore (fast path).
    - Otherwise builds SQLite from markdown and returns it.
    """
    if prefer_memory:
        concepts = load_bundle(bundle_dir, use_cache=False)
        return MemoryBundleStore(concepts)

    db_path = bundle_dir / ".okf_db.sqlite"

    if SQLiteBundleStore.db_is_fresh(db_path, bundle_dir):
        return SQLiteBundleStore(db_path)

    # Build from markdown
    store = SQLiteBundleStore.build(bundle_dir, db_path)
    return store
