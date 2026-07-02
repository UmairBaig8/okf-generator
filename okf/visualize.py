"""okf visualize — generate an interactive HTML explorer for an OKF bundle.

Usage:
  okf visualize <bundle_dir> [output_file]
"""

import argparse
import base64
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
        nodes.append({
            "id": nid, "title": c["title"], "type": c["type"],
            "description": c.get("description", ""),
            "resource": c.get("resource", ""),
            "sections": c.get("sections", {}),
            "deptable": deptable,
            "body": c.get("raw", ""),
            "code": "",
        })

    # Source code reading: best-effort per unique resource path
    # The resource field is relative to the scanned root (e.g. "src/file.py").
    # We don't store the scanned root, so try multiple common layouts.
    code_cache: dict[str, str] = {}
    for n in nodes:
        resource = n.get("resource", "")
        if not resource:
            continue
        if resource in code_cache:
            n["code"] = code_cache[resource]
            continue
        bp = bundle_dir.parent
        src_candidates = [
            bp / resource,                        # bundle at ./okf_bundle, src at ./src/file.py → ./src/file.py
            bp / resource.lstrip("/"),
            Path(resource) if resource.startswith("/") else None,
            # Resource may include the source dir prefix (e.g. "my_project/src/file.py")
            bp / resource.split("/")[-1] if "/" in resource else None,
        ]
        # Also try walking up: the resource might be relative to a subdir of bundle_dir.parent
        for part in Path(resource).parents:
            if part.name and (bp / part.parent.name / resource).exists():
                src_candidates.append(bp / part.parent.name / resource)
                break
        found = ""
        for sp in src_candidates:
            if sp and sp.exists() and sp.is_file():
                try:
                    found = sp.read_text(encoding="utf-8")
                except Exception:
                    found = ""
                break
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

    # If no sub-bundles detected, fall back to first-path-segment grouping
    if not sub_bundles:
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

    # Strip code from nodes for main JSON (code is sent separately per node)
    json_nodes = []
    for n in nodes:
        jn = {k: v for k, v in n.items() if k != "code"}
        if n.get("code"):
            jn["code"] = n["code"]
        json_nodes.append(jn)

    json_data = json.dumps({"nodes": json_nodes, "links": links}, ensure_ascii=False)

    from okf._viz_template import DEMO_HTML_B64
    html = base64.b64decode(DEMO_HTML_B64).decode("utf-8")

    html = html.replace("<title>OKF Bundle — demo</title>", f"<title>OKF Bundle — {bundle_name}</title>")
    html = html.replace('<span class="name">fresh_agentbox</span>', f'<span class="name">{bundle_name}</span>')

    okf_link = '<a href="https://github.com/UmairBaig8/okf-generator" target="_blank" style="font-size:11px;color:var(--text-3);text-decoration:none;margin-right:8px;white-space:nowrap">okf</a>\n  '
    html = html.replace('<button class="icon-btn" id="theme-toggle"', okf_link + '<button class="icon-btn" id="theme-toggle"')

    html = html.replace(
        "const TYPE_COLORS = {\n"
        "  Class:'#a78bfa', Function:'#38bdf8', Module:'#fbbf24', Dependency:'#4ade80',\n"
        "  Table:'#fb7185', View:'#fb923c', Index:'#f472b6', Method:'#c084fc',\n"
        "  Interface:'#22d3ee', Type:'#818cf8', Trigger:'#f43f5e',\n"
        "};",
        "const TYPE_COLORS = {\n" + "\n".join(f'  {t}:"{c}",' for t, c in sorted(TYPE_COLORS.items())) + "\n};"
    )

    # Inject data, BUNDLE_NAME, and BUNDLES
    data_marker = "const data = {\n  nodes: ["
    data_idx = html.find(data_marker)
    if data_idx >= 0:
        end_marker = "const BUNDLES = [];"
        end_idx = html.find(end_marker, data_idx)
        if end_idx >= 0:
            new_data = f"const data = {json_data};\n\nconst BUNDLE_NAME = '{bundle_name}';\nconst BUNDLES = {json.dumps(bundles)};\n"
            html = html[:data_idx] + new_data + html[end_idx + len(end_marker):]

    return html, len(nodes), len(links)


def main():
    parser = argparse.ArgumentParser(
        description="Generate an interactive HTML explorer for an OKF bundle.",
    )
    parser.add_argument("bundle_dir", help="Path to the OKF bundle directory")
    parser.add_argument("output", nargs="?", default=None, help="Output HTML file (default: bundle_path/bundle_name.html)")
    args = parser.parse_args()

    bundle_dir = Path(args.bundle_dir).resolve()
    if not bundle_dir.exists():
        print(f"ERROR: Bundle not found: {bundle_dir}", file=sys.stderr)
        sys.exit(1)

    html, n_nodes, n_edges = visualize(bundle_dir)

    out = Path(args.output).resolve() if args.output else bundle_dir / "viz.html"
    out.write_text(html, encoding="utf-8")
    print(f"Visualization written -> {out}")
    print(f"  {n_nodes} concepts, {n_edges} edges")
    print(f"  Open in browser: file://{out}")
