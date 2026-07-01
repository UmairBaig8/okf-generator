"""okf visualize — generate an interactive HTML graph of an OKF bundle.

Usage:
  okf visualize <bundle_dir> [output_file]

Outputs a self-contained HTML file with a force-directed graph showing
concepts and their relationships (calls, called-by, related, dependencies).
"""

import argparse
import json
import re
import sys
from pathlib import Path


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OKF Bundle — {bundle_name}</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f0f1a; color: #e2e8f0; overflow: hidden; }}
#graph {{ width: 100vw; height: 100vh; }}
#tooltip {{ position: absolute; display: none; background: #1a1a2e; border: 1px solid #7c3aed; border-radius: 8px; padding: 12px; font-size: 13px; max-width: 350px; pointer-events: none; z-index: 100; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }}
#tooltip h3 {{ color: #a78bfa; margin-bottom: 4px; font-size: 15px; }}
#tooltip p {{ color: #94a3b8; margin: 2px 0; }}
#tooltip .type {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-bottom: 6px; }}
#legend {{ position: absolute; bottom: 20px; left: 20px; background: #1a1a2e; border: 1px solid #2d2d4a; border-radius: 8px; padding: 12px; font-size: 12px; }}
#legend h4 {{ color: #a78bfa; margin-bottom: 6px; font-size: 13px; }}
.legend-item {{ display: flex; align-items: center; gap: 8px; margin: 3px 0; color: #94a3b8; }}
.legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
#search {{ position: absolute; top: 20px; right: 20px; background: #1a1a2e; border: 1px solid #2d2d4a; border-radius: 8px; padding: 8px 12px; color: #e2e8f0; font-size: 14px; width: 220px; outline: none; }}
#search:focus {{ border-color: #7c3aed; }}
#stats {{ position: absolute; top: 20px; left: 20px; background: #1a1a2e; border: 1px solid #2d2d4a; border-radius: 8px; padding: 12px; font-size: 12px; color: #94a3b8; }}
#stats strong {{ color: #e2e8f0; }}
</style>
</head>
<body>
<div id="stats">OKF Bundle · <strong>{bundle_name}</strong> · {concept_count} concepts · {edge_count} edges</div>
<input id="search" type="text" placeholder="Search concepts..." oninput="filterGraph(this.value)">
<div id="tooltip"></div>
<div id="legend">
<h4>Legend</h4>
{legend_html}
</div>
<div id="graph"></div>
<script>
const data = {json_data};

const colorMap = {{
{color_map}
}};

const typeLabels = {{
{type_labels}
}};

const width = window.innerWidth;
const height = window.innerHeight;

const nodes = data.nodes.map(d => ({{ ...d }}));
const links = data.links.map(d => ({{ ...d }}));

const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(80))
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(20));

const svg = d3.select("#graph").append("svg")
    .attr("width", width).attr("height", height);

const g = svg.append("g");

svg.call(d3.zoom().scaleExtent([0.1, 4]).on("zoom", (event) => {{
    g.attr("transform", event.transform);
}}));

const link = g.append("g").selectAll("line").data(links).join("line")
    .attr("stroke", "#2d2d4a").attr("stroke-width", 1).attr("stroke-opacity", 0.6);

const node = g.append("g").selectAll("circle").data(nodes).join("circle")
    .attr("r", d => d.type === "Function" ? 5 : d.type === "Class" ? 7 : d.type === "Dependency" ? 4 : 6)
    .attr("fill", d => colorMap[d.type] || "#64748b")
    .attr("stroke", "#1a1a2e").attr("stroke-width", 1.5)
    .style("cursor", "pointer")
    .call(d3.drag()
        .on("start", (event, d) => {{ if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }})
        .on("drag", (event, d) => {{ d.fx = event.x; d.fy = event.y; }})
        .on("end", (event, d) => {{ if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }})
    );

const label = g.append("g").selectAll("text").data(nodes).join("text")
    .text(d => d.title.length > 20 ? d.title.slice(0, 18) + "..." : d.title)
    .attr("font-size", "10px").attr("dx", 10).attr("dy", 3)
    .attr("fill", "#94a3b8").style("pointer-events", "none");

const tooltip = d3.select("#tooltip");

node.on("mouseover", (event, d) => {{
    tooltip.style("display", "block")
        .html(`<span class="type" style="background:${{colorMap[d.type]||'#64748b'}}20;color:${{colorMap[d.type]||'#64748b'}}">${{d.type}}</span><h3>${{d.title}}</h3><p>${{(d.description||'').slice(0,100)}}</p><p style="color:#64748b;font-size:11px;margin-top:4px">${{d.resource||''}}</p>`)
        .style("left", (event.pageX + 15) + "px").style("top", (event.pageY - 10) + "px");
}}).on("mouseout", () => tooltip.style("display", "none"));

simulation.on("tick", () => {{
    link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
    node.attr("cx", d => d.x).attr("cy", d => d.y);
    label.attr("x", d => d.x).attr("y", d => d.y);
}});

