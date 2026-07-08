"""okf dashboard — FastAPI live bundle browser with interactive concept graph.

Usage:
  okf dashboard <bundle_dir> [--port PORT] [--host HOST] [--open]
"""

import argparse
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
        ecosystems: dict[str, int] = {}
        for c in concepts:
            types[c["type"]] = types.get(c["type"], 0) + 1
            for t in c.get("tags", []):
                if t.startswith("lang:") and t != "lang:manifest":
                    langs[t[5:]] = langs.get(t[5:], 0) + 1
                if t.startswith("ecosystem:"):
                    ecosystems[t[10:]] = ecosystems.get(t[10:], 0) + 1
        return {
            "name": bundle_dir.name,
            "total": len(concepts),
            "types": types,
            "languages": langs,
            "ecosystems": ecosystems,
        }

    @app.get("/api/types")
    def list_types():
        types: dict[str, int] = {}
        for c in concepts:
            types[c["type"]] = types.get(c["type"], 0) + 1
        return [{"type": k, "count": v} for k, v in sorted(types.items(), key=lambda x: -x[1])]

    @app.get("/api/languages")
    def list_languages():
        langs: dict[str, int] = {}
        for c in concepts:
            for t in c.get("tags", []):
                if t.startswith("lang:") and t != "lang:manifest":
                    lang = t[5:]
                    langs[lang] = langs.get(lang, 0) + 1
        return [{"language": k, "count": v} for k, v in sorted(langs.items(), key=lambda x: -x[1])]

    @app.get("/api/search")
    def search(
        q: str = Query("", description="Search query"),
        type_filter: str = Query("", alias="type", description="Filter by type"),
        tag: str = Query("", description="Filter by tag"),
        limit: int = Query(80, description="Max results"),
    ):
        from okf.lookup import search as _search

        tokens = q.split() if q else []
        tag_filters = [tag] if tag else []
        results = _search(
            concepts, tokens=tokens, type_filter=type_filter, tag_filters=tag_filters, limit=limit
        )
        return [
            {
                "concept_id": c["concept_id"],
                "title": c["title"],
                "type": c["type"],
                "resource": c.get("resource", ""),
                "description": c.get("description", "")[:140],
                "tags": c.get("tags", []),
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
        related = []
        for line in sections.get("related", "").splitlines():
            m = re.search(r"\[([^\]]+)\]\(/(.+?)\.md\)", line)
            if m:
                related.append({"title": m.group(1), "concept_id": m.group(2)})
        calls = []
        for line in sections.get("calls", "").splitlines():
            m = re.search(r"\[([^\]]+)\]\(/(.+?)\.md\)", line)
            if m:
                calls.append({"title": m.group(1), "concept_id": m.group(2)})
        called_by = []
        for line in sections.get("called by", "").splitlines():
            m = re.search(r"\[([^\]]+)\]\(/(.+?)\.md\)", line)
            if m:
                called_by.append({"title": m.group(1), "concept_id": m.group(2)})
        used_by = []
        for line in sections.get("used by", "").splitlines():
            m = re.search(r"\[([^\]]+)\]\(/(.+?)\.md\)", line)
            if m:
                used_by.append({"title": m.group(1), "concept_id": m.group(2)})
        lang = ""
        for t in c.get("tags", []):
            if t.startswith("lang:") and t != "lang:manifest":
                lang = t[5:]
                break
        return {
            "concept_id": c["concept_id"],
            "title": c["title"],
            "type": c["type"],
            "resource": c.get("resource", ""),
            "description": c.get("description", ""),
            "tags": c.get("tags", []),
            "lang": lang,
            "signature": sections.get("signature", ""),
            "docstring": sections.get("docstring", ""),
            "parameters": sections.get("parameters", ""),
            "returns": sections.get("returns", ""),
            "source": sections.get("source", ""),
            "related": related,
            "calls": calls,
            "called_by": called_by,
            "used_by": used_by,
            "raw": c.get("raw", ""),
        }

    @app.get("/api/graph")
    def graph(max_nodes: int = Query(120)):
        ref_count: dict[str, int] = {}
        for c in concepts:
            for line in c.get("sections", {}).get("related", "").splitlines():
                m = re.search(r"\]\(/(.+?)\.md\)", line)
                if m:
                    ref_count[m.group(1)] = ref_count.get(m.group(1), 0) + 1
        top_ids: set[str] = {
            t[0] for t in sorted(ref_count.items(), key=lambda x: -x[1])[:max_nodes]
        }
        for c in concepts:
            if c["type"] == "Dependency" and c["concept_id"] not in top_ids:
                ub = [
                    m.group(1)
                    for line in c.get("sections", {}).get("used by", "").splitlines()
                    if (m := re.search(r"\]\(/(.+?)\.md\)", line))
                ]
                if ub and len(top_ids) < max_nodes:
                    top_ids.add(c["concept_id"])
                    top_ids.update(ub[:5])
        nodes, edges = [], []
        for c in concepts:
            if c["concept_id"] not in top_ids:
                continue
            nodes.append(
                {
                    "id": c["concept_id"],
                    "label": c["title"],
                    "title": f"{c['type']}: {c['title']}",
                    "group": c["type"],
                }
            )
            for sec_key in ("related", "calls"):
                for line in c.get("sections", {}).get(sec_key, "").splitlines():
                    m = re.search(r"\]\(/(.+?)\.md\)", line)
                    if m and m.group(1) in top_ids:
                        edges.append(
                            {"from": c["concept_id"], "to": m.group(1), "type": sec_key}
                        )
            for line in c.get("sections", {}).get("used by", "").splitlines():
                m = re.search(r"\]\(/(.+?)\.md\)", line)
                if m and m.group(1) in top_ids:
                    edges.append({"from": m.group(1), "to": c["concept_id"], "type": "uses"})
        return {"nodes": nodes, "edges": edges, "total": len(concepts), "shown": len(nodes)}

    @app.get("/")
    def index():
        return HTMLResponse(FRONTEND_HTML)

    return app


FRONTEND_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="dark light">
<title>OKF Dashboard</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🗺</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
<style>
:root {
  --primary: #6366F1;
  --primary-hover: #4F46E5;
  --primary-light: #A5B4FC;
  --primary-subtle: #EEF2FF;
  --accent: #06B6D4;
  --accent-hover: #0891B2;
  --success: #10B981;
  --warning: #F59E0B;
  --danger: #EF4444;
  --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --radius: 8px;
  --radius-sm: 4px;
  --radius-lg: 12px;
  --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-lg: 0 4px 6px rgba(0,0,0,0.07), 0 10px 15px rgba(0,0,0,0.1);
  --transition: 0.2s ease;
}

[data-theme="light"] {
  --bg: #F8FAFC;
  --bg-card: #FFFFFF;
  --bg-sidebar: #FFFFFF;
  --bg-topbar: #FFFFFF;
  --bg-hover: #F1F5F9;
  --bg-active: #EEF2FF;
  --border: #E2E8F0;
  --text: #0F172A;
  --text-secondary: #64748B;
  --text-muted: #94A3B8;
  --text-inverse: #FFFFFF;
  --input-bg: #F1F5F9;
  --input-border: #E2E8F0;
  --pre-bg: #F1F5F9;
  --scrollbar-thumb: #CBD5E1;
  --scrollbar-track: transparent;
}

[data-theme="dark"] {
  --bg: #0F172A;
  --bg-card: #1E293B;
  --bg-sidebar: #1E293B;
  --bg-topbar: #1E293B;
  --bg-hover: #334155;
  --bg-active: #312E81;
  --border: #334155;
  --text: #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
  --text-inverse: #0F172A;
  --input-bg: #334155;
  --input-border: #475569;
  --pre-bg: #0F172A;
  --scrollbar-thumb: #475569;
  --scrollbar-track: transparent;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: var(--font); background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column; overflow: hidden; -webkit-font-smoothing: antialiased; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--scrollbar-track); }
::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 3px; }
:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; border-radius: var(--radius-sm); }

