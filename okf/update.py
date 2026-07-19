"""okf update — Incremental bundle generation.

Usage:
    okf update                          # incremental
    okf update --force                  # full re-scan (same as generate)
    okf update --enrich                 # + re-enrich changed concepts
    okf update --watch                  # continuous file watcher

Pipeline:
    1. Read .okf-manifest.json
    2. Walk source tree, diff against manifest
    3. Parse only NEW + CHANGED files
    4. Remove deleted concepts from pool
    5. Full re-link
    6. Render-diff (hash compare, zero disk I/O)
    7. Write dirty concepts + affected indexes
    8. Prune orphaned .md files
    9. Always write SUMMARY.md, root index.md, log.md
    10. Write manifest LAST (crash guard)
"""

from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from okf.parsers.base import Concept

log = logging.getLogger("okf_update")


# ---------------------------------------------------------------------------
# Load existing concepts from on-disk bundle
# ---------------------------------------------------------------------------

def _concept_output_path(concept_id: str, bundle_dir: Path) -> Path:
    """Map concept_id to .md path in the bundle."""
    return bundle_dir.joinpath(*concept_id.split("/")).with_suffix(".md")


def _load_concepts_from_bundle(bundle_dir: Path) -> dict[str, Concept]:
    """Load all existing concept.md files from bundle into {concept_id: Concept}.

    Skips reserved files (index.md, log.md, SUMMARY.md).
    """
    from okf.pairs import parse_okf_file
    reserved = {"index.md", "log.md", "SUMMARY.md"}
    pool: dict[str, Concept] = {}
    for md_file in sorted(bundle_dir.rglob("*.md")):
        if md_file.name in reserved:
            continue
        raw = parse_okf_file(md_file)
        if raw is None:
            continue
        if raw["type"] in {"Index", "Log"}:
            continue
        rel = md_file.relative_to(bundle_dir)
        cid = str(rel.with_suffix("")).replace(os.sep, "/")
        s = raw.get("sections", {})
        full_body = raw.get("body", "")
        source_lines = _parse_source_range(s.get("source", ""))
        # Parse relationships from the combined ## Relationships table (v0.2).
        # Individual ## Calls / ## Called By / ## Related sections also work
        # as backward-compat fallback.
        rels = s.get("relationships", "")
        calls, called_by, related = _parse_relationships_table(rels)
        if not calls:
            calls = _parse_list_section(s.get("calls", ""))
        if not called_by:
            called_by = _parse_list_section(s.get("called by", ""))
        if not related:
            related = _parse_list_section(s.get("related", ""))
        body_extra = _parse_dependency_body_extra(full_body, s) if raw["type"] == "Dependency" else {}
        c = Concept(
            type=raw["type"],
            title=raw["title"],
            description=raw.get("description", ""),
            resource=raw.get("resource", ""),
            tags=raw.get("tags", []),
            timestamp=raw.get("timestamp", ""),
            signature=s.get("signature", ""),
            docstring=s.get("docstring", ""),
            params=_parse_params_table(s.get("parameters", "")),
            returns=s.get("returns", "").strip("`").strip(),
            source_lines=source_lines,
            concept_id=cid,
            methods=[],
            calls_raw=[],
            calls=list(calls),
            called_by=list(called_by),
            related=list(related),
            related_semantic=_parse_list_section(s.get("semantic related", "")),
            status=raw.get("status", ""),
            usage_example=s.get("usage example", ""),
            side_effects=s.get("side effects", ""),
            security=s.get("security", ""),
            complexity=s.get("complexity", ""),
            body_extra=body_extra,
        )
        pool[cid] = c
    return pool


def _parse_source_range(text: str) -> tuple:
    """Parse 'Line 42-67' or '42-67' into (42, 67)."""
    if not text:
        return ()
    m = re.search(r"(\d+)\s*[-–—]+\s*(\d+)", text)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return ()


def _parse_params_table(text: str) -> list[dict]:
    """Parse a markdown table of parameters into list of dicts."""
    if not text:
        return []
    params = []
    for line in text.splitlines():
        if "|" not in line or "---" in line or "Name" in line:
            continue
        parts = [p.strip().strip("`") for p in line.split("|")]
        if len(parts) >= 4:
            params.append({"name": parts[1], "annotation": parts[2], "default": parts[3]})
    return params


