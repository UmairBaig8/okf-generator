"""
okf/enrich/lsp.py

Minimal hand-rolled LSP client over stdio. No pygls — this needs exactly
two request types (textDocument/definition, textDocument/references),
so a ~150-line client is less risk than pulling in a library built
primarily for writing servers, not clients.

v1 scope, deliberately narrow:
  - one LSP process per language, spawned once, reused for the whole pass
  - textDocument/definition + textDocument/references only
  - 3s startup timeout -> skip that language, keep going
  - partial results are written; a crashed/timed-out server never loses
    the tree-sitter data already in the bundle
  - subprocess is always cleaned up, even on Ctrl+C
"""

from __future__ import annotations

import atexit
import json
import logging
import subprocess
import threading
from pathlib import Path
from queue import Empty, Queue

from ..parsers.base import Concept
from ..generator import _concept_output_path, render_concept
from .base import EnrichResult, Enricher
from ._lsp_map import LSP_MAP, LspServer, detect

log = logging.getLogger("okf_gen")

# Extension → language ID for textDocument/didOpen notifications.
# Must match what the LSP server expects for its language.
# Per-language initialization options for LSP servers that need
# explicit include/exclude paths to begin indexing.
_LANGS_INIT_OPTIONS: dict[str, dict] = {
    "python": {"include": ["."], "exclude": ["**/__pycache__", "**/.git", "**/node_modules", "**/.venv"]},
    "typescript": {},
}

_EXT_TO_LANG_ID: dict[str, str] = {
    ".py": "python",
    ".go": "go",
    ".rs": "rust",
    ".ts": "typescript",
    ".tsx": "typescriptreact",
    ".js": "javascript",
    ".jsx": "javascriptreact",
}


class LspTimeoutError(Exception):
    pass


