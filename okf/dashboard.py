"""okf dashboard — FastAPI live bundle browser with interactive concept graph.

Usage:
  okf dashboard <bundle_dir> [--port PORT] [--host HOST] [--open]
"""

import argparse
import re
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

TEMPLATE_PATH = Path(__file__).parent / "templates" / "viz-template.html"


def _resolve_source(bundle_dir: Path, resource: str, line_range: str) -> str:
    """Read source code from original file using line range from concept."""
    if not resource or not line_range:
        return ""
    import re
    m = re.search(r"Lines (\d+)\s*[–-]\s*(\d+)", line_range)
    if not m:
        return ""
    start, end = int(m.group(1)), int(m.group(2))

    # Find source root from bundle index.md
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


def build_app(bundle_dir: Path, graph_max_nodes: int = 2000, token: str | None = None):
    from okf.storage import open_store

    store = open_store(bundle_dir)

    app = FastAPI(title="OKF Dashboard", version="0.1")
    app.state.concept_count = store.get_info()["total"]
    app.state.store = store
    app.state.graph_max_nodes = graph_max_nodes

    # Block cross-origin reads (localhost CSRF / data exfiltration). Only the
    # dashboard's own origin (and loopback origins) may fetch the API.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[],  # no external origins
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$",
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=[],
    )

    @app.middleware("http")
    async def _auth_guard(request, call_next):
        if token:
            auth = request.headers.get("Authorization", "")
            if not (auth.startswith("Bearer ") and auth[7:] == token):
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Unauthorized")
        return await call_next(request)

    @app.get("/api/info")
    def bundle_info():
        info = store.get_info()
        info["name"] = bundle_dir.name
        return info

    @app.get("/api/types")
    def list_types():
        return store.get_types()

    @app.get("/api/languages")
    def list_languages():
        return store.get_languages()

    @app.get("/api/search")
    def search(
        q: str = Query("", description="Search query"),
        type_filter: str = Query("", alias="type", description="Filter by type"),
        tag: str = Query("", description="Filter by tag"),
        limit: int = Query(80, description="Max results"),
    ):
        tag_filters = [tag] if tag else []
        results = store.search(query=q, type_filter=type_filter, tag_filters=tag_filters, limit=limit)
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
        c = store.get(concept_id)
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
            "source": _resolve_source(bundle_dir, c.get("resource", ""), sections.get("source", "")),
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
    def graph(max_nodes: int = Query(200)):
        g = store.get_graph(max_nodes=max_nodes)
        return g

    @app.get("/")
    def index():
        html = TEMPLATE_PATH.read_text(encoding="utf-8")
        html = html.replace("{DYNAMIC_FLAG}", "true")
        html = html.replace("{BUNDLE_DATA}", "null")
        html = html.replace("{GRAPH_MAX_NODES}", str(graph_max_nodes))
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
    parser.add_argument("--token", default=None,
                        help="Require this token (Authorization: Bearer) for all requests")
    parser.add_argument("--open", "-o", action="store_true", help="Open browser automatically")
    parser.add_argument("--memory", action="store_true", help="Force in-memory mode (no SQLite)")
    parser.add_argument("--graph-nodes", type=int, default=2000, help="Max nodes in graph view (default: 2000)")
    args = parser.parse_args()

    bundle_dir = Path(args.bundle_dir).resolve()
    if not bundle_dir.exists():
        print(f"ERROR: Bundle not found: {bundle_dir}", file=sys.stderr)
        sys.exit(1)

    host = args.host
    if host not in {"127.0.0.1", "localhost", "::1"} and not host.startswith("127.") and not args.token:
        print(
            "ERROR: binding to a non-loopback host requires --token <secret> "
            "so the dashboard is not publicly readable.",
            file=sys.stderr,
        )
        sys.exit(1)

    app = build_app(bundle_dir, graph_max_nodes=args.graph_nodes, token=args.token)
    url = f"http://{host}:{args.port}"
    print(f"  OKF Dashboard: {url}")
    print(f"  Bundle: {bundle_dir.name} ({app.state.concept_count} concepts)")
    if args.token:
        print("  Token auth enabled (send Authorization: Bearer <token>).")

    if args.open:
        import webbrowser
        webbrowser.open(url)

    uvicorn.run(app, host=host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
