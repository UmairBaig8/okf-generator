"""
okf/enrich/_lsp_map.py

Static registry mapping source file extensions to the LSP server command
needed to analyze them, plus a lightweight availability check.

Deliberately just a dict + two functions. No config parsing, no plugin
system here — that complexity belongs in okf/config.py if/when users need
to override commands (e.g. custom pyright path).
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass


@dataclass(frozen=True)
class LspServer:
    lang: str
    command: tuple[str, ...]
    check_cmd: str  # binary name to check with shutil.which()


LSP_MAP: dict[str, LspServer] = {
    ".py": LspServer(
        lang="python",
        command=("pyright-langserver", "--stdio"),
        check_cmd="pyright-langserver",
    ),
    ".go": LspServer(
        lang="go",
        command=("gopls",),
        check_cmd="gopls",
    ),
    ".rs": LspServer(
        lang="rust",
        command=("rust-analyzer",),
        check_cmd="rust-analyzer",
    ),
    ".ts": LspServer(
        lang="typescript",
        command=("typescript-language-server", "--stdio"),
        check_cmd="typescript-language-server",
    ),
    ".tsx": LspServer(
        lang="typescript",
        command=("typescript-language-server", "--stdio"),
        check_cmd="typescript-language-server",
    ),
}


def is_installed(server: LspServer) -> bool:
    """Check if the LSP binary for this server is on $PATH."""
    return shutil.which(server.check_cmd) is not None


def detect(extensions: set[str]) -> dict[str, LspServer]:
    """
    Given a set of file extensions found in the bundle (e.g. {'.py', '.go'}),
    return the subset of LSP_MAP entries that are both relevant and
    installed on this machine.

    Extensions with no known server, or a known-but-uninstalled server,
    are silently omitted — the caller is responsible for logging what
    was skipped and why (see LspEnricher.start()).
    """
    found = {}
    for ext in extensions:
        server = LSP_MAP.get(ext)
        if server and is_installed(server):
            found[ext] = server
    return found


def status_table() -> list[tuple[str, str, bool, str]]:
    """
    Returns (ext, lang, installed, check_cmd) rows for ``okf lsp status``.
    Dedupes by lang since .ts/.tsx share a server.
    """
    seen_langs = set()
    rows = []
    for ext, server in LSP_MAP.items():
        if server.lang in seen_langs:
            continue
        seen_langs.add(server.lang)
        rows.append((ext, server.lang, is_installed(server), server.check_cmd))
    return rows
