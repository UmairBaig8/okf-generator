"""Manifest model & change detection for okf update.

Stores file-level metadata (path, mtime_ns, SHA256 hash, concept_ids)
and per-concept metadata (render_hash, type, resource, enriched status)
so that ``okf update`` can detect what changed without re-scanning
every file.

Manifest is written atomically LAST — after all .md writes succeed.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("okf_manifest")

MANIFEST_VERSION = 2
MANIFEST_FILENAME = ".okf-manifest.json"

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class FileState:
    path: str                 # relpath from source_root
    mtime_ns: int
    hash: str                 # SHA256 hex of source file content
    concept_ids: list[str]    # concept_ids derived from this file


@dataclass
class ConceptState:
    concept_id: str
    type: str
    resource: str             # source file relpath
    render_hash: str          # SHA256 of rendered .md output
    edge_hash: str            # SHA256 of sorted(calls + called_by + related)
    enriched: bool            # has LLM enrichment been applied?


@dataclass
class Manifest:
    okf_version: str
    manifest_version: int = MANIFEST_VERSION
    source_root: str = ""
    files: dict[str, FileState] = field(default_factory=dict)
    concepts: dict[str, ConceptState] = field(default_factory=dict)
    generated_at: str = ""


@dataclass
class Changeset:
    new_files: set[Path] = field(default_factory=set)
    changed_files: set[Path] = field(default_factory=set)
    deleted_ids: set[str] = field(default_factory=set)
    skipped_files: set[Path] = field(default_factory=set)
    rename_map: dict[str, str] = field(default_factory=dict)  # old_concept_id -> new_concept_id

    @property
    def has_changes(self) -> bool:
        return bool(self.new_files or self.changed_files or self.deleted_ids)

    @property
    def parse_files(self) -> set[Path]:
        return self.new_files | self.changed_files


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def compute_file_hash(path: Path) -> str:
    """SHA256 hex of file content. Reads in 64 KiB chunks."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
    except Exception as e:
        log.warning(f"Failed to hash {path}: {e}")
        return ""
    return h.hexdigest()


