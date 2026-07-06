"""okf diff — compare two OKF bundles.

Usage:
  okf diff <old_bundle> <new_bundle>
  okf diff <old_bundle> <new_bundle> --compact
  okf diff <old_bundle> <new_bundle> --json
  okf diff <old_bundle> <new_bundle> --impact

Outputs added, removed, and changed concepts between bundle versions.
With --impact, also traces how dependency changes affect modules
and their functions/classes.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def _concept_hash(c: dict) -> str:
    """Stable hash of content fields — not concept_id or timestamps."""
    raw = json.dumps(
        {
            "description": c.get("description", ""),
            "signature": c.get("sections", {}).get("signature", ""),
            "tags": sorted(c.get("tags", [])),
            "body_extra": c.get("body_extra", {}),
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.md5(raw.encode()).hexdigest()


def diff_bundles(
    old_dir: Path,
    new_dir: Path,
    old_list: list | None = None,
    new_list: list | None = None,
) -> dict:
    """Compare two bundles and return added/removed/changed concepts.

    If old_list/new_list are provided (pre-loaded via lookup.load_bundle),
    they are used directly instead of loading from disk again.
    """
    if old_list is None or new_list is None:
        from okf.lookup import load_bundle as _load
        old_list = _load(old_dir)
        new_list = _load(new_dir)

    old_by_id: dict[str, dict] = {c["concept_id"]: c for c in old_list}
    new_by_id: dict[str, dict] = {c["concept_id"]: c for c in new_list}

    old_ids = set(old_by_id.keys())
    new_ids = set(new_by_id.keys())

    old_hashes = {cid: _concept_hash(c) for cid, c in old_by_id.items()}
    new_hashes = {cid: _concept_hash(c) for cid, c in new_by_id.items()}

    added_ids = new_ids - old_ids
    removed_ids = old_ids - new_ids
    common_ids = new_ids & old_ids
    changed_ids = {cid for cid in common_ids if old_hashes[cid] != new_hashes[cid]}

    def _brief(c: dict) -> dict:
        return {
            "concept_id": c["concept_id"],
            "type": c["type"],
            "title": c["title"],
            "resource": c.get("resource", ""),
            "description": c.get("description", ""),
        }

    added = [_brief(new_by_id[cid]) for cid in sorted(added_ids)]
    removed = [_brief(old_by_id[cid]) for cid in sorted(removed_ids)]

    changed = []
    for cid in sorted(changed_ids):
        old_c = old_by_id[cid]
        new_c = new_by_id[cid]
        entry = _brief(new_c)
        entry["changes"] = {}
        if old_c.get("description") != new_c.get("description"):
            entry["changes"]["description"] = (old_c.get("description", ""), new_c.get("description", ""))
        old_sig = old_c.get("sections", {}).get("signature", "")
        new_sig = new_c.get("sections", {}).get("signature", "")
        if old_sig != new_sig:
            entry["changes"]["signature"] = (old_sig, new_sig)
        if old_c.get("tags") != new_c.get("tags"):
            entry["changes"]["tags"] = (old_c.get("tags", []), new_c.get("tags", []))
        changed.append(entry)

    return {
        "old_path": str(old_dir),
        "new_path": str(new_dir),
        "old_count": len(old_list),
        "new_count": len(new_list),
        "added": added,
        "removed": removed,
        "changed": changed,
    }


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

DIVIDER = "─" * 60


def fmt_compact(result: dict) -> str:
    lines = [
        DIVIDER,
        "  okf diff",
        DIVIDER,
        f"  Old: {result['old_path']} ({result['old_count']} concepts)",
        f"  New: {result['new_path']} ({result['new_count']} concepts)",
        DIVIDER,
    ]
    if result["added"]:
        lines.append(f"\n  Added ({len(result['added'])}):")
        for c in result["added"][:10]:
            lines.append(f"    [+] {c['type']}: {c['title']} — {c['resource']}")
        if len(result["added"]) > 10:
            lines.append(f"    ... and {len(result['added']) - 10} more")
    if result["removed"]:
        lines.append(f"\n  Removed ({len(result['removed'])}):")
        for c in result["removed"][:10]:
            lines.append(f"    [-] {c['type']}: {c['title']} — {c['resource']}")
        if len(result["removed"]) > 10:
            lines.append(f"    ... and {len(result['removed']) - 10} more")
    if result["changed"]:
        lines.append(f"\n  Changed ({len(result['changed'])}):")
        for c in result["changed"][:10]:
            lines.append(f"    [~] {c['type']}: {c['title']} — {c['resource']}")
        if len(result["changed"]) > 10:
            lines.append(f"    ... and {len(result['changed']) - 10} more")
    lines.append(DIVIDER)
    return "\n".join(lines)


def fmt_detail(result: dict) -> str:
    lines = [
        DIVIDER,
        "  okf diff",
        DIVIDER,
        f"  Old: {result['old_path']} ({result['old_count']} concepts)",
        f"  New: {result['new_path']} ({result['new_count']} concepts)",
        DIVIDER,
    ]
    if result["added"]:
        lines.append(f"\n  Added ({len(result['added'])}):\n")
        for c in result["added"]:
            lines.append(f"    [+] {c['type']}: {c['title']}")
            lines.append(f"        resource: {c['resource']}")
            if c.get("description"):
                lines.append(f"        description: {c['description'][:80]}")
            lines.append("")
    if result["removed"]:
        lines.append(f"  Removed ({len(result['removed'])}):\n")
        for c in result["removed"]:
            lines.append(f"    [-] {c['type']}: {c['title']}")
            lines.append(f"        resource: {c['resource']}")
            lines.append("")
    if result["changed"]:
        lines.append(f"  Changed ({len(result['changed'])}):\n")
        for c in result["changed"]:
            lines.append(f"    [~] {c['type']}: {c['title']}")
            lines.append(f"        resource: {c['resource']}")
            for field, (old_val, new_val) in c.get("changes", {}).items():
                old_short = str(old_val)[:60]
                new_short = str(new_val)[:60]
                lines.append(f"        {field}:")
                lines.append(f"          - {old_short}")
                lines.append(f"          + {new_short}")
            lines.append("")
    lines.append(DIVIDER)
    return "\n".join(lines)


def fmt_json(result: dict) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Impact analysis — trace dependency changes to affected code
# ---------------------------------------------------------------------------


def _parse_used_by(concept: dict) -> list[str]:
    """Extract module concept_ids from a Dependency's ## Used By section."""
    used_by_section = concept.get("sections", {}).get("used by", "")
    if not used_by_section:
        return []
    ids = []
    for line in used_by_section.splitlines():
        m = re.search(r"\]\(/(.+?)\.md\)", line)
        if m:
            ids.append(m.group(1))
    return ids


