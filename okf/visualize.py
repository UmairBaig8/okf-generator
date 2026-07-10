"""okf visualize — generate an interactive HTML explorer for an OKF bundle.

Usage:
  okf visualize [bundle_dir] [output_file]
  okf visualize --bundle <path> [output_file]
"""

import argparse
import json
import re
import sys
from pathlib import Path


TYPE_COLORS = {
    "Class": "#a78bfa", "Function": "#38bdf8", "Module": "#fbbf24",
    "Dependency": "#4ade80", "Table": "#fb7185", "View": "#fb923c",
    "Index": "#f472b6", "Method": "#c084fc", "Interface": "#22d3ee",
    "Type": "#818cf8", "Trigger": "#f43f5e",
}


# ---------------------------------------------------------------------------
# Data extraction
# ---------------------------------------------------------------------------

def build_graph(bundle_dir: Path) -> tuple[list[dict], list[dict], list[str], dict]:
    from okf.lookup import load_bundle as _load
    concepts = _load(bundle_dir)

    nodes = []
    node_ids = set()
    for c in concepts:
        nid = c["concept_id"]
        if nid in node_ids:
            continue
        node_ids.add(nid)
        raw_body = c.get("raw", "")
        deptable = {}
        if c["type"] == "Dependency" and "| Ecosystem |" in raw_body:
            for line in raw_body.splitlines():
                if line.startswith("| "):
                    parts = [p.strip().strip("`") for p in line.split("|")[1:-1]]
                    if len(parts) == 2 and parts[0] not in ("Field", "Ecosystem", "Version constraint", "Source manifest", "Dev dependency", "Used by"):
                        deptable[parts[0]] = parts[1]
                    elif len(parts) == 2:
                        deptable[parts[0].lower()] = parts[1]
        sections = c.get("sections", {})
        # Parse structured fields from markdown bullet lists in sections
        def _parse_bullets(text: str) -> list[str]:
            if not text:
                return []
            return [re.sub(r'^-\s*`?|`$', '', line).strip() for line in text.strip().splitlines()
                    if line.strip().startswith('- ')]
        nodes.append({
            "id": nid, "title": c["title"], "type": c["type"],
            "description": c.get("description", ""),
            "resource": c.get("resource", ""),
            "sections": sections,
            "deptable": deptable,
            "body": c.get("raw", ""),
            "code": "",
            "visibility": _parse_bullets(sections.get("visibility", "")),
            "decorators": _parse_bullets(sections.get("decorators", "")),
            "inheritance": _parse_bullets(sections.get("inheritance", "")),
            "type_params": _parse_bullets(sections.get("type_parameters", "")),
            "tags": c.get("tags", []),
        })

    # Source code reading: best-effort per unique resource path
    # The resource field is relative to the scanned root (e.g. "src/file.py").
    # We don't store the scanned root, so try multiple base directories.
    code_cache: dict[str, str] = {}
    # Collect all possible base dirs (parents of bundle + CWD + ancestors up to git root)
    search_bases: list[Path] = [bundle_dir.parent]
    # Read source_root from bundle index.md if available
    try:
        index_md = bundle_dir / "index.md"
        if index_md.exists():
            raw = index_md.read_text(encoding="utf-8")
            parts = raw.split("---", 2)
            if len(parts) >= 2:
                import yaml
                fm = yaml.safe_load(parts[1]) or {}
                src = fm.get("source_root")
                if src:
                    search_bases.insert(0, Path(str(src)).resolve())
    except Exception:
        pass
    try:
        cwd = Path.cwd().resolve()
        search_bases.append(cwd)
        # Walk up from CWD to find git root and all intermediate dirs
        for parent in cwd.parents:
            search_bases.append(parent)
            if (parent / ".git").exists():
                break
    except Exception:
        pass
    for n in nodes:
        resource = n.get("resource", "")
        if not resource:
            continue
        if resource in code_cache:
            n["code"] = code_cache[resource]
            continue
        src_candidates = []
        for base in search_bases:
            src_candidates.append(base / resource)
            src_candidates.append(base / resource.lstrip("/"))
            if "/" in resource:
                src_candidates.append(base / resource.split("/")[-1])
        found = ""
        for sp in src_candidates:
            if sp:
                try:
                    if sp.exists() and sp.is_file():
                        found = sp.read_text(encoding="utf-8")
                        break
                except (PermissionError, OSError):
                    continue
                except Exception:
                    continue
        code_cache[resource] = found
        n["code"] = found

    def _extract_ids(text: str) -> list[str]:
        if not text:
            return []
        return re.findall(r"\(/([^)]+)\.md\)", text)

    links = []
    link_set = set()
    for c in concepts:
        src = c["concept_id"]
        sections = c.get("sections", {})
        schema = c.get("body_extra", {})

        for rel_id in _extract_ids(sections.get("related", "")):
            key = f"rel||{src}||{rel_id}"
            if key not in link_set and rel_id in node_ids:
                link_set.add(key)
                links.append({"source": src, "target": rel_id, "type": "related"})

        for callee_id in _extract_ids(sections.get("calls", "")):
            key = f"call||{src}||{callee_id}"
            if key not in link_set and callee_id in node_ids:
                link_set.add(key)
                links.append({"source": src, "target": callee_id, "type": "calls"})

        for caller_id in _extract_ids(sections.get("called by", "")):
            key = f"cb||{caller_id}||{src}"
            if key not in link_set and caller_id in node_ids:
                link_set.add(key)
                links.append({"source": caller_id, "target": src, "type": "called_by"})

        if c["type"] == "Dependency":
            for module_id in _extract_ids(sections.get("used by", "")):
                key = f"usedby||{module_id}||{src}"
                if key not in link_set and module_id in node_ids:
                    link_set.add(key)
                    links.append({"source": module_id, "target": src, "type": "imports"})
            if schema and schema.get("used_by"):
                for module_id in schema["used_by"]:
                    key = f"usedby||{module_id}||{src}"
                    if key not in link_set and module_id in node_ids:
                        link_set.add(key)
                        links.append({"source": module_id, "target": src, "type": "imports"})

    # Detect sub-bundles: directories under bundle_dir that have SUMMARY.md
    sub_bundles: list[str] = sorted(
        d.name for d in bundle_dir.iterdir()
        if d.is_dir() and (d / "SUMMARY.md").exists()
    )

    bundle_of_node: dict[str, str] = {}
    for n in nodes:
        cid = n["id"]
        matched = next((sb for sb in sub_bundles if cid.startswith(sb + "/")), "")
        bundle = matched if matched else bundle_dir.name
        bundle_of_node[cid] = bundle

    # If no sub-bundles detected (or none matched), fall back to first-path-segment grouping
    if not sub_bundles or all(b == bundle_dir.name for b in bundle_of_node.values()):
        if sub_bundles:  # reset when sub-bundles exist but none matched
            sub_bundles.clear()
        for n in nodes:
            cid = n["id"]
            seg = cid.split("/")[0] if cid else bundle_dir.name
            bundle_of_node[n["id"]] = seg

    bundles = sorted(set(bundle_of_node.values()),
                     key=lambda x: (x == bundle_dir.name, x))

    # Count per bundle for landing stats
    bundle_counts: dict[str, int] = {}
    for nid, b in bundle_of_node.items():
        bundle_counts[b] = bundle_counts.get(b, 0) + 1

    # Attach bundle to each node
    for n in nodes:
        n["bundle"] = bundle_of_node.get(n["id"], bundle_dir.name)

    return nodes, links, bundles, bundle_counts


