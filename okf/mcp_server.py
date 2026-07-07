"""okf mcp — Model Context Protocol server for OKF bundles.

Lets any MCP-compatible agent (Claude Desktop, Cursor, etc.)
browse and search bundle concepts natively over stdio.

Usage:
  okf mcp [bundle_dir]              Start MCP server (stdio mode, default: ./okf_bundle)
  okf mcp [bundle_dir] --port 9000  Start MCP server (HTTP+SSE mode)
  okf mcp --bundle <path>           Explicit bundle path

Tools:
  lookup              Search concepts by name/type/tag
  get_concept         Full detail by concept_id
  find_callers        Concepts that reference a given concept_id
  find_callees        Concepts that a given concept_id references (forward edge)
  list_by_file        Concepts extracted from a source file
  list_dependencies   List dependency concepts
  bundle_info         Bundle statistics
  list_by_type        List concepts of a specific type
  search_by_tag       List concepts matching a tag prefix (e.g. lang:python, ecosystem:pip)
  get_related         Get concepts related (called/referenced) by a given concept
  get_manifest_source Get manifest file info for a dependency concept
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def jsonrpc(id: int | str, result: Any = None, error: dict | None = None) -> str:
    msg = {"jsonrpc": "2.0", "id": id}
    if error:
        msg["error"] = error
    else:
        msg["result"] = result
    return json.dumps(msg, ensure_ascii=False)


class ToolError(Exception):
    """Raised inside handle_tool_call to produce a structured MCP error."""
    def __init__(self, message: str, code: int = -32000):
        self.code = code
        self.message = message


# ═══════════════════════════════════════════════════════════════════════════
# MCP Server
# ═══════════════════════════════════════════════════════════════════════════


class BundleMCPServer:
    """Minimal MCP server that exposes an OKF bundle as resources + tools."""

    def __init__(self, bundle_dir: Path):
        from okf.lookup import load_bundle
        self.bundle_dir = bundle_dir
        self.concepts = load_bundle(bundle_dir)
        self.req_id = 0

    # ── Helpers ─────────────────────────────────────────────────────────

    def _require(self, args: dict, key: str, typ: type = str) -> Any:
        val = args.get(key)
        if val is None:
            raise ToolError(f"Missing required argument: '{key}'")
        if not isinstance(val, typ):
            raise ToolError(f"Argument '{key}' must be {typ.__name__}, got {type(val).__name__}")
        return val

    def _build_callers_index(self) -> dict[str, list[dict]]:
        """Build {referenced_cid: [concepts_that_reference_it]} from all concepts."""
        idx: dict[str, list[dict]] = {}
        for c in self.concepts:
            related_text = c.get("sections", {}).get("related", "")
            refs = re.findall(r"\]\(/(.+?)\.md\)", related_text)
            for ref in refs:
                idx.setdefault(ref, []).append(c)
        return idx

    def _build_callees_index(self) -> dict[str, list[dict]]:
        """Build {caller_cid: [concepts_it_references]} from all concepts."""
        idx: dict[str, list[dict]] = {}
        for c in self.concepts:
            related_text = c.get("sections", {}).get("related", "")
            refs = re.findall(r"\]\(/(.+?)\.md\)", related_text)
            if refs:
                idx[c["concept_id"]] = [
                    {"concept_id": ref, "title": ref.split("/")[-1]}
                    for ref in refs
                ]
        return idx

    def _concept_detail(self, c: dict) -> dict:
        """Build a rich detail dict from a concept."""
        sections = c.get("sections", {})
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
            "related": sections.get("related", ""),
        }

    # ── Resource handlers ───────────────────────────────────────────────

    def list_resources(self) -> list[dict]:
        resources = []
        for c in self.concepts:
            uri = f"okf://{c['concept_id']}"
            resources.append({
                "uri": uri,
                "name": c["title"],
                "description": c.get("description", "")[:120],
                "mimeType": "text/markdown",
            })
        return resources

    def read_resource(self, uri: str) -> str:
        cid = uri.replace("okf://", "", 1)
        for c in self.concepts:
            if c["concept_id"] == cid:
                return c.get("raw", f"# {c['title']}\n\n{c.get('description', '')}")
        return ""

    # ── Tool handlers ───────────────────────────────────────────────────

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": "lookup",
                "description": "Search concepts by name, type, or tag. Returns compact results by default; set detail=true for full fields (signature, params, etc.)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query (space-separated tokens, fuzzy)"},
                        "type": {"type": "string", "description": "Filter by concept type", "enum": ["", "Class", "Function", "Module", "Dependency"]},
                        "tag": {"type": "string", "description": "Filter by tag (e.g. lang:python, ecosystem:pip)"},
                        "limit": {"type": "integer", "description": "Max results (default 10)"},
                        "detail": {"type": "boolean", "description": "Return full detail (signature, params, etc.)"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "get_concept",
                "description": "Get full detail for a single concept by concept_id (e.g. 'utils/slugify' or '_dependencies/pip/requests')",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "concept_id": {"type": "string", "description": "Concept ID (path relative to bundle root, no .md extension)"},
                    },
                    "required": ["concept_id"],
                },
            },
            {
                "name": "find_callers",
                "description": "List all concepts that reference (call, import, or link to) a given concept_id",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "concept_id": {"type": "string", "description": "Target concept_id to find callers for"},
                    },
                    "required": ["concept_id"],
                },
            },
            {
                "name": "list_by_file",
                "description": "List all concepts extracted from a specific source file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string", "description": "Source file path (e.g. 'utils.py' or 'src/main.ts')"},
                    },
                    "required": ["file"],
                },
            },
            {
                "name": "list_dependencies",
                "description": "List all dependency concepts, optionally filtered by ecosystem",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ecosystem": {"type": "string", "description": "Filter by ecosystem (pip, npm, cargo, go, etc.)"},
                    },
                },
            },
            {
                "name": "bundle_info",
                "description": "Get bundle statistics (total concepts, breakdown by type and language)",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "list_by_type",
                "description": "List all concepts of a specific type",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "description": "Concept type", "enum": ["Class", "Function", "Module", "Dependency"]},
                    },
                    "required": ["type"],
                },
            },
            {
                "name": "find_callees",
                "description": "List all concepts that a given concept references (calls, imports, or links to) — forward edge, opposite of find_callers",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "concept_id": {"type": "string", "description": "Caller concept_id to find callees for"},
                    },
                    "required": ["concept_id"],
                },
            },
            {
                "name": "search_by_tag",
                "description": "List all concepts matching a tag prefix (e.g. lang:python, ecosystem:pip, domain:api, manifest:pyproject.toml)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tag": {"type": "string", "description": "Tag prefix to match (e.g. 'lang:python', 'ecosystem:')"},
                        "limit": {"type": "integer", "description": "Max results (default 50)"},
                    },
                    "required": ["tag"],
                },
            },
            {
                "name": "get_related",
                "description": "Get concepts semantically related to or referenced by a given concept_id. Returns both related links and called-by edges.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "concept_id": {"type": "string", "description": "Concept_id to find related concepts for"},
                    },
                    "required": ["concept_id"],
                },
            },
            {
                "name": "get_manifest_source",
                "description": "Get the manifest file (e.g. requirements.txt, Cargo.toml, package.json) that declared a dependency. Only works for Dependency-type concepts.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "concept_id": {"type": "string", "description": "Dependency concept_id (e.g. '_dependencies/pip/requests')"},
                    },
                    "required": ["concept_id"],
                },
            },
        ]

    def handle_tool_call(self, name: str, args: dict) -> Any:
        try:
            return self._dispatch(name, args)
        except ToolError as e:
            return {"error": {"code": e.code, "message": e.message}}

    def _dispatch(self, name: str, args: dict) -> Any:
        if name == "lookup":
            from okf.lookup import search
            tokens = args.get("query", "").split()
            if not tokens:
                raise ToolError("query is required")
            type_filter = args.get("type", "")
            tag_filters = [args["tag"]] if args.get("tag") else []
            results = search(self.concepts, tokens=tokens, type_filter=type_filter, tag_filters=tag_filters, limit=args.get("limit", 10))
            detail = args.get("detail", False)
            if detail:
                return [self._concept_detail(c) for c in results]
            return [{"title": c["title"], "type": c["type"], "description": c.get("description", ""), "resource": c.get("resource", "")} for c in results]

        if name == "get_concept":
            cid = self._require(args, "concept_id")
            for c in self.concepts:
                if c["concept_id"] == cid:
                    return self._concept_detail(c)
            raise ToolError(f"Concept not found: {cid}", code=-32001)

        if name == "find_callers":
            target = self._require(args, "concept_id")
            idx = self._build_callers_index()
            callers = idx.get(target, [])
            return [{"concept_id": c["concept_id"], "title": c["title"], "type": c["type"], "resource": c.get("resource", "")} for c in callers]

        if name == "list_by_file":
            file_path = self._require(args, "file")
            results = [c for c in self.concepts if file_path in c.get("resource", "")]
            if not results:
                return []
            return [{"concept_id": c["concept_id"], "title": c["title"], "type": c["type"], "resource": c.get("resource", "")} for c in results]

        if name == "list_dependencies":
            deps = [c for c in self.concepts if c["type"] == "Dependency"]
            eco = args.get("ecosystem", "")
            if eco:
                deps = [c for c in deps if any(eco in t for t in c.get("tags", []))]
            return [{"title": c["title"], "resource": c.get("resource", ""), "description": c.get("description", "")} for c in deps]

        if name == "bundle_info":
            types: dict[str, int] = {}
            langs: dict[str, int] = {}
            for c in self.concepts:
                types[c["type"]] = types.get(c["type"], 0) + 1
                for t in c.get("tags", []):
                    if t.startswith("lang:"):
                        lang = t[5:]
                        langs[lang] = langs.get(lang, 0) + 1
            return {"name": self.bundle_dir.name, "total": len(self.concepts), "types": types, "languages": langs}

        if name == "list_by_type":
            ctype = self._require(args, "type")
            return [{"title": c["title"], "resource": c.get("resource", ""), "description": c.get("description", "")} for c in self.concepts if c["type"] == ctype]

        if name == "find_callees":
            cid = self._require(args, "concept_id")
            idx = self._build_callees_index()
            callees = idx.get(cid, [])
            return callees

        if name == "search_by_tag":
            tag_prefix = self._require(args, "tag")
            limit = args.get("limit", 50)
            results = []
            for c in self.concepts:
                for t in c.get("tags", []):
                    if t.startswith(tag_prefix):
                        results.append({
                            "title": c["title"],
                            "type": c["type"],
                            "concept_id": c["concept_id"],
                            "resource": c.get("resource", ""),
                            "description": c.get("description", ""),
                        })
                        break
                if len(results) >= limit:
                    break
            return results

        if name == "get_related":
            cid = self._require(args, "concept_id")
            for c in self.concepts:
                if c["concept_id"] != cid:
                    continue
                sec = c.get("sections", {})
                related = sec.get("related", "")
                sem = sec.get("related_semantic", "")
                # Parse related markdown links into structured results
                refs = re.findall(r"\[(.+?)\]\(/(.+?)\.md\)", related)
                related_concepts = [
                    {"title": t, "concept_id": cid2}
                    for t, cid2 in refs
                ]
                semantic_concepts = []
                if sem:
                    sem_refs = re.findall(r"\[(.+?)\]\(/(.+?)\.md\)", sem)
                    semantic_concepts = [
                        {"title": t, "concept_id": cid2}
                        for t, cid2 in sem_refs
                    ]
                return {
                    "related": related_concepts,
                    "related_semantic": semantic_concepts,
                }
            raise ToolError(f"Concept not found: {cid}", code=-32001)

        if name == "get_manifest_source":
            cid = self._require(args, "concept_id")
            for c in self.concepts:
                if c["concept_id"] != cid:
                    continue
                if c["type"] != "Dependency":
                    raise ToolError(f"Not a Dependency concept: {cid}")
                tags = c.get("tags", [])
                ecosystem = next((t.split(":", 1)[1] for t in tags if t.startswith("ecosystem:")), "")
                manifest = next((t.split(":", 1)[1] for t in tags if t.startswith("manifest:")), "")
                return {
                    "concept_id": cid,
                    "title": c["title"],
                    "manifest_file": manifest,
                    "source_file": c.get("resource", ""),
                    "ecosystem": ecosystem,
                }
            raise ToolError(f"Dependency not found: {cid}", code=-32001)

        raise ToolError(f"Unknown tool: {name}", code=-32601)

    # ── JSON-RPC dispatch ────────────────────────────────────────────────

    def handle_request(self, raw: str) -> str | None:
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            return None

        rid = msg.get("id", 0)
        method = msg.get("method", "")
        params = msg.get("params", {}) or {}

        if method == "initialize":
            return jsonrpc(rid, {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "resources": {"listChanged": False},
                    "tools": {"listChanged": False},
                },
                "serverInfo": {"name": "okf-mcp", "version": "0.1"},
            })

        if method == "notifications/initialized":
            return None

        if method == "resources/list":
            return jsonrpc(rid, {"resources": self.list_resources()})

        if method == "resources/read":
            uri = params.get("uri", "")
            content = self.read_resource(uri)
            return jsonrpc(rid, [{"uri": uri, "mimeType": "text/markdown", "text": content}])

        if method == "tools/list":
            return jsonrpc(rid, {"tools": self.list_tools()})

        if method == "tools/call":
            result = self.handle_tool_call(params.get("name", ""), params.get("arguments", {}))
            return jsonrpc(rid, {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]})

        return jsonrpc(rid, None, {"code": -32601, "message": f"Method not found: {method}"})

    def run_stdio(self):
        """Read JSON-RPC requests from stdin, write responses to stdout."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            resp = self.handle_request(line)
            if resp:
                sys.stdout.write(resp + "\n")
                sys.stdout.flush()

    def run_http(self, port: int):
        """Simple HTTP+SSE server for MCP over HTTP."""
        from http.server import HTTPServer, BaseHTTPRequestHandler

        class MCPHTTPHandler(BaseHTTPRequestHandler):
            server_ref = None

            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode()
                resp = self.server_ref.handle_request(body) if self.server_ref else None
                if resp:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(resp.encode())
                else:
                    self.send_response(202)
                    self.end_headers()

            def log_message(self, format, *args):
                pass

        MCPHTTPHandler.server_ref = self
        server = HTTPServer(("127.0.0.1", port), MCPHTTPHandler)
        print(f"MCP server listening on http://127.0.0.1:{port}/mcp", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
            sys.exit(0)


def _install_mcp_config(bundle_dir: Path):
    """Register MCP server in detected client configs."""
    import json, os
    abs_bundle = str(bundle_dir.resolve())
    okf_path = shutil.which("okf") or ""
    if not okf_path:
        print("WARNING: okf not found in PATH — MCP config will use bare 'okf' command", file=sys.stderr)
        okf_path = "okf"

    mcp_entry = {
        "command": okf_path,
        "args": ["mcp", abs_bundle],
    }

    written = []

    # ── OpenCode (project opencode.json / opencode.jsonc) ──
    for cfg_name in ("opencode.json", "opencode.jsonc"):
        cfg_path = Path.cwd() / cfg_name
        if cfg_path.exists():
            try:
                data = json.loads(cfg_path.read_text(encoding="utf-8"))
            except Exception:
                data = {}
            data.setdefault("mcp", {})["okf-generator"] = {
                "type": "local",
                "command": [okf_path, "mcp", abs_bundle],
                "enabled": True,
            }
            cfg_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            written.append(f"OpenCode ({cfg_path})")
            break
    else:
        # No config file exists — create opencode.json
        cfg_path = Path.cwd() / "opencode.json"
        data = {
            "$schema": "https://opencode.ai/config.json",
            "mcp": {
                "okf-generator": {
                    "type": "local",
                    "command": [okf_path, "mcp", abs_bundle],
                    "enabled": True,
                }
            },
        }
        cfg_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        written.append(f"OpenCode (created {cfg_path})")

    # ── Claude Desktop (claude_desktop_config.json) ──
    claude_candidates = [
        Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
        Path.home() / ".config" / "Claude" / "claude_desktop_config.json",
        Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
    ]
    claude_path = None
    for p in claude_candidates:
        if p.exists():
            claude_path = p
            break
    if claude_path:
        try:
            data = json.loads(claude_path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        data.setdefault("mcpServers", {})["okf-generator"] = mcp_entry
        claude_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        written.append(f"Claude Desktop ({claude_path})")

    if written:
        print(f"MCP server registered for: {', '.join(written)}")
        print("Restart your MCP client to pick up the changes.")
    else:
        print("No MCP clients detected. Created opencode.json for OpenCode.")
        print("For other clients, see: https://umairbaig8.github.io/okf-generator/docs-site/user-guide/mcp-server/")


def main():
    parser = argparse.ArgumentParser(
        description="MCP server for OKF bundles.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("bundle_dir", nargs="?", default="./okf_bundle", help="Path to OKF bundle directory (default: ./okf_bundle)")
    parser.add_argument("--bundle", help="Path to OKF bundle (overrides positional)")
    parser.add_argument("--port", "-p", type=int, default=0, help="HTTP port (omit or 0 for stdio mode)")
    parser.add_argument("--install", action="store_true", help="Register MCP server in detected client configs (opencode.json, claude_desktop_config.json) then exit")
    args = parser.parse_args()

    bundle_dir = Path(args.bundle or args.bundle_dir).resolve()

    if args.install:
        if not bundle_dir.exists():
            print(f"WARNING: Bundle not found at {bundle_dir}. MCP config will still be written but the server won't start until you generate a bundle.", file=sys.stderr)
        _install_mcp_config(bundle_dir)
        return

    if not bundle_dir.exists():
        print(f"ERROR: Bundle not found: {bundle_dir}", file=sys.stderr)
        sys.exit(1)

    server = BundleMCPServer(bundle_dir)
    print(f"MCP server ready — {len(server.concepts)} concepts from {bundle_dir.name}", file=sys.stderr)

    if args.port:
        server.run_http(args.port)
    else:
        server.run_stdio()
