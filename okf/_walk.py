"""Fast filtered directory walker.

Replaces `Path.rglob("*")` for large trees. Uses `os.walk` with in-place
directory pruning so we never descend into hidden, vendor, or ignored
directories (saves ~95% of syscalls on repos with node_modules / .venv).
"""

import os
import sys
from pathlib import Path
from typing import Generator

from okf.ignore import matches as ignore_matches
from okf.parsers.base import SKIP_DIRS, SKIP_DIR_SUFFIXES


# Detect CPU count for worker pool sizing
_CPU_COUNT = os.cpu_count() or 4
MAX_WORKERS = min(32, _CPU_COUNT * 2)
MAX_PARALLEL_WORKERS = _CPU_COUNT  # for CPU-bound parallelism (parsing)


def _skip_dir(name: str) -> bool:
    return (
        name.startswith(".") or
        name in SKIP_DIRS or
        any(name.endswith(sfx) for sfx in SKIP_DIR_SUFFIXES)
    )


def walk_files(
    root: Path,
    ignore_pats: list | None = None,
    exclude: set[str] | None = None,
) -> Generator[Path, None, None]:
    """Yield file paths under *root*, skipping excluded dirs at the dir level.

    Uses ``os.walk`` with in-place ``dirnames`` mutation so we never descend
    into ``node_modules``, ``.venv``, ``.git``, etc. — the OS does not even
    ``readdir`` their children.

    Args:
        root: Top-level directory to walk.
        ignore_pats: Compiled .okfignore / .gitignore patterns (from
            ``okf.ignore.load_patterns``).  Pass ``None`` to skip pattern
            matching (faster but less accurate).
        exclude: Additional directory basenames to skip (e.g. ``{"tests"}``).

    Yields:
        ``Path`` for every non-excluded file under *root*.
    """
    exclude = exclude or set()
    for dirpath_str, dirnames, filenames in os.walk(str(root), topdown=True):
        # Prune hidden / vendor / excluded directories in-place
        i = 0
        while i < len(dirnames):
            d = dirnames[i]
            if _skip_dir(d) or d in exclude:
                del dirnames[i]
                continue
            if ignore_pats:
                rel = Path(dirpath_str).relative_to(root) / d
                if ignore_matches(rel, ignore_pats):
                    del dirnames[i]
                    continue
            i += 1
        # Yield regular files
        for f in filenames:
            yield Path(dirpath_str) / f


def walk_dirs(
    root: Path,
    ignore_pats: list | None = None,
    exclude: set[str] | None = None,
) -> set[str]:
    """Yield relative directory paths under *root* (like ``_walk_source_dirs``).

    The returned set always includes ``""`` (the root itself).
    """
    exclude = exclude or set()
    dirs = {""}
    for dirpath_str, dirnames, _ in os.walk(str(root), topdown=True):
        i = 0
        while i < len(dirnames):
            d = dirnames[i]
            if _skip_dir(d) or d in exclude:
                del dirnames[i]
                continue
            if ignore_pats:
                rel = Path(dirpath_str).relative_to(root) / d
                if ignore_matches(rel, ignore_pats):
                    del dirnames[i]
                    continue
            i += 1
        rel = Path(dirpath_str).relative_to(root)
        if str(rel) != ".":
            dirs.add(str(rel).replace(os.sep, "/"))
    return dirs