def _parse_list_section(text: str) -> list[str]:
    """Parse a markdown list into a list of strings (concept IDs)."""
    if not text:
        return []
    ids = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- [") or line.startswith("- "):
            m = re.search(r"\(/([^)]+)\.md\)", line)
            if m:
                ids.append(m.group(1))
            else:
                ids.append(line.lstrip("- ").strip())
    return ids


def _parse_relationships_table(text: str) -> tuple[list[str], list[str], list[str]]:
    """Parse the v0.2 ``## Relationships`` markdown table.

    Returns (calls, called_by, related) lists of concept IDs extracted
    from the ``| Type | Target |`` rows.
    """
    if not text or "| Type | Target |" not in text:
        return [], [], []
    calls: list[str] = []
    called_by: list[str] = []
    related: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.startswith("| Type") or stripped.startswith("|---"):
            continue
        parts = [p.strip() for p in stripped.split("|") if p.strip()]
        if len(parts) >= 2:
            rtype = parts[0].strip()
            target = parts[1].strip()
            # Extract concept_id from link [label](/concept_id.md)
            m = re.search(r"\(/([^)]+)\.md\)", target)
            cid = m.group(1) if m else target.strip("`")
            if rtype == "calls":
                calls.append(cid)
            elif rtype == "called_by":
                called_by.append(cid)
            elif rtype in ("related", "related (AI)"):
                related.append(cid)
    return calls, called_by, related


def _parse_dependency_body_extra(full_body: str, sections: dict[str, str]) -> dict:
    """Reconstruct body_extra from rendered Dependency markdown.

    The Dependency renderer outputs a table at the top of the body (before
    any ## section heading). ``sections`` only captures content after the
    first heading, so we parse the table from ``full_body`` directly.
    """
    extra: dict = {}
    in_table = False
    for line in full_body.splitlines():
        stripped = line.strip()
        if stripped.startswith("| Field | Value |"):
            in_table = True
            continue
        if stripped.startswith("|---"):
            continue
        if in_table:
            if not stripped.startswith("|") or stripped.startswith("| Used by"):
                if stripped.startswith("| Used by"):
                    break
                continue
            parts = [p.strip().strip("`") for p in stripped.split("|") if p.strip()]
            if len(parts) >= 2:
                key = parts[0].strip().lower().replace(" ", "_")
                val = parts[1].strip()
                if key == "ecosystem":
                    extra["ecosystem"] = val
                elif key == "version_constraint":
                    extra["version_constraint"] = val
                elif key == "source_manifest":
                    extra["source_manifest"] = val
                elif key == "dev_dependency":
                    extra["dev_dependency"] = val.lower() == "yes"
    # Parse used_by from the Used By section (which IS captured by sections)
    ub = sections.get("used by", "")
    if ub:
        extra["used_by"] = _parse_list_section(ub)
    return extra


# ---------------------------------------------------------------------------
# Scan + parse new/changed files
# ---------------------------------------------------------------------------

def _get_parser_for(ext: str):
    """Get parser for a file extension."""
    from okf.parsers import get_parser
    return get_parser(ext.lower())


def _parse_file(path: Path, source_root: Path, parser, exclude: set[str] | None = None) -> list[Concept]:
    """Parse a single file and return its concepts with updated tags.

    Handles both code files (via parser) and manifest files.
    """
    from okf.generator import _git_info, _make_tags
    git = _git_info(source_root)

    import okf.manifest_scanner as manifest_scanner
    if manifest_scanner.is_manifest_file(path):
        concepts = []
        try:
            raw_deps = manifest_scanner.scan_manifest(path, source_root)
            for d in raw_deps:
                base = _make_tags(language="manifest", resource=d["resource"],
                                  concept_type=d["type"], git=git)
                existing = set(d.get("tags", []))
                merged = list(dict.fromkeys(base + [t for t in existing if not t.startswith(("lang:", "type:", "module:", "domain:", "git:"))]))
                c = Concept(
                    type=d["type"], title=d["title"],
                    description=d["description"], resource=d["resource"],
                    tags=merged,
                    timestamp=d["timestamp"], concept_id=d["concept_id"],
                    body_extra=d.get("body_extra", {}),
                )
                concepts.append(c)
        except Exception as e:
            log.warning(f"Failed to parse manifest {path}: {e}")
        return concepts

    concepts = []
    try:
        file_concepts = parser.parse_file(path, source_root)
        for c in file_concepts:
            c.tags = _make_tags(
                language=parser.LANGUAGE,
                resource=c.resource,
                concept_type=c.type,
                git=git,
            )
        concepts.extend(file_concepts)
    except Exception as e:
        log.warning(f"Failed to parse {path}: {e}")
    return concepts


def _walk_source_dirs(source_root: Path, exclude: set[str] | None = None) -> set[str]:
    exclude = exclude or set()
    from okf.ignore import load_patterns, matches
    ignore_pats = load_patterns(source_root)
    dirs: set[str] = set()
    for path in sorted(source_root.rglob("*")):
        if not path.is_dir():
            continue
        rel = path.relative_to(source_root)
        parts = rel.parts
        if any(part in exclude for part in parts):
            continue
        if matches(rel, ignore_pats):
            continue
        if any(part.startswith(".") for part in parts):
            continue
        from okf.parsers.base import SKIP_DIRS, SKIP_DIR_SUFFIXES
        if any(part in SKIP_DIRS for part in parts):
            continue
        if any(part.endswith(sfx) for sfx in SKIP_DIR_SUFFIXES for part in parts):
            continue
        dirs.add(str(rel).replace(os.sep, "/"))
    return dirs


# ---------------------------------------------------------------------------
# Render-diff helpers
# ---------------------------------------------------------------------------

def _render_concept_safe(concept: Concept, all_map: dict[str, Concept]) -> str:
    """Render a concept's .md content. Sets timestamp from resource file mtime."""
    from okf.generator import render_concept
    return render_concept(concept, all_map)


def _compute_render_hash(content: str) -> str:
    """SHA256 of rendered .md content."""
    from okf.manifest import compute_content_hash
    return compute_content_hash(content)


def _find_dirty_dirs(concept_ids: set[str]) -> set[str]:
    """Given a set of concept_ids, return all ancestor directories.

    E.g. {'StockAI/RnD/connectors/MyClass'} -> {'', 'StockAI', 'StockAI/RnD',
    'StockAI/RnD/connectors'}
    """
    dirs: set[str] = set()
    for cid in concept_ids:
        parts = cid.split("/")[:-1]  # drop concept name, keep directory
        for i in range(len(parts) + 1):
            dirs.add("/".join(parts[:i]))
    return dirs


# ---------------------------------------------------------------------------
# Bundle name helper
# ---------------------------------------------------------------------------

def _detect_bundle_name(source_root: Path) -> str:
    """Derive bundle name from source root directory name."""
    return source_root.resolve().name


# ---------------------------------------------------------------------------
# Main update entry point
# ---------------------------------------------------------------------------

def update_bundle(
    source_root: Path,
    bundle_dir: Path,
    exclude: set[str] | None = None,
    force: bool = False,
    enable_enrich: bool = False,
) -> int:
    """Run incremental bundle update.

    Returns number of dirty concepts written (0 if nothing changed).
    """
    from okf.manifest import (
        Manifest, read_manifest, write_manifest,
        diff_source, compute_file_hash, walk_source_files,
    )
    from okf.linker import link_all

    source_root = source_root.resolve()
    bundle_dir = bundle_dir.resolve()
    exclude = exclude or set()

    # ── Step 1: Read manifest ──────────────────────────────────────────────
    manifest = None if force else read_manifest(bundle_dir)
    if manifest is None:
        if force:
            log.info("Force mode: full re-scan")
        else:
            log.info("No manifest found — full scan required")

    # ── Step 2: Diff source tree ───────────────────────────────────────────
    changeset = diff_source(source_root, manifest, exclude)
    if not changeset.has_changes and manifest is not None:
        log.info("No changes detected — bundle is up to date")
        return 0

    # If manifest exists but this is the first update (no manifest.concepts populated),
    # treat as full scan to reconstruct manifest
    if manifest is None or not manifest.concepts:
        log.info("Full scan required: no concept state in manifest")

    # ── Step 3: Build or update concept pool ────────────────────────────────
    if manifest is not None:
        # Warm start: load existing concepts from disk
        pool = _load_concepts_from_bundle(bundle_dir)
        log.info(f"Loaded {len(pool)} existing concepts from bundle")
    else:
        pool = {}

    # Parse new + changed files
    new_concepts_parsed = 0
    for rel_path in changeset.parse_files:
        full_path = source_root / rel_path
        if not full_path.exists():
            continue
        parser = _get_parser_for(full_path.suffix)
        import okf.manifest_scanner as manifest_scanner
        if parser is None and not manifest_scanner.is_manifest_file(full_path):
            continue
        # Remove stale concepts from pool (for changed files)
        if manifest and not force:
            old_rel = str(rel_path).replace(os.sep, "/")
            if old_rel in manifest.files:
                for old_cid in manifest.files[old_rel].concept_ids:
                    pool.pop(old_cid, None)
        # Parse
        concepts = _parse_file(full_path, source_root, parser, exclude)
        for c in concepts:
            # Apply rename migration if applicable
            if changeset.rename_map:
                old_cid = c.concept_id
                if old_cid in changeset.rename_map:
                    c.concept_id = changeset.rename_map[old_cid]
                    log.debug(f"Migrated concept_id: {old_cid} -> {c.concept_id}")
            pool[c.concept_id] = c
            new_concepts_parsed += 1

    # Remove genuinely deleted concepts from pool (files that no longer exist).
    # Concept IDs from changed files are already removed and re-parsed above —
    # do NOT pop them again or the freshly-parsed concepts get wiped.
    re_parsed_ids: set[str] = set()
    if manifest:
        for rel_path in changeset.parse_files:
            old_rel = str(rel_path).replace(os.sep, "/")
            if old_rel in manifest.files:
                re_parsed_ids.update(manifest.files[old_rel].concept_ids)
    for cid in changeset.deleted_ids:
        if cid not in re_parsed_ids:
            pool.pop(cid, None)

    log.info(f"Parsed {new_concepts_parsed} new/changed concepts; pool size: {len(pool)}")

    if not pool:
        log.warning("No concepts in pool after update — bundle will be empty")
        return 0

    # Deduplicate concept IDs (same as generator._dedup_concept_ids).
    # Multiple source files can produce the same concept_id (e.g., two
    # requirements.txt both expressing a dependency on `rich`).
    from okf.generator import _dedup_concept_ids
    all_concepts = list(pool.values())
    all_concepts = _dedup_concept_ids(all_concepts)
    pool = {c.concept_id: c for c in all_concepts}

    # ── Step 4: Full re-link ────────────────────────────────────────────────
    log.info("Relinking concept pool...")
    stats = link_all(all_concepts)
    log.info(stats.summary_line())
    all_map: dict[str, Concept] = {c.concept_id: c for c in all_concepts}

    # ── Step 5: Edge-diff ─────────────────────────────────────────────────────
    bundle_okf_version = "0.2"

    # Initialize manifest if needed
    if manifest is None:
        ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        manifest = Manifest(
            okf_version=bundle_okf_version,
            source_root=str(source_root),
            generated_at=ts,
        )

    # Mark concepts from changed/new files as dirty (they were re-parsed).
    dirty_ids: set[str] = set(changeset.deleted_ids)
    for rel_path in changeset.parse_files:
        rel_str = str(rel_path).replace(os.sep, "/")
        if manifest and rel_str in manifest.files:
            dirty_ids.update(manifest.files[rel_str].concept_ids)

    # After re-linking, compare edges (calls, called_by, related) against
    # manifest. If edges changed, the concept's Relationships table changed
    # and it must be re-rendered. This catches edge cascades (e.g. A edited
    # to call B → B's called_by changes) without re-rendering every concept.
    for c in all_concepts:
        old_cs = manifest.concepts.get(c.concept_id)
        new_edge_hash = _compute_edge_hash(c)
        old_edge_hash = old_cs.edge_hash if old_cs else ""
        if new_edge_hash != old_edge_hash:
            dirty_ids.add(c.concept_id)
        # Update manifest concept state for the write phase
        if c.concept_id not in manifest.concepts:
            manifest.concepts[c.concept_id] = _make_concept_state(c)
        manifest.concepts[c.concept_id].edge_hash = new_edge_hash
        manifest.concepts[c.concept_id].render_hash = "stale"  # will be set on write

    # ── Step 6: Write dirty concepts ───────────────────────────────────────
    bundle_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for c in all_concepts:
        if c.concept_id in dirty_ids:
            out_path = _concept_output_path(c.concept_id, bundle_dir)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            content = _render_concept_safe(c, all_map)
            _atomic_write(out_path, content)
            written += 1

    log.info(f"Written {written} dirty concept files")

    # ── Step 7: Prune orphan .md files (deleted + renamed old paths) ────────
    # Only remove files that are NOT in the pool (i.e. genuinely deleted, not
    # re-created by parsing a changed file with the same concept_id).
    effective_deleted = set(changeset.deleted_ids) - set(pool.keys())
    for old_cid in changeset.rename_map:
        effective_deleted.discard(changeset.rename_map[old_cid])
    pruned = 0
    for cid in effective_deleted:
        orphan = _concept_output_path(cid, bundle_dir)
        if orphan.exists():
            orphan.unlink()
            pruned += 1
    for old_cid in changeset.rename_map:
        orphan = _concept_output_path(old_cid, bundle_dir)
        if orphan.exists():
            orphan.unlink()
            pruned += 1
    if pruned:
        log.info(f"Pruned {pruned} orphaned concept files")

    # ── Step 7b: Clean up any .md files not in the manifest ─────────────────
    # This handles orphaned files from dedup changes (e.g. `generate` produced
    # `click` + `click_1` but `update` only wrote `click`).
    reserved_names = {"index.md", "log.md", "SUMMARY.md"}
    manifest_concept_ids = set(manifest.concepts.keys())
    cleaned = 0
    for md_file in sorted(bundle_dir.rglob("*.md")):
        if md_file.name in reserved_names:
            continue
        rel = md_file.relative_to(bundle_dir)
        cid = str(rel.with_suffix("")).replace(os.sep, "/")
        if cid not in manifest_concept_ids:
            md_file.unlink()
            cleaned += 1
    if cleaned:
        log.info(f"Cleaned {cleaned} stale concept files not in manifest")

    # ── Step 8: Build directory tree & write dirty indexes ──────────────────
    all_dirty = dirty_ids | changeset.deleted_ids | set(changeset.rename_map.keys())
    dirty_dirs = _find_dirty_dirs(all_dirty)

    # Build full directory tree from concept pool
    dir_tree = _build_dir_tree(all_concepts, bundle_dir, source_root, exclude)

    # Write dirty index files
    for rel_dir in sorted(dirty_dirs, key=len):
        node = dir_tree.get(rel_dir)
        if node is None:
            node = {"subdirs": set(), "concepts": []}
            dir_tree[rel_dir] = node
        index_content = _render_dir_index(rel_dir, node["subdirs"], node["concepts"])
        dir_path = bundle_dir / rel_dir if rel_dir else bundle_dir
        dir_path.mkdir(parents=True, exist_ok=True)
        (dir_path / "index.md").write_text(index_content, encoding="utf-8")

    # ── Step 9: Always write root index, SUMMARY.md, log.md ─────────────────
    _write_root_index(bundle_dir, dir_tree, all_concepts)
    _write_summary(bundle_dir, all_concepts, source_root)
    _write_log(bundle_dir, new_concepts_parsed, len(all_concepts))

    # ── Step 10: Update manifest file states ────────────────────────────────
    # Build from concept pool first (resource → concept_ids)
    new_file_states: dict[str, dict] = {}
    for c in all_concepts:
        rel = c.resource.replace(os.sep, "/")
        if not rel:
            continue
        if rel not in new_file_states:
            full_path = source_root / rel
            h = compute_file_hash(full_path) if full_path.exists() else ""
            mtime = full_path.stat().st_mtime_ns if full_path.exists() else 0
            new_file_states[rel] = {
                "path": rel, "mtime_ns": mtime, "hash": h, "concept_ids": []
            }
        if c.concept_id not in new_file_states[rel]["concept_ids"]:
            new_file_states[rel]["concept_ids"].append(c.concept_id)

    # Merge with all known source files (ensures files whose concepts were
    # dedup'd away still appear in the manifest, preventing false diffs).
    for rel_path in walk_source_files(source_root, exclude):
        rel_str = str(rel_path).replace(os.sep, "/")
        if rel_str not in new_file_states:
            full_path = source_root / rel_path
            h = compute_file_hash(full_path) if full_path.exists() else ""
            mtime = full_path.stat().st_mtime_ns if full_path.exists() else 0
            new_file_states[rel_str] = {
                "path": rel_str, "mtime_ns": mtime, "hash": h, "concept_ids": []
            }

    manifest.files = {}
    for k, v in new_file_states.items():
        from okf.manifest import FileState
        manifest.files[k] = FileState(**v)

    manifest.source_root = str(source_root)

    # ── Step 11: Write manifest LAST ────────────────────────────────────────
    write_manifest(bundle_dir, manifest)
    log.info(f"Manifest written -> {bundle_dir / '.okf-manifest.json'}")

    return written


# ---------------------------------------------------------------------------
# Directory tree builder
# ---------------------------------------------------------------------------

def _build_dir_tree(
    concepts: list[Concept],
    bundle_dir: Path,
    source_root: Path,
    exclude: set[str] | None = None,
) -> dict[str, dict]:
    """Build {dir_relpath: {'subdirs': set, 'concepts': list}} from concept pool."""
    dir_tree: dict[str, dict] = {}

    def _ensure(rel: str):
        if rel not in dir_tree:
            dir_tree[rel] = {"subdirs": set(), "concepts": []}

    def _register_ancestors(rel_dir: str):
        parts = rel_dir.split("/") if rel_dir else []
        for i in range(len(parts)):
            parent = "/".join(parts[:i]) if i > 0 else ""
            child = "/".join(parts[:i + 1])
            _ensure(parent)
            _ensure(child)
            dir_tree[parent]["subdirs"].add(child)

    for c in concepts:
        out_path = _concept_output_path(c.concept_id, bundle_dir)
        rel_dir = str(out_path.parent.relative_to(bundle_dir)).replace(os.sep, "/")
        if rel_dir == ".":
            rel_dir = ""
        _ensure(rel_dir)
        dir_tree[rel_dir]["concepts"].append(c)
        _register_ancestors(rel_dir)

    # Register source dirs (for empty directories)
    source_dirs = _walk_source_dirs(source_root, exclude)
    for rel_dir in source_dirs:
        rel_dir = rel_dir.replace(os.sep, "/")
        _ensure(rel_dir)
        _register_ancestors(rel_dir)

    return dir_tree


# ---------------------------------------------------------------------------
# Render helpers (thin wrappers around generator.py)
# ---------------------------------------------------------------------------

def _render_dir_index(dir_path: str, subdirs: set[str], concepts: list[Concept]) -> str:
    from okf.generator import render_dir_index
    # Build all_map from concepts
    all_map = {c.concept_id: c for c in concepts}
    return render_dir_index(dir_path, list(subdirs), concepts, "", all_map)


def _write_root_index(bundle_dir: Path, dir_tree: dict, concepts: list[Concept]):
    from okf.generator import render_root_index
    top_dirs = sorted(dir_tree.get("", {}).get("subdirs", set()))
    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    bundle_name = bundle_dir.resolve().name
    content = render_root_index(bundle_name, top_dirs, len(concepts), ts)
    (bundle_dir / "index.md").write_text(content, encoding="utf-8")


def _write_summary(bundle_dir: Path, concepts: list[Concept], source_root: Path):
    from okf.generator import _git_info
    from okf.generator import render_summary
    bundle_name = bundle_dir.resolve().name
    git = _git_info(source_root)
    content = render_summary(bundle_name, concepts, bundle_dir, git)
    (bundle_dir / "SUMMARY.md").write_text(content, encoding="utf-8")


def _write_log(bundle_dir: Path, new_count: int, total: int):
    from okf.generator import render_log
    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries = [
        f"{ts} — Incremental update: {new_count} new/changed, {total} total concepts",
    ]
    # Read existing log entries and append
    existing_entries = []
    log_path = bundle_dir / "log.md"
    if log_path.exists():
        try:
            raw = log_path.read_text(encoding="utf-8")
            parts = raw.split("---", 2)
            if len(parts) >= 3:
                body = parts[2].strip()
                existing_entries = [line.strip("- ") for line in body.splitlines() if line.strip().startswith("- ")]
        except Exception:
            pass
    all_entries = existing_entries + entries
    content = render_log(all_entries)
    log_path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _atomic_write(path: Path, content: str):
    """Write file atomically (write to tmp, rename)."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def _compute_edge_hash(concept: Concept) -> str:
    """SHA256 of sorted edges — detects any change to the Relationships table."""
    from okf.manifest import compute_content_hash
    edges = sorted(concept.calls) + sorted(concept.called_by) + sorted(concept.related)
    return compute_content_hash("\0".join(edges))


def _make_concept_state(concept: Concept):
    """Build a ConceptState from a Concept dataclass."""
    from okf.manifest import ConceptState
    return ConceptState(
        concept_id=concept.concept_id,
        type=concept.type,
        resource=concept.resource,
        render_hash="",
        edge_hash=_compute_edge_hash(concept),
        enriched=False,
    )
