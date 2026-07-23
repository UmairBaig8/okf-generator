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
  trace_path          BFS call chain traversal (inbound/outbound) with depth limit
  detect_changes      Compare current bundle against a reference (path or git ref)
  get_architecture    Bundle overview: languages, packages, hotspot concepts
  check_index_coverage Verify specific source files are indexed in the bundle
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
import os
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
        self._call_graph: dict[str, dict] | None = None

    # ── Helpers ─────────────────────────────────────────────────────────

    def _require(self, args: dict, key: str, typ: type = str) -> Any:
        val = args.get(key)
        if val is None:
            raise ToolError(f"Missing required argument: '{key}'")
        if not isinstance(val, typ):
            raise ToolError(f"Argument '{key}' must be {typ.__name__}, got {type(val).__name__}")
        return val

    def _parse_relationship_table(self, table_text: str) -> dict[str, list[str]]:
        """Parse a markdown relationship table into {type: [concept_ids]}.

        Table format:
        | Type     | Target                |
        |----------|-----------------------|
        | calls    | [get](//get.md)       |
        | called_by| [main](//main.md)     |
        """
        result: dict[str, list[str]] = {}
        for line in table_text.splitlines():
            if "|" not in line or "---" in line:
                continue
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if len(cols) < 2:
                continue
            rel_type = cols[0].strip().lower()
            target_match = re.search(r"\]\(/(.+?)\.md\)", cols[1])
            if target_match:
                result.setdefault(rel_type, []).append(target_match.group(1))
        return result

    def _build_call_graph(self) -> dict[str, dict]:
        """Build full call graph from all concepts.

        Call/called_by edges come from ## Calls and ## Called By sections
        (bullet lists of [title](//concept_id.md) links).

        Returns {concept_id: {calls: [cid, ...], called_by: [cid, ...]}}
        """
        if self._call_graph is not None:
            return self._call_graph

        graph: dict[str, dict] = {}
        for c in self.concepts:
            cid = c["concept_id"]
            graph.setdefault(cid, {"calls": [], "called_by": []})

        _link_re = re.compile(r"\]\(/(.+?)\.md\)")

        for c in self.concepts:
            cid = c["concept_id"]
            sections = c.get("sections", {})

            callee_ids = _link_re.findall(sections.get("calls", ""))
            for callee_id in callee_ids:
                if callee_id not in graph[cid]["calls"]:
                    graph[cid]["calls"].append(callee_id)
                graph.setdefault(callee_id, {"calls": [], "called_by": []})
                if cid not in graph[callee_id]["called_by"]:
                    graph[callee_id]["called_by"].append(cid)

            caller_ids = _link_re.findall(sections.get("called by", ""))
            for caller_id in caller_ids:
                graph.setdefault(caller_id, {"calls": [], "called_by": []})
                if cid not in graph[caller_id]["calls"]:
                    graph[caller_id]["calls"].append(cid)
                if caller_id not in graph[cid]["called_by"]:
                    graph[cid]["called_by"].append(caller_id)

            # Also index plain "related" section (list of related concept links)
            related_text = sections.get("related", "") or sections.get("relationships", "")
            for ref_id in _link_re.findall(related_text):
                graph.setdefault(ref_id, {"calls": [], "called_by": []})

        self._call_graph = graph
        return graph

    def _build_callers_index(self) -> dict[str, list[dict]]:
        """Build {referenced_cid: [concepts_that_reference_it]} from all concepts."""
        idx: dict[str, list[dict]] = {}
        for c in self.concepts:
            secs = c.get("sections", {})
            related_text = secs.get("relationships", "") or secs.get("related", "")
            refs = re.findall(r"\]\(/(.+?)\.md\)", related_text)
            for ref in refs:
                idx.setdefault(ref, []).append(c)
        return idx

    def _build_callees_index(self) -> dict[str, list[dict]]:
        """Build {caller_cid: [concepts_it_references]} from all concepts."""
        idx: dict[str, list[dict]] = {}
        for c in self.concepts:
            secs = c.get("sections", {})
            related_text = secs.get("relationships", "") or secs.get("related", "")
            refs = re.findall(r"\]\(/(.+?)\.md\)", related_text)
            if refs:
                idx[c["concept_id"]] = [
                    {"concept_id": ref, "title": ref.split("/")[-1]}
                    for ref in refs
                ]
        return idx

    def _concept_detail(self, c: dict, compact: bool = False) -> dict:
        """Build a rich detail dict from a concept.

        If compact=True (TOON-lite), returns a token-efficient format
        with minimal keys and shortened field names.
        """
        sections = c.get("sections", {})
        if compact:
            return {
                "id": c["concept_id"],
                "t": c["title"],
                "y": c["type"],
                "f": c.get("resource", ""),
                "d": c.get("description", "")[:200],
                "sig": sections.get("signature", "")[:120],
            }
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
                        "compact": {"type": "boolean", "description": "Return TOON-lite compact format (shorter keys, less tokens)"},
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
            {
                "name": "trace_path",
                "description": "BFS call chain traversal from a concept. Follows calls (outbound) or called_by (inbound) edges up to a configurable depth. Returns ordered path chains.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "concept_id": {"type": "string", "description": "Starting concept_id for traversal"},
                        "direction": {"type": "string", "description": "Traversal direction: 'outbound' (follows calls) or 'inbound' (follows called_by)", "enum": ["outbound", "inbound"]},
                        "depth": {"type": "integer", "description": "Maximum traversal depth (default: 3, max: 10)"},
                        "compact": {"type": "boolean", "description": "Return TOON-lite compact format (smaller tokens)"},
                    },
                    "required": ["concept_id", "direction"],
                },
            },
            {
                "name": "detect_changes",
                "description": "Detect changes between current bundle and a reference (previous bundle path, git reference, or manifest snapshot). Returns added/removed/changed concepts with optional impact analysis.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "reference": {"type": "string", "description": "Path to reference bundle OR git ref (e.g. 'HEAD~1', 'main'). If omitted, compares against stored manifest snapshot."},
                        "kind": {"type": "string", "description": "Comparison kind: 'bundle' (compare two bundles) or 'git' (git diff of source)", "enum": ["bundle", "git"]},
                        "impact": {"type": "boolean", "description": "Include dependency impact analysis (trace dep changes to affected modules)"},
                        "compact": {"type": "boolean", "description": "Return compact format (smaller tokens)"},
                    },
                },
            },
            {
                "name": "get_architecture",
                "description": "Get high-level architecture overview of the indexed codebase: languages, packages, concept hotspots, dependency count, and type breakdown.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "compact": {"type": "boolean", "description": "Return compact format (smaller tokens)"},
                    },
                },
            },
            {
                "name": "check_index_coverage",
                "description": "Verify whether specific source files were indexed in the bundle. Accepts a list of file paths and returns which are present and which are missing.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "files": {"type": "array", "items": {"type": "string"}, "description": "List of source file paths to check (e.g. ['src/main.py', 'utils/helpers.ts'])"},
                    },
                    "required": ["files"],
                },
            },
        ]

    def handle_tool_call(self, name: str, args: dict) -> Any:
        try:
            return self._dispatch(name, args)
        except ToolError as e:
            return {"error": {"code": e.code, "message": e.message}}

    def _format_diff(self, result: dict, do_impact: bool, new_list: list, old_list: list, compact: bool) -> dict:
        """Format diff result, optionally with impact analysis, in compact or full mode."""
        from okf.diff import impact_analysis as _impact
        output = {
            "old_concepts": result["old_count"],
            "new_concepts": result["new_count"],
            "added": len(result["added"]),
            "removed": len(result["removed"]),
            "changed": len(result["changed"]),
        }
        if compact:
            if result["added"]:
                output["added_list"] = [{"t": c["title"], "y": c["type"]} for c in result["added"][:15]]
            if result["removed"]:
                output["removed_list"] = [{"t": c["title"], "y": c["type"]} for c in result["removed"][:15]]
            if result["changed"]:
                output["changed_list"] = [{"t": c["title"], "y": c["type"], "changes": list(c.get("changes", {}).keys())} for c in result["changed"][:15]]
        else:
            output["added"] = result["added"]
            output["removed"] = result["removed"]
            output["changed"] = result["changed"]
        if do_impact:
            impact = _impact(old_list, new_list, result)
            output["impact"] = {
                "total_impacted_modules": impact["total_impacted_modules"],
                "total_impacted_code_concepts": impact["total_impacted_code_concepts"],
            }
            if compact:
                if impact.get("changed_deps"):
                    output["impact"]["dep_changes"] = [
                        {"t": d["title"], "old_v": d.get("old_version", ""), "new_v": d.get("new_version", ""),
                         "modules": d["total_modules"], "concepts": d["total_code_concepts"]}
                        for d in impact.get("changed_deps", [])[:10]
                    ]
            else:
                output["impact"]["details"] = impact
        return output

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
            compact = args.get("compact", False)
            if compact:
                return [self._concept_detail(c, compact=True) for c in results]
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

        if name == "trace_path":
            cid = self._require(args, "concept_id")
            direction = self._require(args, "direction")
            depth = min(args.get("depth", 3), 10)
            compact = args.get("compact", False)
            graph = self._build_call_graph()

            if cid not in graph:
                raise ToolError(f"Concept not found in call graph: {cid}", code=-32001)

            edge_key = "calls" if direction == "outbound" else "called_by"
            reverse_key = "called_by" if direction == "outbound" else "calls"

            paths: list[list[dict]] = []
            def _bfs(start: str, max_depth: int):
                queue = [(start, [start], 0)]
                visited_at_depth: dict[str, int] = {start: 0}
                while queue:
                    current, path, d = queue.pop(0)
                    if d > 0:
                        paths.append(path)
                    if d >= max_depth:
                        continue
                    for neighbor in graph.get(current, {}).get(edge_key, []):
                        nd = d + 1
                        if neighbor not in visited_at_depth or nd < visited_at_depth[neighbor]:
                            visited_at_depth[neighbor] = nd
                            queue.append((neighbor, path + [neighbor], nd))

            _bfs(cid, depth)

            by_id = {c["concept_id"]: c for c in self.concepts}
            result_chains = []
            seen_chains = set()
            for path in paths:
                chain = []
                for pid in path:
                    c = by_id.get(pid)
                    if c:
                        chain.append(self._concept_detail(c, compact=compact))
                    else:
                        chain.append({"concept_id": pid, "title": pid.split("/")[-1], "type": "?"})
                chain_key = " -> ".join(p["concept_id"] if not compact else p["id"] for p in chain)
                if chain_key not in seen_chains:
                    seen_chains.add(chain_key)
                    result_chains.append(chain)

            root = by_id.get(cid)
            return {
                "root": self._concept_detail(root, compact=compact) if root else {"concept_id": cid},
                "direction": direction,
                "max_depth": depth,
                "paths": result_chains[:50],
                "total_paths_found": len(result_chains),
            }

        if name == "detect_changes":
            reference = args.get("reference", "")
            kind = args.get("kind", "bundle")
            do_impact = args.get("impact", False)
            compact = args.get("compact", False)

            ref_bundle = None
            ref_list = None

            if kind == "git" and reference:
                import subprocess
                from okf.lookup import load_bundle as _load
                source_dir = self.bundle_dir.parent
                try:
                    old_bundle_dir = self.bundle_dir.parent / f".okf_bundle_{reference.replace('/', '_')}"
                    subprocess.run(
                        ["git", "show", f"{reference}:okf_bundle/"],
                        cwd=source_dir, capture_output=True, timeout=10
                    )
                except Exception:
                    pass
                ref_list = _load(self.bundle_dir)
            elif reference:
                ref_dir = Path(reference).resolve()
                if ref_dir.exists():
                    from okf.lookup import load_bundle as _load
                    ref_list = _load(ref_dir)
                    ref_bundle = ref_dir
            else:
                manifest_path = self.bundle_dir / ".okf-manifest.json"
                if manifest_path.exists():
                    try:
                        import json as _json
                        manifest = _json.loads(manifest_path.read_text(encoding="utf-8"))
                        from okf.update import _read_previous_manifest
                        prev = _read_previous_manifest(self.bundle_dir)
                        if prev and prev.get("file_states"):
                            from okf.diff import diff_bundles
                            new_list = self.concepts
                            return self._format_diff(
                                diff_bundles(self.bundle_dir, self.bundle_dir,
                                             old_list=self.concepts, new_list=new_list),
                                do_impact, new_list, self.concepts, compact
                            )
                    except Exception:
                        pass
                raise ToolError("No reference provided and no manifest snapshot found. Pass a reference bundle path or git ref.", code=-32001)

            from okf.diff import diff_bundles, impact_analysis
            new_list = self.concepts
            result = diff_bundles(self.bundle_dir, ref_bundle or self.bundle_dir,
                                  old_list=ref_list, new_list=new_list)
            return self._format_diff(result, do_impact, new_list, ref_list or [], compact)

        if name == "get_architecture":
            compact = args.get("compact", False)
            types: dict[str, int] = {}
            langs: dict[str, int] = {}
            deps = 0
            resources: dict[str, int] = {}
            type_concepts: dict[str, list[dict]] = {}

            for c in self.concepts:
                types[c["type"]] = types.get(c["type"], 0) + 1
                if c["type"] == "Dependency":
                    deps += 1
                res = c.get("resource", "")
                if res:
                    resources[res] = resources.get(res, 0) + 1
                for t in c.get("tags", []):
                    if t.startswith("lang:"):
                        lang = t[5:]
                        langs[lang] = langs.get(lang, 0) + 1
                type_concepts.setdefault(c["type"], []).append(c)

            hotspot_candidates = sorted(
                [(res, count) for res, count in resources.items()],
                key=lambda x: -x[1]
            )[:15]

            hotspots = []
            for res, count in hotspot_candidates:
                concepts_in_file = [
                    {"title": c["title"], "type": c["type"]}
                    for c in self.concepts if c.get("resource") == res
                ]
                hotspots.append({
                    "file": res,
                    "concept_count": count,
                    "concepts": concepts_in_file,
                })

            if compact:
                return {
                    "langs": langs,
                    "total": len(self.concepts),
                    "types": types,
                    "deps": deps,
                    "hotspots": [{"file": h["file"], "count": h["concept_count"]} for h in hotspots[:5]],
                }

            return {
                "name": self.bundle_dir.name,
                "total_concepts": len(self.concepts),
                "languages": langs,
                "by_type": types,
                "dependencies": deps,
                "hotspot_files": hotspots,
            }

        if name == "check_index_coverage":
            files = self._require(args, "files", list)
            indexed_resources = {c.get("resource", "") for c in self.concepts if c.get("resource")}

            def _match(query: str) -> list[str]:
                """Match source file query against indexed resources.
                Tries exact match first, then suffix match (file basename),
                then substring."""
                if query in indexed_resources:
                    return [query]
                basename = query.split("/")[-1]
                exact_base = [r for r in indexed_resources if r == basename]
                if exact_base:
                    return exact_base
                suffix_matches = [r for r in indexed_resources if r.endswith(query) or query.endswith(r)]
                if suffix_matches:
                    return suffix_matches
                substr_matches = [r for r in indexed_resources if query in r or r in query]
                if substr_matches:
                    return substr_matches
                return []

            found = []
            missing = []
            for f in files:
                normalized = f.strip()
                if not normalized:
                    continue
                matches = _match(normalized)
                if matches:
                    for m in matches:
                        concepts_in_file = [
                            {"title": c["title"], "type": c["type"], "concept_id": c["concept_id"]}
                            for c in self.concepts if c.get("resource") == m
                        ]
                        found.append({"file": normalized, "matched_as": m, "concepts": concepts_in_file})
                else:
                    missing.append({"file": normalized})

            return {
                "total_requested": len(files),
                "found": len(found),
                "missing": len(missing),
                "coverage_pct": round(len(found) / max(len(files), 1) * 100, 1),
                "files_found": found,
                "files_missing": missing,
            }

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
            args = params.get("arguments", {}) or {}
            is_compact = args.get("compact", False)
            if is_compact:
                text = json.dumps(result, ensure_ascii=False)
            else:
                text = json.dumps(result, indent=2, ensure_ascii=False)
            return jsonrpc(rid, {"content": [{"type": "text", "text": text}]})

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
        bind = os.environ.get("OKF_MCP_BIND", "127.0.0.1")
        server = HTTPServer((bind, port), MCPHTTPHandler)
        print(f"MCP server listening on http://127.0.0.1:{port}/mcp", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
            sys.exit(0)


def _install_mcp_config(bundle_dir: Path):
    """Register MCP server in detected client configs."""
    import json
    import shutil
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
