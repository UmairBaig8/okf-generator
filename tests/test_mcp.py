"""Tests for okf/mcp_server.py — MCP protocol."""

import json
from pathlib import Path


SAMPLE = Path(__file__).parent / "fixtures" / "realworld" / "python" / "easy"
SAMPLE_V2 = Path(__file__).parent / "fixtures" / "realworld" / "python" / "easy_v2"


def _send(server, msg: dict) -> dict:
    resp = server.handle_request(json.dumps(msg))
    return json.loads(resp) if resp else {}


def _make_server(src, tmp_path):
    from okf.generator import scan_codebase, write_bundle
    from okf.mcp_server import BundleMCPServer
    concepts = scan_codebase(src)
    write_bundle(concepts, tmp_path, "sample", ["test"])
    return BundleMCPServer(tmp_path)


def test_mcp_initialize(tmp_path):
    s = _make_server(SAMPLE, tmp_path)
    resp = _send(s, {"id": 1, "method": "initialize"})
    assert resp.get("result", {}).get("protocolVersion") == "2024-11-05"
    assert "resources" in resp["result"]["capabilities"]
    assert "tools" in resp["result"]["capabilities"]


def test_mcp_tools_list(tmp_path):
    s = _make_server(SAMPLE, tmp_path)
    resp = _send(s, {"id": 1, "method": "tools/list"})
    tools = resp.get("result", [])
    names = {t["name"] for t in tools}
    assert "lookup" in names
    assert "bundle_info" in names
    assert "list_dependencies" in names
    assert "list_by_type" in names
    assert "get_concept" in names
    assert "find_callers" in names
    assert "list_by_file" in names


def test_mcp_tool_bundle_info(tmp_path):
    s = _make_server(SAMPLE, tmp_path)
    resp = _send(s, {"id": 1, "method": "tools/call", "params": {"name": "bundle_info", "arguments": {}}})
    text = resp.get("result", {}).get("content", [{}])[0].get("text", "")
    data = json.loads(text)
    assert data["total"] > 0
    assert "python" in data.get("languages", {})
    assert "Function" in data.get("types", {})


def test_mcp_tool_lookup(tmp_path):
    s = _make_server(SAMPLE, tmp_path)
    resp = _send(s, {"id": 1, "method": "tools/call", "params": {"name": "lookup", "arguments": {"query": "calc"}}})
    text = resp.get("result", {}).get("content", [{}])[0].get("text", "")
    results = json.loads(text)
    assert len(results) > 0


def test_mcp_tool_lookup_detail(tmp_path):
    """lookup with detail=true returns full fields (signature, params, etc.)."""
    s = _make_server(SAMPLE, tmp_path)
    resp = _send(s, {"id": 1, "method": "tools/call", "params": {"name": "lookup", "arguments": {"query": "chunk_list", "detail": True}}})
    text = resp.get("result", {}).get("content", [{}])[0].get("text", "")
    results = json.loads(text)
    assert len(results) == 1
    assert "signature" in results[0]
    assert "parameters" in results[0]
    assert "returns" in results[0]
    assert "source" in results[0]


def test_mcp_tool_get_concept(tmp_path):
    """get_concept returns full detail for a known concept_id."""
    s = _make_server(SAMPLE, tmp_path)
    resp = _send(s, {"id": 1, "method": "tools/call", "params": {"name": "get_concept", "arguments": {"concept_id": "utils/slugify"}}})
    text = resp.get("result", {}).get("content", [{}])[0].get("text", "")
    data = json.loads(text)
    assert data["title"] == "slugify"
    assert data["type"] == "Function"
    assert data["concept_id"] == "utils/slugify"
    assert "signature" in data
    assert "parameters" in data


def test_mcp_tool_get_concept_not_found(tmp_path):
    """get_concept returns structured error for missing concept_id."""
    s = _make_server(SAMPLE, tmp_path)
    resp = _send(s, {"id": 1, "method": "tools/call", "params": {"name": "get_concept", "arguments": {"concept_id": "nonexistent"}}})
    result = resp.get("result", {})
    content = result.get("content", [{}])[0].get("text", "")
    data = json.loads(content)
    assert "error" in data
    assert data["error"]["code"] == -32001


def test_mcp_tool_list_by_file(tmp_path):
    """list_by_file returns all concepts from a source file."""
    s = _make_server(SAMPLE, tmp_path)
    resp = _send(s, {"id": 1, "method": "tools/call", "params": {"name": "list_by_file", "arguments": {"file": "utils.py"}}})
    text = resp.get("result", {}).get("content", [{}])[0].get("text", "")
    results = json.loads(text)
    assert len(results) > 0
    titles = {r["title"] for r in results}
    assert "slugify" in titles
    assert "chunk_list" in titles


def test_mcp_tool_find_callers(tmp_path):
    """find_callers returns concepts that reference a target."""
    # Use v2 which has more cross-references (e.g. batched --> chunk_list)
    from okf.generator import scan_codebase, write_bundle
    from okf.mcp_server import BundleMCPServer
    all_c = scan_codebase(SAMPLE_V2)
    write_bundle(all_c, tmp_path, "sample", ["test"])
    s = BundleMCPServer(tmp_path)

    # Find a concept that has known callers — try utils module
    # which references the functions inside it
    resp = _send(s, {"id": 1, "method": "tools/call", "params": {"name": "find_callers", "arguments": {"concept_id": "utils/chunk_list"}}})
    text = resp.get("result", {}).get("content", [{}])[0].get("text", "")
    results = json.loads(text)
    assert isinstance(results, list)


def test_mcp_tool_missing_args(tmp_path):
    """Tools return structured error for missing required args."""
    s = _make_server(SAMPLE, tmp_path)
    # get_concept without concept_id
    resp = _send(s, {"id": 1, "method": "tools/call", "params": {"name": "get_concept", "arguments": {}}})
    text = resp.get("result", {}).get("content", [{}])[0].get("text", "")
    data = json.loads(text)
    assert "error" in data
    assert "Missing required argument" in data["error"]["message"]

    # lookup without query
    resp = _send(s, {"id": 1, "method": "tools/call", "params": {"name": "lookup", "arguments": {}}})
    text = resp.get("result", {}).get("content", [{}])[0].get("text", "")
    data = json.loads(text)
    assert "error" in data


def test_mcp_resources_list(tmp_path):
    s = _make_server(SAMPLE, tmp_path)
    resp = _send(s, {"id": 1, "method": "resources/list"})
    resources = resp.get("result", [])
    assert len(resources) > 0
    assert any(r["uri"].startswith("okf://") for r in resources)
