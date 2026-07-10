"""Migrate OKF bundles between schema versions.

Usage:
  okf migrate v0.1-to-v0.2 <bundle_dir>
"""

import re
import sys
from pathlib import Path

import yaml


def _migrate_v01_to_v02(bundle_dir: Path, dry_run: bool = False) -> int:
    """Convert a v0.1 bundle to v0.2 in-place. Returns count of files changed."""
    if not bundle_dir.is_dir():
        print(f"Not a directory: {bundle_dir}", file=sys.stderr)
        sys.exit(1)

    changed = 0
    md_files = sorted(bundle_dir.rglob("*.md"))

    for path in md_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue

        try:
            fm = yaml.safe_load(parts[1]) or {}
        except Exception:
            continue

        # skip if already v0.2
        if fm.get("okf_version") == "0.2":
            continue

        # skip Index/Log (no individual concept data)
        ctype = fm.get("type", "")
        body = parts[2]

        # 1. Add okf_version
        fm["okf_version"] = "0.2"

        # 2. Extract language from tags
        tags = fm.get("tags", [])
        if isinstance(tags, list):
            for t in tags:
                if isinstance(t, str) and t.startswith("lang:"):
                    fm["language"] = t.removeprefix("lang:")
                    break

        # 3. Add concept_id if missing (non-Index, non-Log concepts)
        if ctype not in {"Index", "Log"}:
            rel = path.relative_to(bundle_dir)
            cid = str(rel.with_suffix("")).replace("\\", "/").replace("/", "/")
            if not fm.get("concept_id"):
                fm["concept_id"] = cid

        # 4. Convert body sections: Related/Calls/Called By → Relationships
        body = _convert_relationships(body)

        # 5. Write back
        new_frontmatter = "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True) + "---\n"
        new_text = new_frontmatter + "\n" + body.lstrip("\n")

        if new_text != text:
            if dry_run:
                print(f"  Would update: {path.relative_to(bundle_dir)}")
            else:
                path.write_text(new_text, encoding="utf-8")
            changed += 1

    return changed


_REL_SECTION_RE = re.compile(
    r"^## (Related|Calls|Called By|Related \(AI-suggested\))\s*$",
    re.MULTILINE,
)


def _convert_relationships(body: str) -> str:
    """Replace standalone Related/Calls/Called By sections with a single Relationships table."""
    lines = body.splitlines()
    result: list[str] = []
    in_rel_section: str | None = None
    rel_items: list[tuple[str, str]] = []  # (type, link_line)

    for line in lines:
        m = _REL_SECTION_RE.match(line)
        if m:
            if in_rel_section and rel_items:
                # flush previous section (shouldn't happen, but safety)
                pass
            in_rel_section = {
                "Related": "related",
                "Related (AI-suggested)": "related (AI)",
                "Calls": "calls",
                "Called By": "called_by",
            }.get(m.group(1), m.group(1).lower())
            rel_items = []
            continue

        if in_rel_section:
            stripped = line.strip()
            if not stripped:
                continue
            # keep bullet items
            if stripped.startswith("- ["):
                rel_items.append((in_rel_section, stripped))
                continue
            # blank line ends section
            if stripped == "" and not rel_items:
                continue
            if stripped == "":
                # end of section
                in_rel_section = None
                continue
            # non-blank non-bullet might be part of section content — skip
            continue

        result.append(line)

    if rel_items:
        result.append("## Relationships\n")
        result.append("| Type | Target |")
        result.append("|------|--------|")
        link_re = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        for rtype, item in rel_items:
            m = link_re.search(item)
            if m:
                result.append(f"| {rtype} | [{m.group(1)}]({m.group(2)}) |")
            else:
                label = item.strip("- []").strip()
                if label:
                    result.append(f"| {rtype} | {label} |")
        result.append("")

    return "\n".join(result)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: okf migrate v0.1-to-v0.2 <bundle_dir>")
        print("  Convert an OKF v0.1 bundle to v0.2 format in-place.")
        print("  Use --dry-run to preview changes without writing.")
        sys.exit(0)

    if len(args) < 1:
        print("Missing migration target: v0.1-to-v0.2", file=sys.stderr)
        sys.exit(1)

    target = args[0]
    if target not in ("v0.1-to-v0.2", "v01-to-v02"):
        print(f"Unknown migration: {target}", file=sys.stderr)
        print("Available: v0.1-to-v0.2", file=sys.stderr)
        sys.exit(1)

    bundle_dir = Path(args[1] if len(args) > 1 else "okf_bundle").resolve()
    dry_run = "--dry-run" in args

    print(f"Migrating {bundle_dir} to v0.2...")
    changed = _migrate_v01_to_v02(bundle_dir, dry_run=dry_run)

    if dry_run:
        print(f"Would update {changed} file(s) (dry run)")
    else:
        print(f"Updated {changed} file(s)")


if __name__ == "__main__":
    main()
