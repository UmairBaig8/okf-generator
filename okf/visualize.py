"""okf visualize — generate an interactive HTML explorer for an OKF bundle.

Usage:
  okf visualize [bundle_dir] [output_file]
  okf visualize --bundle <path> [output_file]
"""

import argparse
import json
import sys
from pathlib import Path

TYPE_COLORS = {
    "Class": "#a78bfa", "Function": "#38bdf8", "Module": "#fbbf24",
    "Dependency": "#4ade80", "Table": "#fb7185", "View": "#fb923c",
    "Index": "#f472b6", "Method": "#c084fc", "Interface": "#22d3ee",
    "Type": "#818cf8", "Trigger": "#f43f5e",
}


def _resolve_source_code(bundle_dir: Path, resource: str, line_range: str) -> str:
    if not resource or not line_range:
        return ""
    import re
    m = re.search(r"Lines (\d+)\s*[–-]\s*(\d+)", line_range)
    if not m:
        return ""
    start, end = int(m.group(1)), int(m.group(2))
    source_roots = [bundle_dir.parent.resolve(), Path.cwd().resolve()]
    index_md = bundle_dir / "index.md"
    if index_md.exists():
        try:
            import yaml
            parts = index_md.read_text(encoding="utf-8").split("---", 2)
            if len(parts) >= 2:
                fm = yaml.safe_load(parts[1]) or {}
                src = fm.get("source_root")
                if src:
                    source_roots.insert(0, Path(str(src)).resolve())
        except Exception:
            pass
    for root in source_roots:
        src_path = root / resource
        try:
            if src_path.exists():
                lines = src_path.read_text(encoding="utf-8", errors="replace").splitlines()
                if start <= len(lines):
                    return "\n".join(lines[max(0, start - 1):end])
        except Exception:
            continue
    return ""


def build_graph(bundle_dir: Path, max_nodes: int = 800) -> tuple[list[dict], list[dict], list[str], dict, int]:
    from okf.storage import open_store

    store = open_store(bundle_dir)
    total = store.get_info()["total"]

    g = store.get_graph(max_nodes=max_nodes)
    nodes_raw = g["nodes"]
    edges_raw = g["edges"]

    # Fetch source code for each node from original files
    for n in nodes_raw:
        concept = store.get(n["id"])
        if concept:
            src_section = concept.get("sections", {}).get("source", "")
            n["code"] = _resolve_source_code(bundle_dir, n.get("resource", ""), src_section)
        else:
            n["code"] = ""

    bundle_of_node: dict[str, str] = {}
    sub_bundles: set[str] = set()
    for n in nodes_raw:
        cid = n["id"]
        seg = cid.split("/")[0] if cid else bundle_dir.name
        bundle_of_node[n["id"]] = seg
        sub_bundles.add(seg)
    bundles = sorted(sub_bundles)
    bundle_counts: dict[str, int] = {}
    for _nid, b in bundle_of_node.items():
        bundle_counts[b] = bundle_counts.get(b, 0) + 1

    for n in nodes_raw:
        n["bundle"] = bundle_of_node.get(n["id"], bundle_dir.name)

    store.close()
    return nodes_raw, edges_raw, bundles, bundle_counts, total


def visualize(bundle_dir: Path, max_nodes: int = 800) -> tuple[str, int, int]:
    nodes, links, bundles, bundle_counts, total_concepts = build_graph(bundle_dir, max_nodes=max_nodes)
    bundle_name = bundle_dir.name

    template_path = Path(__file__).parent / "templates" / "viz-template.html"
    html = template_path.read_text(encoding="utf-8")

    bundle_data = json.dumps({
        "nodes": nodes, "links": links,
        "bundles": bundles,
        "bundle_name": bundle_name,
        "total_concepts": total_concepts,
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
    parser.add_argument("--graph-nodes", type=int, default=800, help="Max nodes in graph view (default: 800)")
    parser.add_argument("output", nargs="?", default=None, help="Output HTML file (default: bundle_path/viz.html)")
    args = parser.parse_args()

    bundle_dir = Path(args.bundle or args.bundle_dir).resolve()
    if not bundle_dir.exists():
        print(f"ERROR: Bundle not found: {bundle_dir}", file=sys.stderr)
        sys.exit(1)

    html, n_nodes, n_edges = visualize(bundle_dir, max_nodes=args.graph_nodes)

    html = html.replace("{GRAPH_MAX_NODES}", str(args.graph_nodes))

    out = Path(args.output).resolve() if args.output else bundle_dir / "viz.html"

    out.write_text(html, encoding="utf-8")

    print(f"Visualization written -> {out}")
    print(f"  {n_nodes} concepts, {n_edges} edges")
    print(f"  Open in browser: file://{out}")


if __name__ == "__main__":
    main()
