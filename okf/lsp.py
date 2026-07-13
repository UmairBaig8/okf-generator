"""
okf/lsp.py — ``okf lsp`` CLI subcommand.

Usage:
  okf lsp status        Table of detected LSPs
  okf lsp resolve FILE:LINE:COL  Test one definition lookup
  okf lsp map           Show full LSP_MAP
"""

from __future__ import annotations

import sys
from pathlib import Path

from .enrich._lsp_map import LSP_MAP, status_table


def main():
    args = sys.argv[1:]  # "okf lsp <subcommand> ..."

    if not args or args[0] in ("-h", "--help", "help"):
        print(__doc__)
        return

    cmd = args[0]

    if cmd == "status":
        _cmd_status()
    elif cmd == "resolve":
        _cmd_resolve(args[1:])
    elif cmd == "map":
        _cmd_map()
    else:
        print(f"Unknown subcommand: {cmd!r}")
        print(__doc__)
        sys.exit(1)


def _cmd_status():
    rows = status_table()
    if not rows:
        print("No LSP servers configured.\n")
        return

    print(f"\n  {'Lang':14s} {'Ext':6s} {'Status':10s} {'Binary'}")
    print(f"  {'----':14s} {'---':6s} {'------':10s} {'------'}")
    for ext, lang, installed, check_cmd in rows:
        status = "✓ installed" if installed else "✗ missing"
        print(f"  {lang:14s} {ext:6s} {status:10s} {check_cmd}")
    print()


def _cmd_resolve(args: list[str]):
    if not args:
        print("Usage: okf lsp resolve <file:line:col>")
        sys.exit(1)

    spec = args[0]
    parts = spec.rsplit(":", 2)
    if len(parts) != 3:
        print(f"Expected format file:line:col, got {spec!r}")
        sys.exit(1)

    file_path, line_str, col_str = parts
    try:
        line = int(line_str) - 1
        col = int(col_str)
    except ValueError:
        print(f"line and col must be integers: {spec!r}")
        sys.exit(1)

    path = Path(file_path).resolve()
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    ext = path.suffix
    server = LSP_MAP.get(ext)
    if server is None:
        print(f"No LSP server configured for extension {ext!r}")
        sys.exit(1)

    from .enrich.lsp import _EXT_TO_LANG_ID, _JsonRpcClient, _to_uri, LspEnricher

    lang_id = _EXT_TO_LANG_ID.get(ext, "plaintext")

    # Detect workspace root (project root with .git, Cargo.toml, etc.)
    workspace_root = LspEnricher._detect_project_root(path.parent)

    client = _JsonRpcClient(server.command, cwd=workspace_root)
    try:
        client.request(
            "initialize",
            {
                "processId": None,
                "rootUri": _to_uri(workspace_root),
                "capabilities": {},
            },
            timeout=10.0,
        )
        client.notify("initialized", {})

        text = path.read_text(encoding="utf-8", errors="replace")
        client.notify(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": _to_uri(path),
                    "languageId": lang_id,
                    "version": 1,
                    "text": text,
                }
            },
        )

        params = {
            "textDocument": {"uri": _to_uri(path)},
            "position": {"line": line, "character": col},
        }

        result = client.request("textDocument/definition", params, timeout=5.0)
        if isinstance(result, list) and result:
            loc = result[0]
            print(f"\n  Definition: {loc.get('uri', '?')}:{loc.get('range', {}).get('start', {}).get('line', '?')}\n")
        elif isinstance(result, dict):
            print(f"\n  Definition: {result.get('uri', '?')}\n")
        else:
            print("  No definition found.\n")

        refs = client.request(
            "textDocument/references",
            {**params, "context": {"includeDeclaration": False}},
            timeout=5.0,
        )
        if refs:
            print(f"  References ({len(refs)}):")
            for r in refs:
                uri = r.get("uri", "?")
                rng = r.get("range", {})
                start = rng.get("start", {})
                print(f"    {uri}:{start.get('line', '?')}:{start.get('character', '?')}")
        else:
            print("  No references found.")
        print()

    finally:
        client.close()


def _cmd_map():
    print(f"\n  {'Ext':6s} {'Language':14s} {'Command'}")
    print(f"  {'---':6s} {'--------':14s} {'-------'}")
    for ext, server in sorted(LSP_MAP.items(), key=lambda x: x[1].lang):
        cmd = " ".join(server.command)
        print(f"  {ext:6s} {server.lang:14s} {cmd}")
    print()