def compute_content_hash(content: str | bytes) -> str:
    """SHA256 of a string or bytes."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


# ---------------------------------------------------------------------------
# Manifest I/O
# ---------------------------------------------------------------------------

def manifest_path(bundle_dir: Path) -> Path:
    return bundle_dir / MANIFEST_FILENAME


def read_manifest(bundle_dir: Path) -> Manifest | None:
    """Read manifest from disk. Returns None if missing/corrupt."""
    path = manifest_path(bundle_dir)
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw.get("manifest_version") != MANIFEST_VERSION:
            log.warning(f"Manifest version mismatch: got {raw.get('manifest_version')}, expected {MANIFEST_VERSION}")
            return None
        files = {}
        for k, v in raw.get("files", {}).items():
            files[k] = FileState(**v)
        concepts = {}
        for k, v in raw.get("concepts", {}).items():
            concepts[k] = ConceptState(**v)
        return Manifest(
            okf_version=raw.get("okf_version", ""),
            manifest_version=raw.get("manifest_version", MANIFEST_VERSION),
            source_root=raw.get("source_root", ""),
            files=files,
            concepts=concepts,
            generated_at=raw.get("generated_at", ""),
        )
    except Exception as e:
        log.warning(f"Failed to read manifest: {e}")
        return None


def write_manifest(bundle_dir: Path, manifest: Manifest):
    """Write manifest atomically (write to tmp, rename)."""
    path = manifest_path(bundle_dir)
    manifest.generated_at = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    raw = _manifest_to_dict(manifest)
    tmp = path.with_suffix(".tmp.json")
    tmp.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _manifest_to_dict(m: Manifest) -> dict:
    files = {k: asdict(v) for k, v in m.files.items()}
    concepts = {k: asdict(v) for k, v in m.concepts.items()}
    return {
        "okf_version": m.okf_version,
        "manifest_version": m.manifest_version,
        "source_root": m.source_root,
        "files": files,
        "concepts": concepts,
        "generated_at": m.generated_at,
    }


# ---------------------------------------------------------------------------
# Source tree walk helpers
# ---------------------------------------------------------------------------

def _should_skip(rel_path: Path, exclude: set[str]) -> bool:
    """Check if a path should be skipped based on exclude patterns and hidden dirs."""
    parts = rel_path.parts
    # User-specified exclude patterns (e.g. --exclude tests)
    if any(part in exclude for part in parts):
        return True
    # Non-manifest files: skip hidden dirs/vendor dirs
    if any(part.startswith(".") for part in parts):
        return True
    from okf.parsers.base import SKIP_DIRS, SKIP_DIR_SUFFIXES
    if any(part in SKIP_DIRS for part in parts):
        return True
    if any(part.endswith(sfx) for sfx in SKIP_DIR_SUFFIXES for part in parts):
        return True
    return False


def walk_source_files(source_root: Path, exclude: set[str] | None = None) -> dict[Path, str]:
    """Walk source tree and return {relpath: sha256_hash} for all parseable files."""
    exclude = exclude or set()
    result: dict[Path, str] = {}
    from okf.parsers import get_parser
    import okf.manifest_scanner as manifest_scanner

    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(source_root)
        if _should_skip(rel, exclude):
            continue
        # Check manifests first
        if manifest_scanner.is_manifest_file(path):
            result[rel] = compute_file_hash(path)
            continue
        # Then check for a language parser
        if get_parser(path.suffix.lower()) is not None:
            result[rel] = compute_file_hash(path)
    return result


# ---------------------------------------------------------------------------
# Change detection
# ---------------------------------------------------------------------------

def _build_hash_index(manifest: Manifest) -> dict[str, list[str]]:
    """Build {content_hash: [relpath, ...]} from manifest files."""
    idx: dict[str, list[str]] = {}
    for fpath, fstate in manifest.files.items():
        if fstate.hash:
            idx.setdefault(fstate.hash, []).append(fpath)
    return idx


def _path_similarity(a: str, b: str) -> int:
    """Count common path segments between two relative paths."""
    pa = set(a.replace("\\", "/").split("/"))
    pb = set(b.replace("\\", "/").split("/"))
    return len(pa & pb)


def diff_source(source_root: Path, manifest: Manifest | None,
                exclude: set[str] | None = None) -> Changeset:
    """Compare source tree against manifest and return a Changeset.

    Handles rename detection via content-hash index.
    """
    exclude = exclude or set()
    changeset = Changeset()

    if manifest is None:
        # No manifest — everything is new
        files = walk_source_files(source_root, exclude)
        changeset.new_files = set(files.keys())
        return changeset

    current = walk_source_files(source_root, exclude)

    # Build hash index from manifest for rename detection
    hash_index = _build_hash_index(manifest)

    # Normalize to string keys for comparison
    manifest_files = set(manifest.files.keys())
    current_files = {str(k).replace(os.sep, "/") for k in current.keys()}

    # Deleted: in manifest but not on disk
    for f in manifest_files - current_files:
        for cid in manifest.files[f].concept_ids:
            changeset.deleted_ids.add(cid)

    # Build str→hash lookup from current results (for diffing)
    current_str_map: dict[str, str] = {str(k).replace(os.sep, "/"): v for k, v in current.items()}

    # New: on disk but not in manifest
    for f_str in sorted(current_files - manifest_files):
        h = current_str_map.get(f_str, "")
        f_path = Path(f_str.replace("/", os.sep))
        if h and h in hash_index:
            # Possible rename — check candidates
            candidates = hash_index[h]
            if len(candidates) == 1:
                old_path = candidates[0]
                changeset.new_files.add(f_path)
                # Carry over concept_ids from old path
                for old_cid in manifest.files[old_path].concept_ids:
                    new_cid = _migrate_concept_id(old_cid, old_path, f_path)
                    changeset.rename_map[old_cid] = new_cid
                    changeset.deleted_ids.discard(old_cid)
                log.info(f"Rename detected: {old_path} -> {f_str} (hash match)")
            else:
                # Ambiguous — pick closest path match
                best = max(candidates, key=lambda c: _path_similarity(c, f_str))
                if _path_similarity(best, f_str) > 0:
                    changeset.new_files.add(f_path)
                    for old_cid in manifest.files[best].concept_ids:
                        new_cid = _migrate_concept_id(old_cid, best, f_path)
                        changeset.rename_map[old_cid] = new_cid
                        changeset.deleted_ids.discard(old_cid)
                    log.info(f"Rename detected (ambiguous, best guess): {best} -> {f_str}")
                else:
                    changeset.new_files.add(f_path)
        else:
            changeset.new_files.add(f_path)

    # Changed: mtime differs, confirm with hash
    for f_str in manifest_files & current_files:
        manifest_state = manifest.files[f_str]
        current_hash = current_str_map.get(f_str, "")
        if not current_hash:
            continue  # not a parseable file anymore
        if manifest_state.hash != current_hash:
            changeset.changed_files.add(Path(f_str.replace("/", os.sep)))
            changeset.deleted_ids.update(manifest_state.concept_ids)
        else:
            changeset.skipped_files.add(Path(f_str.replace("/", os.sep)))

    return changeset


def _migrate_concept_id(old_cid: str, old_path_str: str, new_path: Path) -> str:
    """Recompute concept_id for a renamed file.

    Replaces the old file-path prefix in the concept_id with the new one.
    Concept_id format: ``<resource_without_ext>/<safe_name>``
    """
    old_stem = old_path_str.replace("\\", "/")
    if old_stem.endswith(".md"):
        old_stem = old_stem[:-3]
    new_stem = str(new_path).replace("\\", "/")
    if new_stem.endswith(".md"):
        new_stem = new_stem[:-3]
    suffix = old_cid.removeprefix(old_stem)
    return f"{new_stem}{suffix}"


# ---------------------------------------------------------------------------
# Render hash helpers (for P4)
# ---------------------------------------------------------------------------

def compute_render_hash(content: str) -> str:
    """SHA256 of rendered concept .md content.

    Used by the post-relink render-diff to determine dirtiness without
    reading the existing .md file from disk.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