/* Topbar */
#topbar { display: flex; align-items: center; padding: 0 20px; height: 52px; min-height: 52px; background: var(--bg-topbar); border-bottom: 1px solid var(--border); gap: 16px; z-index: 100; }
#topbar .logo { display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 16px; color: var(--primary); white-space: nowrap; }
#topbar .logo svg { width: 22px; height: 22px; }
#topbar .logo span { color: var(--text); }
#topbar .topbar-center { flex: 1; display: flex; align-items: center; gap: 12px; max-width: 520px; margin: 0 auto; }
#topbar .topbar-right { display: flex; align-items: center; gap: 8px; white-space: nowrap; }
#search-input { flex: 1; padding: 7px 12px 7px 32px; background: var(--input-bg); border: 1px solid var(--input-border); border-radius: var(--radius); color: var(--text); font-size: 13px; font-family: var(--font); transition: border-color var(--transition), box-shadow var(--transition); }
#search-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(99,102,241,0.15); outline: none; }
#search-wrap { position: relative; flex: 1; }
#search-wrap .icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }
#stats { font-size: 12px; color: var(--text-secondary); display: flex; gap: 12px; }
#stats strong { color: var(--text); font-weight: 600; }

/* Theme toggle */
.theme-btn { background: none; border: 1px solid var(--border); border-radius: var(--radius); width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: var(--text-secondary); transition: all var(--transition); font-size: 15px; }
.theme-btn:hover { background: var(--bg-hover); color: var(--text); }

