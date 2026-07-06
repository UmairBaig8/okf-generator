"""okf dashboard — FastAPI live bundle browser with interactive concept graph.

Usage:
  okf dashboard <bundle_dir> [--port PORT] [--host HOST] [--open]
"""

import argparse
import json
import re
import sys
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import uvicorn


def build_app(bundle_dir: Path):
    from okf.lookup import load_bundle

    concepts = load_bundle(bundle_dir, use_cache=False)
    by_id = {c["concept_id"]: c for c in concepts}

    app = FastAPI(title="OKF Dashboard", version="0.1")
    app.state.concept_count = len(concepts)
    app.state.concepts = concepts

    @app.get("/api/info")
    def bundle_info():
        types: dict[str, int] = {}
        langs: dict[str, int] = {}
        for c in concepts:
            types[c["type"]] = types.get(c["type"], 0) + 1
            for t in c.get("tags", []):
                if t.startswith("lang:"):
                    lang = t[5:]
                    langs[lang] = langs.get(lang, 0) + 1
        return {
            "name": bundle_dir.name,
            "total": len(concepts),
            "types": types,
            "languages": langs,
        }

    @app.get("/api/types")
    def list_types():
        types: dict[str, int] = {}
        for c in concepts:
            types[c["type"]] = types.get(c["type"], 0) + 1
        return [{"type": k, "count": v} for k, v in sorted(types.items())]

    @app.get("/api/languages")
    def list_languages():
        langs: dict[str, int] = {}
        for c in concepts:
            for t in c.get("tags", []):
                if t.startswith("lang:"):
                    lang = t[5:]
                    langs[lang] = langs.get(lang, 0) + 1
        return [{"language": k, "count": v} for k, v in sorted(langs.items(), key=lambda x: -x[1])]

    @app.get("/api/search")
    def search(
        q: str = Query("", description="Search query"),
        type_filter: str = Query("", alias="type", description="Filter by type"),
        tag: str = Query("", description="Filter by tag"),
        limit: int = Query(50, description="Max results"),
    ):
        from okf.lookup import search as _search
        tokens = q.split() if q else []
        tag_filters = [tag] if tag else []
        results = _search(concepts, tokens=tokens, type_filter=type_filter, tag_filters=tag_filters, limit=limit)
        return [
            {
                "concept_id": c["concept_id"],
                "title": c["title"],
                "type": c["type"],
                "resource": c.get("resource", ""),
                "description": c.get("description", "")[:120],
            }
            for c in results
        ]

    @app.get("/api/concept/{concept_id:path}")
    def get_concept(concept_id: str):
        c = by_id.get(concept_id)
        if not c:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Concept not found")
        sections = c.get("sections", {})
        # Parse related links into structured list
        related = []
        for line in sections.get("related", "").splitlines():
            m = re.search(r"\[([^\]]+)\]\(/(.+?)\.md\)", line)
            if m:
                related.append({"title": m.group(1), "concept_id": m.group(2)})
        # Parse used_by from Dependency body
        used_by = []
        if c["type"] == "Dependency":
            for line in sections.get("used by", "").splitlines():
                m = re.search(r"\[([^\]]+)\]\(/(.+?)\.md\)", line)
                if m:
                    used_by.append({"title": m.group(1), "concept_id": m.group(2)})
        return {
            "concept_id": c["concept_id"],
            "title": c["title"],
            "type": c["type"],
            "resource": c.get("resource", ""),
            "description": c.get("description", ""),
            "tags": c.get("tags", []),
            "signature": sections.get("signature", ""),
            "docstring": sections.get("docstring", ""),
            "parameters": sections.get("parameters", ""),
            "returns": sections.get("returns", ""),
            "source": sections.get("source", ""),
            "related": related,
            "used_by": used_by,
            "raw": c.get("raw", ""),
        }

    @app.get("/api/graph")
    def graph(max_nodes: int = 100):
        nodes = []
        edges = []
        seen = set()
        # Pick the most referenced concepts up to max_nodes
        ref_count: dict[str, int] = {}
        for c in concepts:
            for line in c.get("sections", {}).get("related", "").splitlines():
                m = re.search(r"\]\(/(.+?)\.md\)", line)
                if m:
                    ref_count[m.group(1)] = ref_count.get(m.group(1), 0) + 1
        top = sorted(ref_count.items(), key=lambda x: -x[1])[:max_nodes]
        top_ids = {t[0] for t in top}
        # Also include dependencies that have used_by
        for c in concepts:
            if c["type"] == "Dependency" and c["concept_id"] not in top_ids:
                ub = []
                for line in c.get("sections", {}).get("used by", "").splitlines():
                    m = re.search(r"\]\(/(.+?)\.md\)", line)
                    if m:
                        ub.append(m.group(1))
                if ub and len(top_ids) < max_nodes:
                    top_ids.add(c["concept_id"])
                    top_ids.update(ub)
        for c in concepts:
            if c["concept_id"] not in top_ids:
                continue
            nodes.append({
                "id": c["concept_id"],
                "label": c["title"],
                "title": f"{c['type']}: {c['title']}",
                "group": c["type"],
            })
            for line in c.get("sections", {}).get("related", "").splitlines():
                m = re.search(r"\[([^\]]+)\]\(/(.+?)\.md\)", line)
                if m:
                    target = m.group(2)
                    if target in top_ids:
                        edges.append({"from": c["concept_id"], "to": target})
            # For Dependencies, add edges from used_by
            for line in c.get("sections", {}).get("used by", "").splitlines():
                m = re.search(r"\[([^\]]+)\]\(/(.+?)\.md\)", line)
                if m:
                    target = m.group(2)
                    if target in top_ids:
                        edges.append({"from": target, "to": c["concept_id"]})
        return {"nodes": nodes, "edges": edges, "total": len(concepts), "shown": len(nodes)}

    @app.get("/")
    def index():
        return HTMLResponse(FRONTEND_HTML)

    return app


