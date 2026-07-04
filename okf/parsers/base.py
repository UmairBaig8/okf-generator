"""Shared parser infrastructure: Concept dataclass, TreeSitterParser base, utility functions (_ts, _prev_comment, _find_all, _node_text, _parse_doc_tags, _safe_id, _first_line, SKIP_DIRS)."""

import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("okf_gen")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Concept:
    """One OKF concept (maps to one .md file)."""
    type: str                        # Module | Function | Class | Method | Dependency
    title: str
    description: str = ""
    resource: str = ""               # relative source path
    tags: list[str] = field(default_factory=list)
    timestamp: str = ""
    signature: str = ""
    docstring: str = ""
    methods: list[str] = field(default_factory=list)
    params: list[dict] = field(default_factory=list)
    returns: str = ""
    source_lines: tuple = ()
    type_params: list[str] = field(default_factory=list)
    inheritance: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    visibility: list[str] = field(default_factory=list)
    fields: list[dict] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    body_extra: dict = field(default_factory=dict)
    usage_example: str = ""
    side_effects: str = ""
    design_pattern: str = ""
    deprecation_notes: str = ""
    security: str = ""
    complexity: str = ""
    related_semantic: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    calls_raw: list[str] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)
    called_by: list[str] = field(default_factory=list)
    concept_id: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SKIP_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", ".mypy_cache", ".pytest_cache",
    "node_modules", ".venv", "venv", "env", ".env", "dist", "build",
    ".tox", "htmlcov", ".eggs", "vendor", "target", "coverage",
    ".next", ".nuxt", "__snapshots__", ".cache", "tmp", "temp", "logs",
    "static", "media", "assets",
}

SKIP_DIR_SUFFIXES = (".egg-info", ".dist-info")