/* Layout */
#layout { display: flex; flex: 1; overflow: hidden; }

/* Sidebar */
#sidebar { width: 280px; min-width: 280px; background: var(--bg-sidebar); border-right: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }
#sidebar-header { padding: 12px 16px; border-bottom: 1px solid var(--border); }
#sidebar-header .filter-row { display: flex; gap: 8px; margin-top: 8px; }
#type-filter { flex: 1; padding: 6px 8px; background: var(--input-bg); border: 1px solid var(--input-border); border-radius: var(--radius-sm); color: var(--text); font-size: 12px; font-family: var(--font); cursor: pointer; }
#lang-filter { flex: 1; padding: 6px 8px; background: var(--input-bg); border: 1px solid var(--input-border); border-radius: var(--radius-sm); color: var(--text); font-size: 12px; font-family: var(--font); cursor: pointer; }

/* Tree */
#concept-tree { flex: 1; overflow-y: auto; padding: 4px 0; }
.group-header { padding: 8px 16px 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); display: flex; align-items: center; gap: 6px; cursor: pointer; user-select: none; }
.group-header:hover { color: var(--text-secondary); }
.group-header .count { font-weight: 400; font-size: 10px; background: var(--bg-hover); padding: 0 5px; border-radius: 8px; }
.group-body { }
.group-body.collapsed { display: none; }
.concept-item { display: flex; align-items: center; gap: 6px; padding: 7px 16px 7px 20px; cursor: pointer; transition: background 0.12s; border-left: 3px solid transparent; font-size: 13px; }
.concept-item:hover { background: var(--bg-hover); }
.concept-item.active { background: var(--bg-active); border-left-color: var(--primary); }
.concept-item .title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 500; }
.concept-item .loc { font-size: 10px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 80px; }

