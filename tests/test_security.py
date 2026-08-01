"""Security regression tests for the hardening work:
- okf serve: loopback-only binding, token auth, https-only git URLs
- okf dashboard: non-loopback requires token
- okf agent: session id path-traversal validation
- generator/update: concept_id path traversal guards
- mcp_server: git reference option injection guard
"""

from pathlib import Path

import pytest

# ── okf serve ────────────────────────────────────────────────────────────────

def test_serve_rejects_non_loopback_without_allow_remote():
    from okf.serve import _is_loopback
    assert _is_loopback("127.0.0.1")
    assert _is_loopback("localhost")
    assert _is_loopback("::1")
    assert _is_loopback("127.0.0.2")
    assert not _is_loopback("0.0.0.0")
    assert not _is_loopback("192.168.1.5")


def test_serve_https_only_git_urls():
    from okf.serve import _parse_git_url
    url, ref = _parse_git_url("https://github.com/user/repo.git@main")
    assert url.startswith("https://")
    assert ref == "main"

    # ssh/scp-style URLs must be rejected outright
    for bad in ("git@github.com:user/repo.git", "ssh://git@github.com/user/repo.git"):
        with pytest.raises(ValueError):
            _parse_git_url(bad)


def test_serve_handler_requires_token(tmp_path):
    import socketserver
    import threading
    import urllib.error
    import urllib.request

    from okf.serve import VizzHandler

    class _Server(socketserver.TCPServer):
        auth_token = "sekret"

    bundle = tmp_path / "okf_bundle"
    bundle.mkdir()
    (bundle / "index.md").write_text("# test")
    (bundle / "viz.html").write_text("<html>ok</html>")

    server = _Server(("127.0.0.1", 0), VizzHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def _get(url):
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                return r.status
        except urllib.error.HTTPError as e:
            return e.code

    try:
        assert _get(f"http://127.0.0.1:{port}/") == 401
        assert _get(f"http://127.0.0.1:{port}/?token=wrong") == 401
        assert _get(f"http://127.0.0.1:{port}/?token=sekret") == 200  # serves viz.html
        req = urllib.request.Request(f"http://127.0.0.1:{port}/", headers={"Authorization": "Bearer sekret"})
        with urllib.request.urlopen(req, timeout=5) as r:
            assert r.status == 200
    finally:
        server.shutdown()
        server.server_close()


# ── okf dashboard ────────────────────────────────────────────────────────────

def test_dashboard_build_app_rejects_cross_origin(tmp_path):
    """The FastAPI app must refuse cross-origin API reads (no CORS allowance).

    Skipped when fastapi isn't installed (it's a `[dashboard]` extra, not `[dev]`).
    """
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from okf.dashboard import build_app

    bundle = tmp_path / "okf_bundle"
    bundle.mkdir()
    (bundle / "index.md").write_text("---\ntype: Index\ntitle: root\n---\n")
    (bundle / "SUMMARY.md").write_text("# Summary")

    app = build_app(bundle)
    client = TestClient(app)
    resp = client.get("/api/info", headers={"Origin": "https://evil.example"})
    # Same-origin GET with a foreign Origin: the response must not expose
    # Access-Control-Allow-Origin (browser blocks the read).
    assert "access-control-allow-origin" not in {k.lower() for k in resp.headers}


# ── okf agent session ids ────────────────────────────────────────────────────

def test_agent_session_path_rejects_traversal():
    from okf.agent import _session_path

    for bad in ("../../etc/passwd", "a/b", "..", "a b", "a\\b"):
        with pytest.raises(ValueError):
            _session_path(bad)

    for good in ("ses_abc123", "my-session_1", "ABC"):
        p = _session_path(good)
        assert p.name == f"{good}.json"


# ── concept_id path traversal guards ─────────────────────────────────────────

def test_concept_output_path_rejects_traversal():
    from okf.generator import _concept_output_path
    from okf.parsers.base import Concept

    c = Concept(type="Function", title="f", concept_id="../../evil")
    with pytest.raises(ValueError):
        _concept_output_path(c, Path("/tmp/bundle"))


def test_update_concept_output_path_rejects_traversal():
    from okf.update import _concept_output_path

    with pytest.raises(ValueError):
        _concept_output_path("../../evil", Path("/tmp/bundle"))


# ── mcp_server reference guard ───────────────────────────────────────────────

def test_mcp_git_reference_rejects_option_injection():
    """detect_changes with kind=git must reject references starting with '-'."""
    # The guard lives in the dispatch path; verify the check rejects option-like refs.
    from okf.mcp_server import BundleMCPServer

    server = BundleMCPServer.__new__(BundleMCPServer)  # avoid __init__
    server.bundle_dir = Path("/tmp/nonexistent")
    args = {"kind": "git", "reference": "--upload-pack=evil"}
    with pytest.raises(ValueError):
        server._dispatch("detect_changes", args)
