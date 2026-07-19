""".gitignore / .okfignore / .okf-exclude parsing and matching for okf.

Ignores gitignore-format patterns from .gitignore, .okfignore, and .okf-exclude
files in the source root. Last-matching-pattern-wins semantics.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

log = logging.getLogger("okf_ignore")

IGNORE_FILENAMES = (".gitignore", ".okfignore", ".okf-exclude")

# Each pattern is stored as (compiled_regex, negate, dir_only)
Pattern = tuple[re.Pattern, bool, bool]


def _glob_to_regex(pattern: str) -> str:
    """Convert gitignore glob pattern to a regex string."""
    i, n, parts = 0, len(pattern), []
    while i < n:
        c = pattern[i]
        if c == "*" and i + 1 < n and pattern[i + 1] == "*":
            parts.append(".*")
            i += 2
            if i < n and pattern[i] == "/":
                i += 1
        elif c == "*":
            parts.append("[^/]*")
            i += 1
        elif c == "?":
            parts.append("[^/]")
            i += 1
        elif c == "[":
            j = pattern.find("]", i + 1)
            if j == -1:
                parts.append("\\" + c)
                i += 1
            else:
                parts.append(pattern[i:j + 1])
                i = j + 1
        elif c in ".+^${}()|\\":
            parts.append("\\" + c)
            i += 1
        else:
            parts.append(re.escape(c))
            i += 1
    return "".join(parts)


def _parse_line(raw: str) -> tuple[str, bool, bool] | None:
    line = raw.strip()
    if not line or line.startswith("#"):
        return None
    negate = line.startswith("!")
    if negate:
        line = line[1:]
    dir_only = line.endswith("/")
    if dir_only:
        line = line.rstrip("/")
    if line.startswith("./"):
        line = line[2:]
    return (line, negate, dir_only)


def _compile(pattern: str, dir_only: bool) -> re.Pattern:
    anchored_at_root = pattern.startswith("/")
    if anchored_at_root:
        pattern = pattern[1:]
    anchored = "/" in pattern or anchored_at_root
    inner = _glob_to_regex(pattern)
    if anchored:
        if dir_only:
            return re.compile(f"^{inner}(/.*)?$")
        return re.compile(f"^{inner}$")
    if dir_only:
        return re.compile(f"(^|/){inner}(/.*)?$")
    return re.compile(f"(^|/){inner}$")


def _load_file(path: Path) -> list[Pattern]:
    if not path.exists():
        return []
    out: list[Pattern] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            r = _parse_line(line)
            if r is None:
                continue
            raw, neg, dir_only = r
            if not raw:
                continue
            try:
                out.append((_compile(raw, dir_only), neg, dir_only))
            except re.error:
                log.debug(f"Bad pattern in {path.name}: {raw!r}")
    except Exception as e:
        log.warning(f"Failed to read {path}: {e}")
    return out


def load_patterns(root: Path) -> list[Pattern]:
    pats: list[Pattern] = []
    for fname in IGNORE_FILENAMES:
        pats.extend(_load_file(root / fname))
    return pats


def matches(rel: str | Path, patterns: list[Pattern]) -> bool:
    """Return True if *rel* should be ignored (last-match-wins)."""
    if not patterns:
        return False
    s = str(rel).replace("\\", "/")
    ignored = False
    for regex, negate, _dir_only in patterns:
        if regex.search(s):
            ignored = not negate
    return ignored