FRONTEND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OKF Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.6/vis-network.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.6/dist/vis-network.min.css">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0e13; color: #e4e7eb; height: 100vh; display: flex; }
#sidebar { width: 300px; min-width: 300px; background: #13181f; border-right: 1px solid #1f2937; display: flex; flex-direction: column; overflow: hidden; }
#main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
#header { padding: 16px; border-bottom: 1px solid #1f2937; }
#header h1 { font-size: 18px; color: #e3b341; }
#header .stats { font-size: 12px; color: #6b7280; margin-top: 4px; }
#search-box { padding: 12px; border-bottom: 1px solid #1f2937; }
#search-box input, #search-box select { width: 100%; padding: 8px; margin-bottom: 6px; background: #1f2937; border: 1px solid #374151; border-radius: 4px; color: #e4e7eb; font-size: 13px; }
#search-box select { cursor: pointer; }
#search-box button { width: 100%; padding: 8px; background: #e3b341; color: #0b0e13; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 13px; }
#concept-list { flex: 1; overflow-y: auto; padding: 4px 0; }
.concept-item { padding: 10px 16px; border-bottom: 1px solid #1f2937; cursor: pointer; transition: background 0.15s; }
.concept-item:hover { background: #1f2937; }
.concept-item .title { font-size: 14px; font-weight: 500; }
.concept-item .meta { font-size: 11px; color: #6b7280; margin-top: 2px; }
.concept-item .desc { font-size: 12px; color: #9ca3af; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.badge { display: inline-block; padding: 1px 6px; border-radius: 3px; font-size: 10px; font-weight: 600; margin-right: 4px; }
.badge-Function { background: #1e40af; color: #93c5fd; }
.badge-Class { background: #065f46; color: #6ee7b7; }
.badge-Module { background: #6b21a8; color: #d8b4fe; }
.badge-Dependency { background: #92400e; color: #fcd34d; }
.badge-Interface { background: #1e3a5f; color: #7dd3fc; }
.badge-Enum { background: #4a1942; color: #f9a8d4; }
.badge-Constant { background: #374151; color: #9ca3af; }
#detail-panel { display: none; flex-direction: column; height: 100%; }
#detail-panel.active { display: flex; }
#detail-header { padding: 16px; border-bottom: 1px solid #1f2937; display: flex; align-items: center; gap: 8px; }
#detail-header h2 { font-size: 18px; flex: 1; }
#detail-close { cursor: pointer; font-size: 20px; color: #6b7280; background: none; border: none; padding: 4px 8px; }
#detail-close:hover { color: #e4e7eb; }
#detail-body { flex: 1; overflow-y: auto; padding: 16px; }
#detail-body pre { background: #1f2937; padding: 12px; border-radius: 4px; overflow-x: auto; font-size: 12px; margin: 8px 0; }
#detail-body table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 13px; }
#detail-body td, #detail-body th { padding: 6px 8px; border: 1px solid #1f2937; text-align: left; }
#detail-body th { background: #13181f; font-weight: 500; }
#detail-body a { color: #e3b341; text-decoration: none; }
#detail-body a:hover { text-decoration: underline; }
#graph-view { flex: 1; }
.tabs { display: flex; border-bottom: 1px solid #1f2937; }
.tab { padding: 10px 20px; cursor: pointer; font-size: 13px; color: #6b7280; border-bottom: 2px solid transparent; }
.tab.active { color: #e3b341; border-bottom-color: #e3b341; }
.tab-content { display: none; flex: 1; }
.tab-content.active { display: flex; flex-direction: column; }
#welcome { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #6b7280; }
#welcome h2 { font-size: 24px; margin-bottom: 8px; color: #e3b341; }
</style>
</head>
<body>
<div id="sidebar">
  <div id="header">
    <h1>OKF Dashboard</h1>
    <div class="stats" id="stats">Loading...</div>
  </div>
  <div id="search-box">
    <input type="text" id="search-input" placeholder="Search concepts..." onkeydown="if(event.key==='Enter') doSearch()">
    <select id="type-filter"><option value="">All types</option></select>
    <button onclick="doSearch()">Search</button>
  </div>
  <div id="concept-list"></div>
</div>
<div id="main">
  <div id="welcome">
    <h2>OKF Bundle Browser</h2>
    <p>Search concepts or click a type filter to begin.</p>
  </div>
  <div id="detail-panel">
    <div id="detail-header">
      <span class="badge" id="detail-badge"></span>
      <h2 id="detail-title"></h2>
      <button id="detail-close" onclick="closeDetail()">&times;</button>
    </div>
    <div class="tabs">
      <div class="tab active" onclick="switchTab('detail', this)">Detail</div>
      <div class="tab" onclick="switchTab('source', this)">Source</div>
      <div class="tab" onclick="switchTab('graph', this)">Graph</div>
    </div>
    <div id="tab-detail" class="tab-content active"><div id="detail-body"></div></div>
    <div id="tab-source" class="tab-content"><pre id="source-body"></pre></div>
    <div id="tab-graph" class="tab-content"><div id="graph-view"></div></div>
  </div>
</div>
<script>
let currentId = null;
let graphInstance = null;

async function api(path) {
  const r = await fetch(path);
  return r.json();
}

async function init() {
  const info = await api('/api/info');
  const types = await api('/api/types');
  document.getElementById('stats').textContent = `${info.total} concepts | ${Object.keys(info.languages).length} languages`;
  const sel = document.getElementById('type-filter');
  types.forEach(t => { const o = document.createElement('option'); o.value = t.type; o.textContent = `${t.type} (${t.count})`; sel.appendChild(o); });
  doSearch();
}

async function doSearch() {
  const q = document.getElementById('search-input').value;
  const t = document.getElementById('type-filter').value;
  const results = await api(`/api/search?q=${encodeURIComponent(q)}&type=${encodeURIComponent(t)}&limit=100`);
  const list = document.getElementById('concept-list');
  list.innerHTML = results.length ? '' : '<div style="padding:16px;color:#6b7280;font-size:13px">No results</div>';
  results.forEach(c => {
    const div = document.createElement('div');
    div.className = 'concept-item';
    div.innerHTML = `<span class="badge badge-${c.type}">${c.type}</span><span class="title">${esc(c.title)}</span><div class="meta">${esc(c.resource)}</div><div class="desc">${esc(c.description)}</div>`;
    div.onclick = () => openConcept(c.concept_id);
    list.appendChild(div);
  });
}

async function openConcept(id) {
  currentId = id;
  const c = await api(`/api/concept/${encodeURIComponent(id)}`);
  document.getElementById('welcome').style.display = 'none';
  document.getElementById('detail-panel').classList.add('active');
  document.getElementById('detail-badge').textContent = c.type;
  document.getElementById('detail-badge').className = 'badge badge-' + c.type;
  document.getElementById('detail-title').textContent = c.title;

  let html = '';
  if (c.description) html += `<p style="margin-bottom:12px">${esc(c.description)}</p>`;
  if (c.signature) html += `<h3>Signature</h3><pre>${esc(c.signature)}</pre>`;
  if (c.docstring) html += `<h3>Docstring</h3><pre>${esc(c.docstring)}</pre>`;
  if (c.parameters) html += `<h3>Parameters</h3>${c.parameters}`;
  if (c.returns) html += `<h3>Returns</h3><pre>${esc(c.returns)}</pre>`;
  if (c.tags && c.tags.length) html += `<h3>Tags</h3><p>${c.tags.map(t => '<code>' + esc(t) + '</code>').join(' ')}</p>`;
  if (c.related && c.related.length) {
    html += '<h3>Related</h3><ul>';
    c.related.forEach(r => { html += `<li><a href="#" onclick="openConcept('${r.concept_id}');return false">${esc(r.title)}</a></li>`; });
    html += '</ul>';
  }
  if (c.used_by && c.used_by.length) {
    html += '<h3>Used By</h3><ul>';
    c.used_by.forEach(r => { html += `<li><a href="#" onclick="openConcept('${r.concept_id}');return false">${esc(r.title)}</a></li>`; });
    html += '</ul>';
  }
  document.getElementById('detail-body').innerHTML = html;
  document.getElementById('source-body').textContent = c.raw;
  switchTab('detail', document.querySelector('.tab'));
  renderGraph(c);
}

function renderGraph(c) {
  const container = document.getElementById('graph-view');
  const nodes = new vis.DataSet([{ id: c.concept_id, label: c.title, group: c.type, color: { background: '#e3b341', border: '#e3b341' }, font: { color: '#fff', size: 16 } }]);
  const edges = new vis.DataSet();
  if (c.related) c.related.forEach(r => { nodes.add({ id: r.concept_id, label: r.title, group: 'Related' }); edges.add({ from: c.concept_id, to: r.concept_id }); });
  if (c.used_by) c.used_by.forEach(r => { nodes.add({ id: r.concept_id, label: r.title, group: 'Module' }); edges.add({ from: r.concept_id, to: c.concept_id }); });
  const options = { physics: { enabled: true, solver: 'forceAtlas2Based' }, edges: { arrows: { to: { enabled: true } }, color: { color: '#4b5563' } }, nodes: { shape: 'dot', size: 20, font: { color: '#e4e7eb', size: 12 }, borderWidth: 0 }, groups: { Related: { color: '#6366f1' }, Module: { color: '#8b5cf6' } }, background: '#0b0e13' };
  if (graphInstance) graphInstance.destroy();
  graphInstance = new vis.Network(container, { nodes, edges }, options);
}

function switchTab(name, el) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  if (name === 'graph' && graphInstance) graphInstance.fit();
}

function closeDetail() {
  document.getElementById('detail-panel').classList.remove('active');
  document.getElementById('welcome').style.display = 'flex';
  currentId = null;
}

function esc(s) { const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }

init();
</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(
        description="Launch the OKF live bundle dashboard (FastAPI + interactive graph).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("bundle_dir", nargs="?", default="./okf_bundle", help="Path to OKF bundle (default: ./okf_bundle)")
    parser.add_argument("--port", "-p", type=int, default=8700, help="Port (default: 8700)")
    parser.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    parser.add_argument("--open", "-o", action="store_true", help="Open browser automatically")
    args = parser.parse_args()

    bundle_dir = Path(args.bundle_dir).resolve()
    if not bundle_dir.exists():
        print(f"ERROR: Bundle not found: {bundle_dir}", file=sys.stderr)
        sys.exit(1)

    app = build_app(bundle_dir)
    url = f"http://{args.host}:{args.port}"
    print(f"  OKF Dashboard: {url}")
    print(f"  Bundle: {bundle_dir.name} ({app.state.concept_count} concepts)")

    if args.open:
        import webbrowser
        webbrowser.open(url)

    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")



if __name__ == "__main__":
    main()