function filterGraph(query) {{
    const q = query.toLowerCase();
    node.attr("opacity", d => !q || d.title.toLowerCase().includes(q) || d.type.toLowerCase().includes(q) ? 1 : 0.15);
    label.attr("opacity", d => !q || d.title.toLowerCase().includes(q) || d.type.toLowerCase().includes(q) ? 1 : 0.15);
    link.attr("stroke-opacity", d => !q ? 0.6 : (d.source.title.toLowerCase().includes(q) || d.target.title.toLowerCase().includes(q) ? 0.6 : 0.05));
}}
</script>
</body>
</html>"""


TYPE_COLORS = {
    "Class": "#7c3aed",
    "Function": "#06b6d4",
    "Module": "#f59e0b",
    "Dependency": "#4ade80",
    "Table": "#ef4444",
    "View": "#f97316",
    "Index": "#ec4899",
    "Method": "#8b5cf6",
    "Interface": "#22d3ee",
    "Type": "#a855f7",
    "Trigger": "#f43f5e",
}


def build_graph(bundle_dir: Path) -> tuple[list[dict], list[dict]]:
    from okf.lookup import load_bundle as _load
    concepts = _load(bundle_dir)

    nodes = []
    node_ids = set()
    for c in concepts:
        nid = c["concept_id"]
        if nid in node_ids:
            continue
        node_ids.add(nid)
        nodes.append({
            "id": nid, "title": c["title"], "type": c["type"],
            "description": c.get("description", ""),
            "resource": c.get("resource", ""),
        })

    def _extract_ids(text: str) -> list[str]:
        """Extract concept IDs from a markdown section like `- [name](/some/path)`."""
        if not text:
            return []
        ids = re.findall(r"\(/([^)]+)\.md\)", text)
        return ids

    links = []
    link_set = set()
    for c in concepts:
        src = c["concept_id"]
        sections = c.get("sections", {})
        schema = c.get("body_extra", {})

        # related links from ## Related section
        for rel_id in _extract_ids(sections.get("related", "")):
            key = f"rel||{src}||{rel_id}"
            if key not in link_set and rel_id in node_ids:
                link_set.add(key)
                links.append({"source": src, "target": rel_id, "type": "related"})

        # calls edges from ## Calls section
        for callee_id in _extract_ids(sections.get("calls", "")):
            key = f"call||{src}||{callee_id}"
            if key not in link_set and callee_id in node_ids:
                link_set.add(key)
                links.append({"source": src, "target": callee_id, "type": "calls"})

        # called_by edges from ## Called By section
        for caller_id in _extract_ids(sections.get("called by", "")):
            key = f"cb||{caller_id}||{src}"
            if key not in link_set and caller_id in node_ids:
                link_set.add(key)
                links.append({"source": caller_id, "target": src, "type": "called_by"})

        # dependency → code: link dep to its used_by (body_extra or section)
        if c["type"] == "Dependency" and schema:
            dep_name = c["title"].lower()
            # match dep name against module names in concept resources
            for other in concepts:
                if other["concept_id"] == src:
                    continue
                res = other.get("resource", "").lower()
                if dep_name in res and other.get("type") == "Module":
                    key = f"dep||{other['concept_id']}||{src}"
                    if key not in link_set:
                        link_set.add(key)
                        links.append({"source": other["concept_id"], "target": src, "type": "imports"})

    return nodes, links


def build_legend() -> str:
    items = []
    for t, color in TYPE_COLORS.items():
        items.append(f'<div class="legend-item"><div class="legend-dot" style="background:{color}"></div>{t}</div>')
    return "\n".join(items)


def build_color_map() -> str:
    lines = []
    for t, color in TYPE_COLORS.items():
        lines.append(f'  "{t}": "{color}",')
    return "\n".join(lines)


def build_type_labels() -> str:
    lines = []
    for t, color in TYPE_COLORS.items():
        lines.append(f'  "{t}": "{t}",')
    return "\n".join(lines)


def visualize(bundle_dir: Path) -> tuple[str, int, int]:
    nodes, links = build_graph(bundle_dir)

    bundle_name = bundle_dir.name
    json_data = json.dumps({"nodes": nodes, "links": links})

    html = HTML_TEMPLATE.format(
        bundle_name=bundle_name,
        bundle_name_esc=json.dumps(bundle_name),
        concept_count=len(nodes),
        edge_count=len(links),
        json_data=json_data,
        legend_html=build_legend(),
        color_map=build_color_map(),
        type_labels=build_type_labels(),
    )

    return html, len(nodes), len(links)


def main():
    parser = argparse.ArgumentParser(
        description="Generate an interactive HTML graph of an OKF bundle.",
    )
    parser.add_argument("bundle_dir", help="Path to the OKF bundle directory")
    parser.add_argument("output", nargs="?", default=None, help="Output HTML file (default: bundle_path/bundle_name.html)")
    args = parser.parse_args()

    bundle_dir = Path(args.bundle_dir).resolve()
    if not bundle_dir.exists():
        print(f"ERROR: Bundle not found: {bundle_dir}", file=sys.stderr)
        sys.exit(1)

    html, n_nodes, n_edges = visualize(bundle_dir)

    out = Path(args.output).resolve() if args.output else bundle_dir / f"{bundle_dir.name}.html"
    out.write_text(html, encoding="utf-8")
    print(f"Visualization written → {out}")
    print(f"  {n_nodes} concepts, {n_edges} edges")
    print(f"  Open in browser: file://{out}")