def _get_dep_version(concept: dict) -> str:
    """Extract version constraint from a Dependency's body table."""
    body = concept.get("raw", "")
    m = re.search(r"\| Version constraint \| `([^`]+)` \|", body)
    return m.group(1) if m else ""


def _get_dep_tag(concept: dict, prefix: str) -> str:
    """Extract a tag value by prefix, e.g. 'ecosystem:' -> 'pip'."""
    for tag in concept.get("tags", []):
        if tag.startswith(prefix):
            return tag[len(prefix):]
    return ""


def _build_code_index(concepts: list[dict]) -> dict[str, list[dict]]:
    """Build {resource: [code_concepts]} for non-Dependency, non-Module concepts."""
    idx: dict[str, list[dict]] = {}
    for c in concepts:
        if c["type"] in ("Dependency", "Module"):
            continue
        res = c.get("resource", "")
        if res:
            idx.setdefault(res, []).append(c)
    return idx


def impact_analysis(
    old_list: list[dict],
    new_list: list[dict],
    diff_result: dict,
) -> dict:
    """Trace dependency changes to affected modules and code concepts.

    Returns:
        {
            "changed_deps": [
                {
                    "title": "requests",
                    "old_version": "2.31.0",
                    "new_version": "3.0.0",
                    "ecosystem": "pip",
                    "affected_modules": [
                        {
                            "concept_id": "...",
                            "title": "utils",
                            "resource": "utils.py",
                            "code_concepts": [
                                {"title": "slugify", "type": "Function"},
                                ...
                            ]
                        }
                    ]
                }
            ],
            "removed_deps": [...],
            "added_deps": [...],
        }
    """
    old_by_id = {c["concept_id"]: c for c in old_list}
    new_by_id = {c["concept_id"]: c for c in new_list}

    code_index = _build_code_index(new_list)
    module_index = {c["concept_id"]: c for c in new_list if c["type"] == "Module"}

    def _module_children(module_cid: str) -> list[dict]:
        """Find Functions/Classes under a module (same resource)."""
        mod = module_index.get(module_cid)
        if not mod:
            return []
        res = mod.get("resource", "")
        return code_index.get(res, [])

    def _trace_dep(dep_cid: str, source_concepts: list[dict]) -> list[dict]:
        """For a dep concept_id, find affected modules and their code concepts."""
        source_by_id = {c["concept_id"]: c for c in source_concepts}
        dep = source_by_id.get(dep_cid)
        if not dep:
            return []
        module_ids = _parse_used_by(dep)
        modules = []
        seen = set()
        for mid in module_ids:
            if mid in seen:
                continue
            seen.add(mid)
            mod = module_index.get(mid) or source_by_id.get(mid)
            children = _module_children(mid)
            modules.append({
                "concept_id": mid,
                "title": mod["title"] if mod else mid.split("/")[-1],
                "resource": mod.get("resource", "") if mod else "",
                "code_concepts": [
                    {"title": cc["title"], "type": cc["type"]}
                    for cc in children
                ],
            })
        return modules

    # --- Changed deps ---
    changed_deps = []
    for c_entry in diff_result.get("changed", []):
        if c_entry["type"] != "Dependency":
            continue
        cid = c_entry["concept_id"]
        old_dep = old_by_id.get(cid)
        new_dep = new_by_id.get(cid)
        modules = _trace_dep(cid, new_list)
        changed_deps.append({
            "title": c_entry["title"],
            "concept_id": cid,
            "ecosystem": _get_dep_tag(new_dep or old_dep or {}, "ecosystem:"),
            "old_version": _get_dep_version(old_dep) if old_dep else "",
            "new_version": _get_dep_version(new_dep) if new_dep else "",
            "affected_modules": modules,
            "total_modules": len(modules),
            "total_code_concepts": sum(len(m["code_concepts"]) for m in modules),
        })

    # --- Removed deps ---
    removed_deps = []
    for c_entry in diff_result.get("removed", []):
        if c_entry["type"] != "Dependency":
            continue
        cid = c_entry["concept_id"]
        old_dep = old_by_id.get(cid)
        modules = _trace_dep(cid, old_list)
        removed_deps.append({
            "title": c_entry["title"],
            "concept_id": cid,
            "ecosystem": _get_dep_tag(old_dep or {}, "ecosystem:"),
            "old_version": _get_dep_version(old_dep) if old_dep else "",
            "affected_modules": modules,
            "total_modules": len(modules),
            "total_code_concepts": sum(len(m["code_concepts"]) for m in modules),
        })

    # --- Added deps ---
    added_deps = []
    for c_entry in diff_result.get("added", []):
        if c_entry["type"] != "Dependency":
            continue
        cid = c_entry["concept_id"]
        new_dep = new_by_id.get(cid)
        modules = _trace_dep(cid, new_list)
        added_deps.append({
            "title": c_entry["title"],
            "concept_id": cid,
            "ecosystem": _get_dep_tag(new_dep or {}, "ecosystem:"),
            "new_version": _get_dep_version(new_dep) if new_dep else "",
            "affected_modules": modules,
            "total_modules": len(modules),
            "total_code_concepts": sum(len(m["code_concepts"]) for m in modules),
        })

    return {
        "changed_deps": changed_deps,
        "removed_deps": removed_deps,
        "added_deps": added_deps,
        "total_impacted_modules": len({
            m["concept_id"]
            for group in [changed_deps, removed_deps, added_deps]
            for dep in group
            for m in dep["affected_modules"]
        }),
        "total_impacted_code_concepts": sum(
            dep["total_code_concepts"]
            for group in [changed_deps, removed_deps, added_deps]
            for dep in group
        ),
    }