class _JsonRpcClient:
    """One JSON-RPC-over-stdio connection to a single LSP server process."""

    def __init__(self, command: tuple[str, ...], cwd: Path):
        self._proc = subprocess.Popen(
            command,
            cwd=str(cwd),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        self._next_id = 0
        self._lock = threading.Lock()
        self._pending: dict[int, Queue] = {}
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()
        self._closed = False
        atexit.register(self.close)

    # -- wire protocol -------------------------------------------

    def _read_loop(self) -> None:
        stdout = self._proc.stdout
        while True:
            try:
                headers = {}
                while True:
                    line = stdout.readline()
                    if not line or line in (b"\r\n", b"\n"):
                        break
                    key, _, value = line.decode("ascii").partition(":")
                    headers[key.strip().lower()] = value.strip()
                length = int(headers.get("content-length", 0))
                if length == 0:
                    if not line:
                        return
                    continue
                body = stdout.read(length)
                msg = json.loads(body)
            except (ValueError, OSError):
                return

            msg_id = msg.get("id")
            if msg_id is not None and msg_id in self._pending:
                self._pending[msg_id].put(msg)

    def _write(self, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
        try:
            self._proc.stdin.write(header + body)
            self._proc.stdin.flush()
        except BrokenPipeError:
            raise RuntimeError("LSP process closed stdin")

    def request(self, method: str, params: dict, timeout: float) -> dict:
        with self._lock:
            self._next_id += 1
            msg_id = self._next_id
            q: Queue = Queue(maxsize=1)
            self._pending[msg_id] = q
        self._write({"jsonrpc": "2.0", "id": msg_id, "method": method, "params": params})
        try:
            response = q.get(timeout=timeout)
        except Empty:
            raise LspTimeoutError(f"{method} timed out after {timeout}s") from None
        finally:
            self._pending.pop(msg_id, None)
        if "error" in response:
            raise RuntimeError(f"{method} -> LSP error: {response['error']}")
        return response.get("result", {})

    def notify(self, method: str, params: dict) -> None:
        self._write({"jsonrpc": "2.0", "method": method, "params": params})

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._proc.poll() is not None:
            return
        try:
            self.request("shutdown", {}, timeout=1.0)
            self.notify("exit", {})
        except Exception:
            pass
        finally:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=2.0)
            except Exception:
                try:
                    self._proc.kill()
                    self._proc.wait(timeout=1.0)
                except Exception:
                    pass


def _to_uri(path: Path) -> str:
    return path.resolve().as_uri()


def _from_uri(uri: str) -> str:
    if uri.startswith("file://"):
        return uri[len("file://"):]
    return uri


class LspEnricher(Enricher):
    """
    Resolves callers/callees for ambiguous concepts using the LSP servers
    available for the languages present in the bundle.

    Only queries nodes tree-sitter flagged as ambiguous (dynamic dispatch,
    interface calls) — same-file, already-resolved calls are left alone
    to keep query volume low.

    **No SIGINT handler registered here.** Cleanup is driven by
    try/finally in the caller (okf/enrich/__init__.py).
    """

    STARTUP_TIMEOUT = 3.0
    QUERY_TIMEOUT = 5.0

    # Language-specific initialization options that some LSP servers
    # require to know which files to index.
    _configs_created: dict[str, Path] = {}

    def _get_source_include(self) -> str:
        """Return the relative path from workspace_root to source_dir for LSP include."""
        try:
            return str(self.source_dir.relative_to(self._workspace_root))
        except ValueError:
            return "."

    def _ensure_pyright_config(self) -> Path | None:
        candidates = [self._workspace_root / "pyrightconfig.json", self._workspace_root / "pyproject.toml"]
        if any(p.exists() for p in candidates):
            return None
        include = self._get_source_include()
        cfg = self._workspace_root / "pyrightconfig.json"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text(json.dumps({"include": [include], "exclude": ["**/__pycache__", "**/.git", "**/node_modules", "**/.venv"]}, indent=2))
        self._configs_created["pyright"] = cfg
        return cfg

    def _ensure_configs(self) -> dict[str, Path]:
        result = {}
        if LSP_MAP.get(".py") and ".py" in detect({".py"}):
            cfg = self._ensure_pyright_config()
            if cfg:
                result["pyright"] = cfg
        return result

    def _cleanup_configs(self) -> None:
        for lang, path in self._configs_created.items():
            try:
                path.unlink()
            except Exception:
                pass
        self._configs_created.clear()

    def __init__(self, source_dir: Path):
        self.source_dir = source_dir
        # LSP workspace root must be the project root, not a subdirectory,
        # so imports like "from ..parsers.base import Concept" resolve.
        self._workspace_root = self._detect_project_root(source_dir)
        self._clients: dict[str, _JsonRpcClient] = {}
        self._opened_files: set[str] = set()
        self._skipped_languages: list[str] = []
        self._ext_to_lang: dict[str, str] = {}

    @staticmethod
    def _detect_project_root(start: Path) -> Path:
        """Walk up from start to find the project root (has .git or pyproject.toml)."""
        for parent in [start] + list(start.parents):
            if (parent / ".git").is_dir() or (parent / "pyproject.toml").is_file():
                return parent
        return start

    # -- Enricher contract ---------------------------------------

    def start(self, bundle_dir: Path, concepts: list[Concept]) -> bool:
        extensions = {Path(c.resource).suffix for c in concepts if c.resource} - {""}
        servers = detect(extensions)
        if not servers:
            self._skipped_languages = sorted({Path(c.resource).suffix.lstrip(".") for c in concepts if c.resource})
            return False

        started_any = False
        seen_langs: dict[str, LspServer] = {}
        self._ensure_configs()

        for ext, server in servers.items():
            if server.lang in seen_langs:
                continue
            seen_langs[server.lang] = server
            try:
                init_opts = _LANGS_INIT_OPTIONS.get(server.lang, {})
                client = _JsonRpcClient(server.command, cwd=self._workspace_root)
                client.request(
                    "initialize",
                    {
                        "processId": None,
                        "rootUri": _to_uri(self._workspace_root),
                        "capabilities": {},
                        "initializationOptions": init_opts,
                    },
                    timeout=self.STARTUP_TIMEOUT,
                )
                client.notify("initialized", {})
                self._clients[server.lang] = client
                started_any = True
            except (LspTimeoutError, OSError, RuntimeError) as e:
                self._skipped_languages.append(f"{server.lang} ({e})")
                continue

        # Cache ext → lang mapping after detection
        self._ext_to_lang = {ext: s.lang for ext, s in servers.items() if s.lang in seen_langs}

        return started_any

    def run(self, bundle_dir: Path, concepts: list[Concept]) -> EnrichResult:
        enriched = 0
        skipped = 0
        warnings: list[str] = list(f"[!] LSP unavailable for: {lang}" for lang in self._skipped_languages)

        line_index = self._build_line_index(concepts)

        for concept in concepts:
            if concept.type not in {"Function", "Class", "Method"}:
                skipped += 1
                continue

            if not concept.source_lines or concept.source_lines[0] < 1:
                skipped += 1
                continue

            lang = self._lang_for(concept)
            client = self._clients.get(lang)
            if client is None:
                skipped += 1
                continue

            try:
                self._ensure_open(client, concept)
                references = self._resolve_references(client, concept)

                caller_ids = []
                for ref in references:
                    cid = self._resolve_to_concept(ref, line_index)
                    if cid and cid != concept.concept_id:
                        caller_ids.append(cid)

                if caller_ids or references:
                    self._write_back(bundle_dir, concept, caller_ids, concepts)

                enriched += 1
            except (LspTimeoutError, RuntimeError, OSError) as e:
                skipped += 1
                warnings.append(f"[!] {concept.concept_id}: {e}")
                continue

        return EnrichResult(enriched_count=enriched, skipped_count=skipped, total_count=len(concepts), warnings=warnings)

    def stop(self) -> None:
        for client in self._clients.values():
            client.close()
        self._clients.clear()
        self._opened_files.clear()
        self._cleanup_configs()

    # -- helpers -------------------------------------------------

    def _build_line_index(self, concepts: list[Concept]) -> list[tuple[str, int, int, str]]:
        """Return [(abs_path, start_line, end_line, concept_id)] for range matching."""
        idx = []
        for c in concepts:
            if not c.resource or not c.source_lines or c.source_lines[0] < 1:
                continue
            abs_path = str((self.source_dir / c.resource).resolve())
            start, end = c.source_lines
            if end < start:
                end = start + 1
            idx.append((abs_path, start, end, c.concept_id))
        return idx

    def _lang_for(self, concept: Concept) -> str | None:
        ext = Path(concept.resource).suffix if concept.resource else ""
        return self._ext_to_lang.get(ext)

    def _ensure_open(self, client: _JsonRpcClient, concept: Concept) -> None:
        path = str((self.source_dir / concept.resource).resolve())
        if path in self._opened_files:
            return
        ext = Path(path).suffix
        lang_id = _EXT_TO_LANG_ID.get(ext, "plaintext")
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        client.notify(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": _to_uri(Path(path)),
                    "languageId": lang_id,
                    "version": 1,
                    "text": text,
                }
            },
        )
        self._opened_files.add(path)

    def _position_params(self, concept: Concept) -> dict:
        path = str((self.source_dir / concept.resource).resolve())
        line = concept.source_lines[0] - 1 if concept.source_lines else 0
        return {
            "textDocument": {"uri": _to_uri(Path(path))},
            "position": {"line": line, "character": 0},
        }

    def _resolve_definition(self, client: _JsonRpcClient, concept: Concept) -> dict | None:
        result = client.request(
            "textDocument/definition", self._position_params(concept), timeout=self.QUERY_TIMEOUT
        )
        if isinstance(result, list) and result:
            loc = result[0]
            return {"uri": _from_uri(loc["uri"]), "range": loc["range"]}
        if isinstance(result, dict) and "uri" in result:
            return {"uri": _from_uri(result["uri"]), "range": result.get("range", {})}
        return None

    def _resolve_references(self, client: _JsonRpcClient, concept: Concept) -> list[dict]:
        params = self._position_params(concept)
        params["context"] = {"includeDeclaration": False}
        result = client.request("textDocument/references", params, timeout=self.QUERY_TIMEOUT)
        return [{"uri": _from_uri(r["uri"]), "range": r["range"]} for r in (result or [])]

    def _resolve_to_concept(
        self,
        ref: dict,
        line_index: list[tuple[str, int, int, str]],
    ) -> str | None:
        ref_path = ref["uri"]
        ref_line = ref.get("range", {}).get("start", {}).get("line", 0) + 1  # back to 1-indexed

        # Find the concept whose source range contains the reference line (tightest match)
        best: tuple[str, int] | None = None
        best_span = 0
        for fp, start, end, cid in line_index:
            if fp != ref_path:
                continue
            if start <= ref_line <= end:
                span = end - start
                if best is None or span < best_span:
                    best = (cid, span)
                    best_span = span

        return best[0] if best else None

    def _write_back(
        self,
        bundle_dir: Path,
        concept: Concept,
        caller_ids: list[str],
        all_concepts: list[Concept],
    ) -> None:
        all_map = {c.concept_id: c for c in all_concepts}
        existing = set(concept.called_by)
        for cid in caller_ids:
            if cid and cid != concept.concept_id:
                existing.add(cid)
        concept.called_by = sorted(existing)
        concept.calls = concept.calls
        concept.body_extra["lsp_enriched"] = True
        md = render_concept(concept, all_map, source_dir=self.source_dir)
        out_path = _concept_output_path(concept, bundle_dir)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
