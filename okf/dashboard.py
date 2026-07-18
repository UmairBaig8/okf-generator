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

TEMPLATE_PATH = Path(__file__).parent / "templates" / "viz-template.html"


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
        def _bullets(text: str) -> list[str]:
            if not text:
                return []
            return [re.sub(r'^-\s*`?|`$', '', line).strip() for line in text.strip().splitlines()
                    if line.strip().startswith('- ')]
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
            "visibility": _bullets(sections.get("visibility", "")),
            "decorators": _bullets(sections.get("decorators", "")),
            "inheritance": _bullets(sections.get("inheritance", "")),
            "type_params": _bullets(sections.get("type_parameters", "")),
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
        # If no relationships found, fall back to showing all non-Dependency concepts
        if not top_ids:
            for c in concepts:
                if c["type"] != "Dependency" and len(top_ids) < max_nodes:
                    top_ids.add(c["concept_id"])
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
        html = TEMPLATE_PATH.read_text(encoding="utf-8")
        html = html.replace("{DYNAMIC_FLAG}", "true")
        html = html.replace("{BUNDLE_DATA}", "null")
        return HTMLResponse(html)

    return app


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