def fmt_impact(impact: dict, diff_result: dict) -> str:
    """Format impact analysis as a hierarchical tree."""
    lines = [
        DIVIDER,
        "  okf diff --impact",
        DIVIDER,
        f"  Old: {diff_result['old_path']} ({diff_result['old_count']} concepts)",
        f"  New: {diff_result['new_path']} ({diff_result['new_count']} concepts)",
        DIVIDER,
    ]

    if impact["changed_deps"]:
        lines.append(f"\n  Changed Dependencies ({len(impact['changed_deps'])}):\n")
        for dep in impact["changed_deps"]:
            v_old = dep["old_version"]
            v_new = dep["new_version"]
            ver_str = f" ({v_old} → {v_new})" if v_old or v_new else ""
            ecostr = f" [{dep['ecosystem']}]" if dep['ecosystem'] else ""
            lines.append(f"    [~] {dep['title']}{ver_str}{ecostr}")
            lines.append(f"        → {dep['total_modules']} module(s), {dep['total_code_concepts']} concept(s)")
            for mod in dep["affected_modules"]:
                res = f" ({mod['resource']})" if mod['resource'] else ""
                lines.append(f"          → {mod['title']}{res}")
                for cc in mod["code_concepts"]:
                    lines.append(f"            · {cc['title']} ({cc['type']})")
            lines.append("")

    if impact["removed_deps"]:
        lines.append(f"  Removed Dependencies ({len(impact['removed_deps'])}):\n")
        for dep in impact["removed_deps"]:
            ver_str = f" ({dep['old_version']})" if dep['old_version'] else ""
            lines.append(f"    [-] {dep['title']}{ver_str}")
            lines.append(f"        → {dep['total_modules']} module(s), {dep['total_code_concepts']} concept(s) impacted")
            for mod in dep["affected_modules"]:
                res = f" ({mod['resource']})" if mod['resource'] else ""
                lines.append(f"          → {mod['title']}{res}")
            lines.append("")

    if impact["added_deps"]:
        lines.append(f"  Added Dependencies ({len(impact['added_deps'])}):\n")
        for dep in impact["added_deps"]:
            ver_str = f" (v{dep['new_version']})" if dep['new_version'] else ""
            lines.append(f"    [+] {dep['title']}{ver_str}")

    # Summary
    lines.append(DIVIDER)
    lines.append(
        f"  Impact: {impact['total_impacted_modules']} module(s), "
        f"{impact['total_impacted_code_concepts']} code concept(s) affected"
    )
    lines.append(DIVIDER)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Diff two OKF bundles — see added, removed, and changed concepts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("old_bundle", help="Path to the older OKF bundle")
    p.add_argument("new_bundle", help="Path to the newer OKF bundle")
    p.add_argument("--compact", action="store_true", help="Compact one-line output per concept")
    p.add_argument("--json", action="store_true", help="JSON output for programmatic use")
    p.add_argument("--impact", action="store_true", help="Trace dependency changes to affected modules and code concepts")
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    old_dir = Path(args.old_bundle).resolve()
    new_dir = Path(args.new_bundle).resolve()

    if not old_dir.exists():
        print(f"ERROR: Old bundle not found: {old_dir}", file=sys.stderr)
        sys.exit(1)
    if not new_dir.exists():
        print(f"ERROR: New bundle not found: {new_dir}", file=sys.stderr)
        sys.exit(1)

    from okf.lookup import load_bundle as _load
    old_list = _load(old_dir)
    new_list = _load(new_dir)

    result = diff_bundles(old_dir, new_dir, old_list=old_list, new_list=new_list)

    if args.impact:
        impact = impact_analysis(old_list, new_list, result)
        if args.json:
            result["impact"] = impact
            print(fmt_json(result))
        else:
            print(fmt_impact(impact, result))
    elif args.json:
        print(fmt_json(result))
    elif args.compact:
        print(fmt_compact(result))
    else:
        print(fmt_detail(result))

    total_changes = len(result["added"]) + len(result["removed"]) + len(result["changed"])
    if total_changes == 0 and not args.impact:
        print("  No differences — bundles are identical.")
    sys.exit(0 if total_changes == 0 else 0)  # diff exits 0 even with changes


if __name__ == "__main__":
    main()