def build_tree(nodes: list[dict]) -> dict:
    root: dict = {"__concepts__": [], "__children__": {}}
    for n in nodes:
        cid = n["id"]
        parts = cid.split("/")
        folder_parts = parts[:-1] if len(parts) > 1 else []
        cursor = root
        for part in folder_parts:
            cursor = cursor["__children__"].setdefault(part, {"__concepts__": [], "__children__": {}})
        cursor["__concepts__"].append(n)
    return root


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def visualize(bundle_dir: Path) -> tuple[str, int, int]:
    nodes, links, bundles, bundle_counts = build_graph(bundle_dir)
    bundle_name = bundle_dir.name

    json_nodes = []
    for n in nodes:
        jn = {k: v for k, v in n.items() if k != "code"}
        jn["code"] = n.get("code", "")
        json_nodes.append(jn)

    template_path = Path(__file__).parent / "templates" / "viz-template.html"
    html = template_path.read_text(encoding="utf-8")

    bundle_data = json.dumps({
        "nodes": json_nodes, "links": links,
        "bundles": bundles,
        "bundle_name": bundle_name,
    }, ensure_ascii=False)

    html = html.replace("{DYNAMIC_FLAG}", "false")
    html = html.replace("{BUNDLE_DATA}", bundle_data)

    return html, len(nodes), len(links)


def main():
    parser = argparse.ArgumentParser(
        description="Generate an interactive HTML explorer for an OKF bundle.",
    )
    parser.add_argument("bundle_dir", nargs="?", default="./okf_bundle", help="Path to the OKF bundle directory (default: ./okf_bundle)")
    parser.add_argument("--bundle", help="Path to OKF bundle (overrides positional)")
    parser.add_argument("output", nargs="?", default=None, help="Output HTML file (default: bundle_path/bundle_name.html)")
    args = parser.parse_args()

    bundle_dir = Path(args.bundle or args.bundle_dir).resolve()
    if not bundle_dir.exists():
        print(f"ERROR: Bundle not found: {bundle_dir}", file=sys.stderr)
        sys.exit(1)

    html, n_nodes, n_edges = visualize(bundle_dir)

    out = Path(args.output).resolve() if args.output else bundle_dir / "viz.html"
    out.write_text(html, encoding="utf-8")
    print(f"Visualization written -> {out}")
    print(f"  {n_nodes} concepts, {n_edges} edges")
    print(f"  Open in browser: file://{out}")
