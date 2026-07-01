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
<script src="https://cdn.jsdelivr.net/npm/cytoscape@3/dist/cytoscape.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#0f0f1a; color:#e2e8f0; overflow:hidden; height:100vh; }}
#container {{ display:flex; height:100vh; }}
#graph {{ flex:1; height:100vh; }}
#panel {{ width:420px; background:#16162a; border-left:1px solid #2d2d4a; overflow-y:auto; display:none; padding:20px; font-size:14px; line-height:1.6; }}
#panel h2 {{ color:#a78bfa; font-size:18px; margin-bottom:4px; }}
#panel .type-badge {{ display:inline-block; padding:2px 10px; border-radius:4px; font-size:11px; font-weight:600; margin-bottom:8px; }}
#panel p {{ color:#94a3b8; margin:4px 0; }}
#panel .section {{ margin-top:12px; }}
#panel .section h3 {{ color:#e2e8f0; font-size:14px; margin-bottom:4px; }}
#panel .section pre {{ background:#1a1a2e; padding:8px; border-radius:4px; font-size:12px; overflow-x:auto; color:#cbd5e1; }}
#panel a {{ color:#7c3aed; text-decoration:none; }}
#panel a:hover {{ text-decoration:underline; }}
#panel .markdown-body {{ font-size:13px; color:#cbd5e1; }}
#panel .markdown-body h1 {{ font-size:16px; color:#e2e8f0; margin:8px 0 4px; }}
#panel .markdown-body h2 {{ font-size:14px; color:#e2e8f0; margin:8px 0 4px; }}
#panel .markdown-body h3 {{ font-size:13px; color:#a78bfa; margin:6px 0 2px; }}
#panel .markdown-body p {{ margin:4px 0; }}
#panel .markdown-body code {{ background:#1a1a2e; padding:1px 4px; border-radius:3px; font-size:12px; }}
#panel .markdown-body pre {{ background:#1a1a2e; padding:8px; border-radius:4px; font-size:12px; overflow-x:auto; }}
#panel .markdown-body table {{ border-collapse:collapse; width:100%; font-size:12px; margin:4px 0; }}
#panel .markdown-body th, #panel .markdown-body td {{ border:1px solid #2d2d4a; padding:4px 8px; text-align:left; }}
#panel .markdown-body th {{ background:#1a1a2e; color:#94a3b8; }}
#panel .markdown-body ul {{ margin:4px 0; padding-left:20px; }}
#panel .markdown-body li {{ margin:2px 0; }}
#topbar {{ position:fixed; top:0; left:0; right:0; height:48px; background:#0f0f1a; border-bottom:1px solid #2d2d4a; display:flex; align-items:center; padding:0 16px; gap:12px; z-index:100; }}
#topbar .title {{ color:#94a3b8; font-size:13px; }}
#topbar .title strong {{ color:#e2e8f0; }}
#search {{ background:#1a1a2e; border:1px solid #2d2d4a; border-radius:6px; padding:6px 10px; color:#e2e8f0; font-size:13px; width:200px; outline:none; }}
#search:focus {{ border-color:#7c3aed; }}
.layout-btn {{ background:#1a1a2e; border:1px solid #2d2d4a; border-radius:4px; color:#94a3b8; padding:4px 10px; font-size:12px; cursor:pointer; }}
.layout-btn:hover {{ border-color:#7c3aed; color:#e2e8f0; }}
.layout-btn.active {{ background:#7c3aed20; border-color:#7c3aed; color:#a78bfa; }}
#legend {{ position:fixed; bottom:16px; left:16px; background:#1a1a2e; border:1px solid #2d2d4a; border-radius:8px; padding:10px; font-size:11px; z-index:50; }}
#legend h4 {{ color:#a78bfa; font-size:12px; margin-bottom:4px; }}
.legend-item {{ display:flex; align-items:center; gap:6px; margin:2px 0; color:#94a3b8; }}
.legend-dot {{ width:10px; height:10px; border-radius:50%; }}
#type-filter {{ background:#1a1a2e; border:1px solid #2d2d4a; border-radius:4px; color:#94a3b8; padding:4px 8px; font-size:12px; outline:none; }}
</style>
</head>
<body>
<div id="loading" style="position:fixed;top:0;left:0;right:0;bottom:0;background:#0f0f1a;display:flex;align-items:center;justify-content:center;z-index:9999;color:#94a3b8;font-size:18px">Loading {concept_count} concepts...</div>
<div id="topbar">
<span class="title">OKF Bundle · <strong>{bundle_name}</strong> · {concept_count} concepts · {edge_count} edges</span>
<input id="search" type="text" placeholder="Search concepts...">
<select id="type-filter">
<option value="">All types</option>
{filter_options}
</select>
<button class="layout-btn active" data-layout="cose">Graph</button>
<button class="layout-btn" data-layout="circle">Circle</button>
<button class="layout-btn" data-layout="grid">Grid</button>
<button class="layout-btn" data-layout="breadthfirst">Tree</button>
</div>
<div id="container">
<div id="graph"></div>
<div id="panel"></div>
</div>
<div id="legend">
<h4>Types</h4>
{legend_html}
</div>
<script>
const data = {json_data};
const colorMap = {{
{color_map}
}};
const nodeData = {{}};
data.nodes.forEach(n => {{ nodeData[n.id] = n; }});

const cy = cytoscape({{
    container: document.getElementById('graph'),
    elements: [
        ...data.nodes.map(n => ({{
            data: {{ id: n.id, label: n.title.length>25?n.title.slice(0,23)+'...':n.title, type: n.type, desc: n.description||'', resource: n.resource||'', full: n }},
            classes: n.type
        }})),
        ...data.links.map(l => ({{
            data: {{ source: l.source, target: l.target, type: l.type }}
        }}))
    ],
    style: [
        {{ selector: 'node', style: {{ 'label': 'data(label)', 'color': '#94a3b8', 'font-size': '10px', 'text-valign': 'bottom', 'text-halign': 'center', 'text-margin-y': '4px', 'width': 10, 'height': 10, 'border-width': 1.5, 'border-color': '#1a1a2e', 'min-zoomed-font-size': 8 }} }},
        {{ selector: 'edge', style: {{ 'width': 0.8, 'line-color': '#2d2d4a', 'target-arrow-color': '#2d2d4a', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'arrow-scale': 0.5 }} }}
    ],
    layout: {{ name: 'cose', nodeDimensionsIncludeLabels: true, animate: false, idealEdgeLength: 60, nodeRepulsion: 4000, gravity: 0.25 }}
}});

// Hide loading screen
document.getElementById('loading').style.display = 'none';

// Color nodes by type
data.nodes.forEach(n => {{
    const color = colorMap[n.type] || '#64748b';
    const el = cy.getElementById(n.id);
    if (el.length) el.style({{ 'background-color': color, 'border-color': color }});
}});

// Type filter
document.getElementById('type-filter').addEventListener('change', function() {{
    const val = this.value;
    cy.nodes().forEach(n => {{
        if (!val || n.data('type') === val) {{
            n.show(); n.connectedEdges().show();
        }} else {{
            n.hide(); n.connectedEdges().hide();
        }}
    }});
}});

// Search
document.getElementById('search').addEventListener('input', function() {{
    const q = this.value.toLowerCase();
    cy.nodes().forEach(n => {{
        const match = !q || n.data('label').toLowerCase().includes(q) || n.data('type').toLowerCase().includes(q) || (n.data('desc')||'').toLowerCase().includes(q);
        if (match) {{ n.show(); n.connectedEdges().show(); }} else {{ n.hide(); n.connectedEdges().hide(); }}
    }});
}});

// Layout switching
document.querySelectorAll('.layout-btn').forEach(btn => {{
    btn.addEventListener('click', function() {{
        document.querySelectorAll('.layout-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        cy.layout({{ name: this.dataset.layout, animate: true, nodeDimensionsIncludeLabels: true, spacingFactor: 1.5 }}).run();
    }});
}});

// Click node → show detail panel
const panel = document.getElementById('panel');
cy.on('tap', 'node', function(evt) {{
    const n = evt.target;
    console.log('Clicked:', n.id());
    const d = nodeData[n.id()];
    if (!d) {{ console.log('No data for', n.id()); return; }}
    panel.style.display = 'block';
    const color = colorMap[d.type] || '#64748b';
    let html = `<span class="type-badge" style="background:${{color}}20;color:${{color}}">${{d.type}}</span>`;
    html += `<h2>${{d.title}}</h2>`;
    if (d.description) html += `<p>${{d.description}}</p>`;
    if (d.resource) html += `<p style="font-size:12px;color:#64748b">${{d.resource}}</p>`;

    // Find sections from node data
    const sections = d.sections || {{}};
    const deptable = d.deptable || {{}};

    // Dependency table
    if (Object.keys(deptable).length) {{
        html += `<div class="section"><h3>Details</h3><table style="width:100%;font-size:12px">`;
        for (const [k, v] of Object.entries(deptable)) {{
            html += `<tr><td style="color:#94a3b8;padding:2px 4px">${{k}}</td><td style="padding:2px 4px">${{v}}</td></tr>`;
        }}
        html += `</table></div>`;
    }}

    if (sections.signature) {{
        html += `<div class="section"><h3>Signature</h3><pre>${{sections.signature.replace(/```\w*\\n?/g,'')}}</pre></div>`;
    }}
    if (sections.docstring) {{
        html += `<div class="section"><h3>Docstring</h3><pre>${{sections.docstring.slice(0,300)}}</pre></div>`;
    }}
    if (sections.parameters) {{
        html += `<div class="section"><h3>Parameters</h3><pre>${{sections.parameters.slice(0,200)}}</pre></div>`;
    }}
    if (sections.returns) {{
        html += `<div class="section"><h3>Returns</h3><pre>${{sections.returns}}</pre></div>`;
    }}

    // Related / Calls / Called By sections
    for (const sk of ['related', 'calls', 'called by']) {{
        if (sections[sk]) {{
            html += `<div class="section"><h3>${{sk.charAt(0).toUpperCase()+sk.slice(1)}}</h3>${{sections[sk]}}</div>`;
        }}
    }}

    // Cited by (reverse of related links)
    const citedBy = data.links.filter(l => l.target === d.id).map(l => nodeData[l.source]).filter(Boolean);
    if (citedBy.length) {{
        html += `<div class="section"><h3>Cited by</h3>`;
        citedBy.forEach(c => {{
            const cc = colorMap[c.type] || '#64748b';
            html += `<div style="margin:4px 0;font-size:13px"><span style="color:${{cc}};font-weight:600">${{c.type}}</span> <a href="#" onclick="selectNode('${{c.id}}');return false">${{c.title}}</a></div>`;
        }});
        html += `</div>`;
    }}

    // Full markdown body (rendered)
    if (d.body) {{
        const bodyParts = d.body.split('---');
        const mdBody = bodyParts.length >= 3 ? bodyParts.slice(2).join('---').trim() : d.body;
        if (mdBody) {{
            // Rewire markdown links to navigate within the viewer
            const rewired = mdBody.replace(/\[([^\]]+)\]\(\/([^)]+)\.md\)/g, (match, text, path) => {{
                const targetId = path;
                if (nodeData[targetId]) {{
                    return `[${{text}}](javascript:selectNode('${{targetId}}'))`;
                }}
                return match;
            }});
            try {{
                html += `<div class="section"><h3>Body</h3><div class="markdown-body">${{marked.parse(rewired)}}</div></div>`;
            }} catch(e) {{
                html += `<div class="section"><h3>Body</h3><pre style="font-size:12px;color:#94a3b8">${{mdBody.slice(0,500)}}</pre></div>`;
            }}
        }}
    }}

    try {
        panel.innerHTML = html;
        panel.scrollTop = 0;
    }} catch(e) {{ console.log('Panel render error:', e); }}
}});

function selectNode(id) {{
    const n = cy.getElementById(id);
    if (n.length) {{
        cy.fit(n, 50);
        n.trigger('tap');
    }}
}}

// Click background → hide panel
cy.on('tap', function(evt) {{
    if (evt.target === cy) panel.style.display = 'none';
}});
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

        # dependency used_by edges from ## Used By section
        if c["type"] == "Dependency":
            for module_id in _extract_ids(sections.get("used by", "")):
                key = f"usedby||{module_id}||{src}"
                if key not in link_set and module_id in node_ids:
                    link_set.add(key)
                    links.append({"source": module_id, "target": src, "type": "imports"})
            # also check body_extra if present
            if schema and schema.get("used_by"):
                for module_id in schema["used_by"]:
                    key = f"usedby||{module_id}||{src}"
                    if key not in link_set and module_id in node_ids:
                        link_set.add(key)
                        links.append({"source": module_id, "target": src, "type": "imports"})

    return nodes, links


def build_filter_options() -> str:
    opts = []
    for t in TYPE_COLORS:
        opts.append(f'<option value="{t}">{t}</option>')
    return "\n".join(opts)


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
        filter_options=build_filter_options(),
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
    print(f"  Or serve via: python3 -m http.server --directory {out.parent} && open http://localhost:8000/{out.name}")