def _safe_id(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", name).strip("_") or "unknown"


def _first_line(text: str) -> str:
    if not text:
        return ""
    return text.strip().splitlines()[0].strip()


def _ts(path: Path) -> str:
    try:
        mtime = path.stat().st_mtime
        return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _prev_comment(node, src_bytes: bytes) -> str:
    chunk = src_bytes[:node.start_byte].rstrip()
    if chunk.endswith(b"*/"):
        begin = chunk.rfind(b"/*")
        if begin >= 0:
            raw = chunk[begin:].decode(errors="replace").strip()
            lines = raw.lstrip("/").lstrip("*").rstrip("*/").strip().splitlines()
            cleaned = [x.strip().lstrip("*").strip() for x in lines]
            return "\n".join(x for x in cleaned if x)
    lines = chunk.splitlines()
    comment_lines = []
    for line in reversed(lines):
        s = line.strip()
        if s.startswith(b"///") or s.startswith(b"//"):
            comment_lines.insert(0, s.lstrip(b"/").strip().decode(errors="replace"))
        elif s.startswith(b"#"):
            comment_lines.insert(0, s.lstrip(b"#").strip().decode(errors="replace"))
        elif s.startswith(b"--"):
            comment_lines.insert(0, s.lstrip(b"-").strip().decode(errors="replace"))
        else:
            break
    return "\n".join(comment_lines)


def _find_all(node, *kinds):
    if node.type in kinds:
        yield node
    for child in node.children:
        yield from _find_all(child, *kinds)


def _node_text(node) -> str:
    if node is None:
        return ""
    return node.text.decode(errors="replace").strip()


def _parse_doc_tags(docstring: str, lang: str) -> tuple[list[dict], str]:
    if not docstring:
        return [], ""
    params = []
    returns = ""
    for line in docstring.splitlines():
        s = line.strip()
        if not s:
            continue
        if lang in ("java",):
            m = re.match(r'@param\s+(\S+)(?:\s+(.*))?', s)
            if m:
                params.append({"name": m.group(1), "annotation": "", "default": ""})
                continue
            m = re.match(r'@return\s+(.*)', s)
            if m:
                returns = m.group(1)
                continue
        elif lang in ("javascript", "typescript"):
            m = re.match(r'@param\s+\{([^}]*)\}\s+(\S+)', s)
            if m:
                params.append({"name": m.group(2), "annotation": m.group(1), "default": ""})
                continue
            m = re.match(r'@param\s+(\S+)', s)
            if m:
                params.append({"name": m.group(1), "annotation": "", "default": ""})
                continue
            m = re.match(r'@returns?\s+\{([^}]*)\}', s)
            if m:
                returns = m.group(1)
                continue
        elif lang == "ruby":
            m = re.match(r'@param\s+\[([^\]]*)\]\s+(\S+)', s)
            if m:
                params.append({"name": m.group(2), "annotation": m.group(1), "default": ""})
                continue
            m = re.match(r'@return\s+\[([^\]]*)\]', s)
            if m:
                returns = m.group(1)
                continue
    return params, returns


# ---------------------------------------------------------------------------
# Tree-sitter base parser
# ---------------------------------------------------------------------------

class TreeSitterParser:
    LANGUAGE     = "unknown"
    EXTENSIONS: set[str] = set()
    _TS_MODULE   = ""
    _lang_obj    = None

    def _lang(self):
        if self.__class__._lang_obj is None:
            import importlib
            mod = importlib.import_module(self._TS_MODULE)
            from tree_sitter import Language
            self.__class__._lang_obj = Language(mod.language())
        return self.__class__._lang_obj

    def _parser(self):
        from tree_sitter import Parser
        p = Parser(self._lang())
        return p

    def parse_file(self, path: Path, repo_root: Path) -> list[Concept]:
        rel    = str(path.relative_to(repo_root))
        ts     = _ts(path)
        res_id = str(path.relative_to(repo_root).with_suffix("")).replace(os.sep, "/")
        try:
            src_bytes = path.read_bytes()
        except Exception:
            return []
        try:
            tree = self._parser().parse(src_bytes)
        except Exception as e:
            log.debug(f"tree-sitter parse error in {path}: {e}")
            return [Concept(
                type="Module", title=path.stem, resource=rel,
                description=f"{self.LANGUAGE} file: {path.name}",
                tags=[self.LANGUAGE], timestamp=ts,
                concept_id=res_id,
            )]
        root = tree.root_node
        module_doc   = self._module_doc(root, src_bytes)
        module_title = path.parent.name if path.stem in {"index", "__init__", "mod", "main"} else path.stem
        module = Concept(
            type="Module",
            title=module_title,
            description=_first_line(module_doc),
            docstring=module_doc,
            resource=rel,
            tags=[self.LANGUAGE, module_title],
            timestamp=ts,
            concept_id=res_id,
            imports=self._collect_imports(root, src_bytes),
        )
        symbols = self._parse_symbols(root, src_bytes, rel, ts, res_id)
        for s in symbols:
            module.related.append(s.concept_id)
        return [module] + symbols

    def _module_doc(self, root, src_bytes: bytes) -> str:
        return ""

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        return []

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        return []

    def _parse_symbols(self, root, src_bytes: bytes, resource: str, ts: str, parent_id: str) -> list[Concept]:
        return []

    def _make_concept(self, ctype: str, name: str, doc: str, sig: str,
                      resource: str, ts: str, parent_id: str,
                      lineno: int = 0, methods: list[str] | None = None,
                      node=None, src_bytes: bytes = b"",
                      type_params: list[str] | None = None) -> Concept:
        res_id = re.sub(r"\.[^/]+$", "", resource).replace(os.sep, "/")
        cid    = f"{res_id}/{_safe_id(name)}"
        calls_raw = self._collect_calls(node, src_bytes) if node is not None else []
        end_lineno = (node.end_point[0] + 1) if node is not None else 0
        return Concept(
            type=ctype,
            title=name,
            description=_first_line(doc),
            docstring=doc,
            signature=sig,
            resource=resource,
            tags=[self.LANGUAGE, ctype.lower()],
            timestamp=ts,
            source_lines=(lineno, end_lineno),
            concept_id=cid,
            related=[parent_id],
            methods=methods or [],
            calls_raw=calls_raw,
            type_params=type_params or [],
        )