/* Badges */
.badge { display: inline-flex; align-items: center; padding: 1px 7px; border-radius: 4px; font-size: 10px; font-weight: 600; line-height: 1.5; text-transform: uppercase; letter-spacing: 0.3px; flex-shrink: 0; }
.badge-Function { background: #DBEAFE; color: #1D4ED8; }
.badge-Class { background: #D1FAE5; color: #047857; }
.badge-Module { background: #EDE9FE; color: #6D28D9; }
.badge-Dependency { background: #FEF3C7; color: #B45309; }
.badge-Interface { background: #E0F2FE; color: #0369A1; }
.badge-Enum { background: #FCE7F3; color: #BE185D; }
.badge-Constant { background: #F3F4F6; color: #374151; }
.badge-Variable { background: #F3F4F6; color: #374151; }
.badge-Method { background: #ECFCCB; color: #3F6212; }
[data-theme="dark"] .badge-Function { background: #1E3A5F; color: #93C5FD; }
[data-theme="dark"] .badge-Class { background: #064E3B; color: #6EE7B7; }
[data-theme="dark"] .badge-Module { background: #3B0764; color: #D8B4FE; }
[data-theme="dark"] .badge-Dependency { background: #451A03; color: #FCD34D; }
[data-theme="dark"] .badge-Interface { background: #0C4A6E; color: #7DD3FC; }
[data-theme="dark"] .badge-Enum { background: #4A1942; color: #F9A8D4; }
[data-theme="dark"] .badge-Constant { background: #374151; color: #D1D5DB; }
[data-theme="dark"] .badge-Variable { background: #374151; color: #D1D5DB; }
[data-theme="dark"] .badge-Method { background: #365314; color: #BEF264; }

/* Main area */
#main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
#tabs { display: flex; border-bottom: 1px solid var(--border); padding: 0 16px; background: var(--bg-card); flex-shrink: 0; }
.tab { padding: 10px 20px; cursor: pointer; font-size: 13px; font-weight: 500; color: var(--text-secondary); border-bottom: 2px solid transparent; transition: all var(--transition); background: none; border-top: none; border-left: none; border-right: none; font-family: var(--font); }
.tab:hover { color: var(--text); background: var(--bg-hover); }
.tab.active { color: var(--primary); border-bottom-color: var(--primary); }
.tab-content { display: none; flex: 1; overflow: hidden; }
.tab-content.active { display: flex; flex-direction: column; }

/* Welcome */
#welcome { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--text-secondary); text-align: center; padding: 40px; gap: 8px; }
#welcome svg { width: 64px; height: 64px; color: var(--text-muted); margin-bottom: 8px; }
#welcome h2 { font-size: 20px; font-weight: 600; color: var(--text); }
#welcome p { font-size: 14px; max-width: 400px; }

/* Detail panel */
#detail-panel { display: none; flex-direction: column; height: 100%; }
#detail-panel.active { display: flex; }
#detail-topbar { display: flex; align-items: center; gap: 10px; padding: 12px 16px; border-bottom: 1px solid var(--border); background: var(--bg-card); flex-shrink: 0; }
#detail-back { background: none; border: none; color: var(--text-secondary); cursor: pointer; font-size: 18px; padding: 2px 4px; border-radius: var(--radius-sm); display: flex; align-items: center; }
#detail-back:hover { color: var(--text); background: var(--bg-hover); }
#detail-topbar .detail-title { font-size: 15px; font-weight: 600; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
#detail-location { font-size: 11px; color: var(--text-muted); background: var(--bg-hover); padding: 2px 8px; border-radius: var(--radius-sm); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 300px; }
#detail-close { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 20px; padding: 2px 6px; border-radius: var(--radius-sm); line-height: 1; }
#detail-close:hover { color: var(--text); background: var(--bg-hover); }

#detail-tabs { display: flex; border-bottom: 1px solid var(--border); padding: 0 16px; background: var(--bg-card); flex-shrink: 0; }
.dtab { padding: 8px 16px; cursor: pointer; font-size: 12px; font-weight: 500; color: var(--text-secondary); border-bottom: 2px solid transparent; transition: all var(--transition); background: none; border-top: none; border-left: none; border-right: none; font-family: var(--font); }
.dtab:hover { color: var(--text); }
.dtab.active { color: var(--primary); border-bottom-color: var(--primary); }
.dtab-content { display: none; flex: 1; overflow-y: auto; }
.dtab-content.active { display: block; }

#detail-body { padding: 16px; }
#detail-body h3 { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); margin: 16px 0 6px; }
#detail-body h3:first-child { margin-top: 0; }
#detail-body p { font-size: 13px; line-height: 1.6; color: var(--text-secondary); margin-bottom: 12px; }
#detail-body pre { background: var(--pre-bg); padding: 10px 12px; border-radius: var(--radius-sm); overflow-x: auto; font-size: 12px; line-height: 1.5; font-family: 'SF Mono', 'Fira Code', monospace; margin: 4px 0 8px; border: 1px solid var(--border); color: var(--text); }
#detail-body pre code { background: none; padding: 0; }
#detail-body code { background: var(--bg-hover); padding: 1px 5px; border-radius: 3px; font-size: 12px; font-family: 'SF Mono', 'Fira Code', monospace; }
#detail-body ul { list-style: none; padding: 0; margin: 4px 0 8px; }
#detail-body ul li { padding: 3px 0; font-size: 13px; }
#detail-body a { color: var(--primary); text-decoration: none; font-weight: 500; cursor: pointer; }
#detail-body a:hover { text-decoration: underline; color: var(--primary-hover); }
.detail-section { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 12px; margin-bottom: 10px; }
.detail-section .section-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); margin-bottom: 6px; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
@media (max-width: 900px) { .detail-grid { grid-template-columns: 1fr; } }
.detail-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 12px; }
.detail-card .card-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px; color: var(--text-muted); margin-bottom: 4px; }
.detail-card .card-value { font-size: 13px; word-break: break-word; }
.detail-card .card-value a { color: var(--primary); text-decoration: none; cursor: pointer; }
.detail-card .card-value a:hover { text-decoration: underline; }
.link-list { display: flex; flex-wrap: wrap; gap: 4px; }
.link-list a { display: inline-block; padding: 2px 8px; background: var(--bg-hover); border-radius: 4px; font-size: 12px; color: var(--primary); text-decoration: none; }
.link-list a:hover { background: var(--bg-active); }

#source-body { padding: 16px; }
#source-body pre { background: var(--pre-bg); padding: 16px; border-radius: var(--radius); overflow-x: auto; font-size: 12px; line-height: 1.6; font-family: 'SF Mono', 'Fira Code', monospace; border: 1px solid var(--border); margin: 0; tab-size: 2; }

#graph-view { flex: 1; min-height: 300px; background: var(--bg); }
#global-graph-view { flex: 1; min-height: 300px; background: var(--bg); }
.graph-legend { display: flex; gap: 12px; padding: 8px 16px; border-bottom: 1px solid var(--border); flex-wrap: wrap; font-size: 11px; background: var(--bg-card); flex-shrink: 0; }
.graph-legend-item { display: flex; align-items: center; gap: 4px; }
.graph-legend-item .dot { width: 10px; height: 10px; border-radius: 50%; }
.graph-legend-item .lbl { color: var(--text-secondary); }

.loading { display: flex; align-items: center; justify-content: center; height: 100%; color: var(--text-muted); font-size: 13px; gap: 8px; }
.spinner { width: 18px; height: 18px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>
<div id="topbar">
  <div class="logo" aria-label="OKF Dashboard">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
    OKF<span>Dashboard</span>
  </div>
  <div class="topbar-center">
    <div id="search-wrap">
      <span class="icon" aria-hidden="true">&#128269;</span>
      <input type="text" id="search-input" placeholder="Search concepts..." aria-label="Search concepts" autocomplete="off">
    </div>
  </div>
  <div class="topbar-right">
    <div id="stats"><span>Concepts: <strong id="stat-total">-</strong></span><span>Languages: <strong id="stat-langs">-</strong></span></div>
    <button class="theme-btn" id="theme-btn" onclick="toggleTheme()" aria-label="Toggle theme" title="Toggle theme">&#9790;</button>
  </div>
</div>

<div id="layout">
  <nav id="sidebar" aria-label="Concept navigation">
    <div id="sidebar-header">
      <div class="filter-row">
        <select id="type-filter" aria-label="Filter by type" onchange="onFilterChange()"><option value="">All types</option></select>
        <select id="lang-filter" aria-label="Filter by language" onchange="onFilterChange()"><option value="">All languages</option></select>
      </div>
    </div>
    <div id="concept-tree" role="tree" aria-label="Concepts"></div>
  </nav>

  <main id="main">
    <div id="tabs" role="tablist" aria-label="Dashboard tabs">
      <button class="tab active" role="tab" aria-selected="true" onclick="switchTab('browse',this)">Browse</button>
      <button class="tab" role="tab" aria-selected="false" onclick="switchTab('graph',this)">Global Graph</button>
    </div>

    <div id="tab-browse" class="tab-content active">
      <div id="welcome">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/><path d="M8 11h6"/><path d="M11 8v6"/></svg>
        <h2>Search or select a concept</h2>
        <p>Use the sidebar tree or search bar to browse the knowledge bundle.</p>
      </div>
      <div id="detail-panel">
        <div id="detail-topbar">
          <button id="detail-back" onclick="closeDetail()" aria-label="Back to concept list">&#8592;</button>
          <span class="badge" id="detail-badge"></span>
          <span class="detail-title" id="detail-title"></span>
          <span id="detail-location"></span>
          <button id="detail-close" onclick="closeDetail()" aria-label="Close detail panel">&times;</button>
        </div>
        <div id="detail-tabs" role="tablist" aria-label="Concept detail tabs">
          <button class="dtab active" role="tab" aria-selected="true" onclick="switchDetailTab('dmain',this)">Detail</button>
          <button class="dtab" role="tab" aria-selected="false" onclick="switchDetailTab('dsource',this)">Source</button>
          <button class="dtab" role="tab" aria-selected="false" onclick="switchDetailTab('dgraph',this)">Subgraph</button>
        </div>
        <div id="dtab-dmain" class="dtab-content active"><div id="detail-body"></div></div>
        <div id="dtab-dsource" class="dtab-content"><div id="source-body"><pre></pre></div></div>
        <div id="dtab-dgraph" class="dtab-content"><div id="graph-view"><div class="loading">Select a concept to see its subgraph</div></div></div>
      </div>
    </div>

    <div id="tab-graph" class="tab-content">
      <div class="graph-legend" id="graph-legend" role="region" aria-label="Graph legend"></div>
      <div id="global-graph-view"><div class="loading"><div class="spinner"></div> Loading graph...</div></div>
    </div>
  </main>
</div>

<script>
let currentId = null;
let currentResults = [];
let graphInstance = null;
let globalGraphInstance = null;
let globalGraphData = null;
let conceptCache = {};
let allTypes = [];
let allLangs = [];

function qs(id) { return document.getElementById(id); }
function esc(s) { var d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }

async function api(path) { var r = await fetch(path); return r.json(); }

/* Theme */
(function() {
  var t = localStorage.getItem('okf-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', t);
  qs('theme-btn').textContent = t === 'dark' ? '\u2600' : '\u263E';
})();
function toggleTheme() {
  var html = document.documentElement;
  var cur = html.getAttribute('data-theme');
  var next = cur === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  qs('theme-btn').textContent = next === 'dark' ? '\u2600' : '\u263E';
  localStorage.setItem('okf-theme', next);
}

/* Init */
async function init() {
  var info = await api('/api/info');
  qs('stat-total').textContent = info.total;
  qs('stat-langs').textContent = Object.keys(info.languages).length;

  allTypes = await api('/api/types');
  var sel = qs('type-filter');
  allTypes.forEach(function(t) {
    var o = document.createElement('option');
    o.value = t.type; o.textContent = t.type + ' (' + t.count + ')';
    sel.appendChild(o);
  });

  allLangs = await api('/api/languages');
  var lsel = qs('lang-filter');
  allLangs.forEach(function(l) {
    var o = document.createElement('option');
    o.value = l.language; o.textContent = l.language + ' (' + l.count + ')';
    lsel.appendChild(o);
  });

  buildLegend();
  doSearch();
}
document.addEventListener('DOMContentLoaded', init);

/* Search */
async function doSearch() {
  var q = qs('search-input').value;
  var t = qs('type-filter').value;
  var l = qs('lang-filter').value;
  var url = '/api/search?q=' + encodeURIComponent(q) + '&type=' + encodeURIComponent(t) + '&limit=200';
  if (l) url += '&tag=' + encodeURIComponent('lang:' + l);
  currentResults = await api(url);
  renderTree(currentResults);
}

function onFilterChange() { doSearch(); }

qs('search-input').addEventListener('keydown', function(e) { if (e.key === 'Enter') doSearch(); });

/* Tree */
function renderTree(results) {
  var groups = {};
  results.forEach(function(c) {
    var g = c.type || 'Other';
    if (!groups[g]) groups[g] = [];
    groups[g].push(c);
  });
  var tree = qs('concept-tree');
  tree.innerHTML = '';
  var sorted = Object.keys(groups).sort();
  sorted.forEach(function(g) {
    var hdr = document.createElement('div');
    hdr.className = 'group-header';
    hdr.setAttribute('role', 'treeitem');
    hdr.setAttribute('aria-expanded', 'true');
    hdr.tabIndex = 0;
    hdr.innerHTML = '<span aria-hidden="true">&#9660;</span> ' + g + ' <span class="count">' + groups[g].length + '</span>';
    var body = document.createElement('div');
    body.className = 'group-body';
    groups[g].forEach(function(c) {
      var item = document.createElement('div');
      item.className = 'concept-item';
      item.setAttribute('role', 'treeitem');
      item.tabIndex = 0;
      item.dataset.id = c.concept_id;
      item.innerHTML = '<span class="badge badge-' + c.type + '">' + c.type + '</span><span class="title">' + esc(c.title) + '</span><span class="loc">' + esc(c.resource.split('/').pop()) + '</span>';
      item.addEventListener('click', function() { openConcept(c.concept_id); });
      item.addEventListener('keydown', function(e) { if (e.key === 'Enter') openConcept(c.concept_id); });
      body.appendChild(item);
    });
    hdr.addEventListener('click', function() {
      var collapsed = body.classList.toggle('collapsed');
      hdr.querySelector('span:first-child').textContent = collapsed ? '\u25B6' : '\u25BC';
      hdr.setAttribute('aria-expanded', !collapsed);
    });
    hdr.addEventListener('keydown', function(e) { if (e.key === 'Enter') { this.click(); } });
    tree.appendChild(hdr);
    tree.appendChild(body);
  });
}

/* Detail */
async function openConcept(id) {
  qs('welcome').style.display = 'none';
  qs('detail-panel').classList.add('active');

  // highlight in tree
  document.querySelectorAll('.concept-item.active').forEach(function(el) { el.classList.remove('active'); });
  var el = document.querySelector('.concept-item[data-id="' + id.replace(/"/g,'\\"') + '"]');
  if (el) el.classList.add('active');

  var c;
  if (conceptCache[id]) { c = conceptCache[id]; }
  else { c = await api('/api/concept/' + id); conceptCache[id] = c; }
  currentId = id;
  renderDetail(c);
}

function renderDetail(c) {
  qs('detail-badge').textContent = c.type;
  qs('detail-badge').className = 'badge badge-' + c.type;
  qs('detail-title').textContent = c.title;
  qs('detail-location').textContent = c.resource;
  qs('detail-location').title = c.resource;

  var body = qs('detail-body');
  var html = '';

  if (c.description) html += '<p>' + esc(c.description) + '</p>';

  html += '<div class="detail-grid">';
  if (c.type) html += '<div class="detail-card"><div class="card-label">Type</div><div class="card-value">' + esc(c.type) + '</div></div>';
  if (c.lang) html += '<div class="detail-card"><div class="card-label">Language</div><div class="card-value">' + esc(c.lang) + '</div></div>';
  if (c.signature) html += '<div class="detail-card" style="grid-column:1/-1"><div class="card-label">Signature</div><div class="card-value"><pre style="margin:4px 0 0;font-size:12px">' + esc(c.signature) + '</pre></div></div>';
  html += '</div>';

  if (c.parameters) {
    html += '<div class="detail-section"><div class="section-label">Parameters</div><pre>' + esc(c.parameters) + '</pre></div>';
  }
  if (c.returns) {
    html += '<div class="detail-section"><div class="section-label">Returns</div><pre>' + esc(c.returns) + '</pre></div>';
  }
  if (c.docstring) {
    html += '<div class="detail-section"><div class="section-label">Docstring</div><pre>' + esc(c.docstring) + '</pre></div>';
  }

  var linkSections = [
    { label: 'Related', items: c.related },
    { label: 'Called By', items: c.called_by },
    { label: 'Used By', items: c.used_by },
    { label: 'Calls', items: c.calls }
  ];
  linkSections.forEach(function(sec) {
    if (sec.items && sec.items.length) {
      html += '<div class="detail-section"><div class="section-label">' + sec.label + '</div><div class="link-list">';
      sec.items.forEach(function(r) {
        html += '<a onclick="openConcept(\'' + r.concept_id.replace(/'/g,"\\'") + '\');return false" role="link" tabindex="0">' + esc(r.title) + '</a>';
      });
      html += '</div></div>';
    }
  });

  if (c.tags && c.tags.length) {
    html += '<div class="detail-section"><div class="section-label">Tags</div><div class="link-list">';
    c.tags.forEach(function(t) { html += '<code>' + esc(t) + '</code> '; });
    html += '</div></div>';
  }

  body.innerHTML = html;

  qs('source-body').querySelector('pre').textContent = c.raw || 'No source available.';
  switchDetailTab('dmain', qs('dtab-dmain'));
  renderSubgraph(c);
}

function renderSubgraph(c) {
  var container = qs('graph-view');
  var nodesArr = [{ id: c.concept_id, label: c.title, group: c.type }];
  var edgesArr = [];
  ['related','used_by','calls','called_by'].forEach(function(k) {
    if (c[k]) c[k].forEach(function(r) {
      nodesArr.push({ id: r.concept_id, label: r.title, group: k === 'called_by' ? 'CalledBy' : (k === 'used_by' ? 'UsedBy' : k) });
      edgesArr.push(k === 'called_by' || k === 'used_by'
        ? { from: r.concept_id, to: c.concept_id }
        : { from: c.concept_id, to: r.concept_id });
    });
  });
  if (graphInstance) graphInstance.destroy();
  if (nodesArr.length < 2) { container.innerHTML = '<div class="loading">No connections for this concept</div>'; return; }
  container.innerHTML = '';
  var nodes = new vis.DataSet(nodesArr);
  var edges = new vis.DataSet(edgesArr);
  var colors = { Related: '#6366F1', Calls: '#10B981', CalledBy: '#F59E0B', UsedBy: '#06B6D4' };
  var defaultColor = '#6366F1';
  var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  var options = {
    physics: { solver: 'forceAtlas2Based', forceAtlas2Based: { gravitationalConstant: -40, centralGravity: 0.005, springLength: 120, springConstant: 0.08 } },
    edges: { arrows: { to: { enabled: true, scaleFactor: 0.6 } }, color: { color: '#64748B' }, smooth: { type: 'curvedCW', roundness: 0.15 } },
    nodes: { shape: 'dot', size: 18, font: { color: isDark ? '#E2E8F0' : '#334155', size: 11, face: 'Inter' }, borderWidth: 0, chosen: { node: function(v) { v.borderWidth = 2; v.borderColor = '#6366F1'; } } },
    groups: Object.fromEntries(Object.entries(colors).map(function(e) { return [e[0], { color: e[1] }]; })),
    interaction: { hover: true, tooltipDelay: 100 },
    background: isDark ? '#0F172A' : '#F8FAFC'
  };
  var mainColor = isDark ? '#A5B4FC' : '#6366F1';
  nodes.update({ id: c.concept_id, color: { background: mainColor, border: mainColor }, font: { color: isDark ? '#FFFFFF' : '#0F172A', size: 12, face: 'Inter' } });
  graphInstance = new vis.Network(container, { nodes: nodes, edges: edges }, options);
  graphInstance.on('click', function(params) {
    if (params.nodes && params.nodes.length && params.nodes[0] !== c.concept_id) openConcept(params.nodes[0]);
  });
}

/* Global Graph */
function buildLegend() {
  var legend = qs('graph-legend');
  var typeColors = { Function: '#3B82F6', Class: '#10B981', Module: '#8B5CF6', Dependency: '#F59E0B', Interface: '#06B6D4', Enum: '#EC4899', Constant: '#6B7280', Variable: '#6B7280', Method: '#84CC16' };
  var html = '';
  Object.keys(typeColors).forEach(function(k) {
    html += '<div class="graph-legend-item"><span class="dot" style="background:' + typeColors[k] + '"></span><span class="lbl">' + k + '</span></div>';
  });
  legend.innerHTML = html;
}

async function loadGlobalGraph() {
  if (globalGraphData) { renderGlobalGraph(globalGraphData); return; }
  var view = qs('global-graph-view');
  globalGraphData = await api('/api/graph?max_nodes=120');
  renderGlobalGraph(globalGraphData);
}

function renderGlobalGraph(data) {
  var container = qs('global-graph-view');
  if (!data.nodes || data.nodes.length === 0) {
    container.innerHTML = '<div class="loading">No concepts to display</div>';
    return;
  }
  container.innerHTML = '';
  var typeColors = { Function: '#3B82F6', Class: '#10B981', Module: '#8B5CF6', Dependency: '#F59E0B', Interface: '#06B6D4', Enum: '#EC4899', Constant: '#6B7280', Variable: '#6B7280', Method: '#84CC16' };
  var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  var nodes = new vis.DataSet(data.nodes.map(function(n) {
    return { id: n.id, label: n.label, title: n.title, group: n.group, color: typeColors[n.group] || '#6366F1' };
  }));
  var edges = new vis.DataSet(data.edges.map(function(e) {
    return { from: e.from, to: e.to, title: e.type, color: { color: isDark ? '#475569' : '#CBD5E1' }, arrows: { to: { enabled: true, scaleFactor: 0.5 } }, width: 0.5 };
  }));
  if (globalGraphInstance) globalGraphInstance.destroy();
  var options = {
    physics: { solver: 'forceAtlas2Based', forceAtlas2Based: { gravitationalConstant: -30, centralGravity: 0.003, springLength: 150, springConstant: 0.05, damping: 0.4 }, stabilization: { iterations: 100 } },
    edges: { smooth: { type: 'continuous' } },
    nodes: { shape: 'dot', size: 15, font: { color: isDark ? '#E2E8F0' : '#334155', size: 10, face: 'Inter' }, borderWidth: 0, chosen: true },
    interaction: { hover: true, tooltipDelay: 150, navigationButtons: true, keyboard: true },
    groups: Object.fromEntries(Object.entries(typeColors).map(function(e) { return [e[0], { color: { background: e[1], border: e[1] }, shape: 'dot' }]; })),
    background: isDark ? '#0F172A' : '#F8FAFC'
  };
  globalGraphInstance = new vis.Network(container, { nodes: nodes, edges: edges }, options);
  globalGraphInstance.on('click', function(params) {
    if (params.nodes && params.nodes.length) openConcept(params.nodes[0]);
  });
  globalGraphInstance.on('doubleClick', function(params) {
    if (params.nodes && params.nodes.length) switchTab('browse', document.querySelector('.tab[onclick*="browse"]'));
  });
}

/* Tab switching */
function switchTab(name, btn) {
  document.querySelectorAll('#tabs .tab').forEach(function(t) { t.classList.remove('active'); t.setAttribute('aria-selected','false'); });
  btn.classList.add('active'); btn.setAttribute('aria-selected','true');
  document.querySelectorAll('#main > .tab-content').forEach(function(t) { t.classList.remove('active'); });
  qs('tab-' + name).classList.add('active');
  if (name === 'graph') { loadGlobalGraph(); if (globalGraphInstance) setTimeout(function() { globalGraphInstance.fit(); }, 300); }
}

function switchDetailTab(name, btn) {
  if (!btn) { btn = document.querySelector('#detail-tabs .dtab'); name = 'dmain'; }
  document.querySelectorAll('#detail-tabs .dtab').forEach(function(t) { t.classList.remove('active'); t.setAttribute('aria-selected','false'); });
  btn.classList.add('active'); btn.setAttribute('aria-selected','true');
  document.querySelectorAll('#detail-panel .dtab-content').forEach(function(t) { t.classList.remove('active'); });
  qs('dtab-' + name).classList.add('active');
  if (name === 'dgraph' && graphInstance) setTimeout(function() { graphInstance.fit(); }, 100);
}

function closeDetail() {
  qs('detail-panel').classList.remove('active');
  qs('welcome').style.display = 'flex';
  document.querySelectorAll('.concept-item.active').forEach(function(el) { el.classList.remove('active'); });
  currentId = null;
}

/* Keyboard shortcuts */
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape' && qs('detail-panel').classList.contains('active')) closeDetail();
  if (e.key === '/' && !e.ctrlKey && !e.metaKey) { qs('search-input').focus(); e.preventDefault(); }
});

/* Theme sync for graph */
var _origToggle = toggleTheme;
toggleTheme = function() {
  _origToggle();
  if (graphInstance) { var c = conceptCache[currentId]; if (c) renderSubgraph(c); }
  if (globalGraphData) renderGlobalGraph(globalGraphData);
};
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
