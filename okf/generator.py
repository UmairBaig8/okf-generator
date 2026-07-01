"""Generate an OKF (Open Knowledge Format) bundle from a codebase.

Walks a source directory and produces a conformant OKF v0.1 bundle whose
layout mirrors the source tree exactly (domain/resource-based), e.g.:

  <output>/
  ├── index.md                          # bundle root — lists top-level dirs
  ├── log.md                            # generation history
  │
  ├── StockAI/
  │   ├── index.md                      # lists subdirs + concepts
  │   └── RnD/
  │       └── python/
  │           └── connectors/
  │               ├── index.md          # lists all concepts in this folder
  │               ├── economic_data.md  # Module concept (one per source file)
  │               └── economic_data/
  │                   ├── WorldBankConnector.md  # Class concept
  │                   ├── get_indicator.md       # Function concept
  │                   └── search.md              # Function concept
  └── ...

Every directory gets an index.md listing its subdirectories and concepts
grouped by type (Module / Class / Function). This makes the bundle
navigable by domain, just like the original codebase.

Concept frontmatter (OKF v0.1 conformant):
  type         REQUIRED — Module | Function | Class | Method
  title        display name
  description  one-line summary (from docstring or LLM enrichment)
  resource     relative source file path
  tags         language, module name, etc.
  timestamp    ISO-8601 last-modified time of the source file

Supported languages:
  Python       full AST — functions, classes, params, return types, docstrings
  JS/TS/Go/Java/Rust/Ruby  tree-sitter — functions, classes, methods, doc comments
  SQL          dialect-tolerant regex — tables, views, functions/procedures, indexes

Config via env vars:
  OKF_API_KEY      API key for LLM enrichment
  OKF_BASE_URL     API base URL (default: http://localhost:8080/v1)
  OKF_MODEL        model name (default: claude-sonnet-4-6)
  OKF_ENRICH=1     enable LLM enrichment of descriptions + docstrings
  OKF_MAX_WORKERS  parallel enrichment workers (default: 2)
  LOG_LEVEL        default: INFO

Usage:
  python okf_generator.py <source_dir> [output_dir]

  source_dir   root of the codebase to scan
  output_dir   where to write the OKF bundle (default: ./okf_bundle)
"""

import ast
import subprocess
import json
import logging
import os
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml  # PyYAML
from tqdm import tqdm

from okf import manifest_scanner

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
    # extra body sections
    signature: str = ""
    docstring: str = ""
    methods: list[str] = field(default_factory=list)   # for classes
    params: list[dict] = field(default_factory=list)   # {name, annotation, default}
    returns: str = ""
    source_lines: tuple = ()         # (start, end)
    related: list[str] = field(default_factory=list)   # concept IDs to cross-link
    body_extra: dict = field(default_factory=dict)     # type-specific fields (e.g. Dependency)

    # cross-reference edges (populated by parsers + okf.linker)
    imports: list[str] = field(default_factory=list)    # Module only — raw import names
    calls_raw: list[str] = field(default_factory=list)  # Function/Class/Method — raw callee names
    calls: list[str] = field(default_factory=list)       # resolved concept_ids (linker output)
    called_by: list[str] = field(default_factory=list)   # resolved concept_ids (linker output)
    # internal
    concept_id: str = ""             # e.g. "functions/my_func"


# ---------------------------------------------------------------------------
# Language parsers
# ---------------------------------------------------------------------------

def _ts(path: Path) -> str:
    try:
        mtime = path.stat().st_mtime
        return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Tree-sitter base parser
# ---------------------------------------------------------------------------

def _prev_comment(node, src_bytes: bytes) -> str:
    """Extract the comment block immediately preceding a node (JSDoc, ///, #, --)."""
    chunk = src_bytes[:node.start_byte].rstrip()

    # Block comment: /** ... */ or /* ... */
    if chunk.endswith(b"*/"):
        begin = chunk.rfind(b"/*")
        if begin >= 0:
            raw = chunk[begin:].decode(errors="replace").strip()
            # strip /* */ and leading * from each line
            lines = raw.lstrip("/").lstrip("*").rstrip("*/").strip().splitlines()
            cleaned = [x.strip().lstrip("*").strip() for x in lines]
            return "\n".join(x for x in cleaned if x)

    # Line comments: // /// # --
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
    """Yield all descendant nodes matching any of the given type names."""
    if node.type in kinds:
        yield node
    for child in node.children:
        yield from _find_all(child, *kinds)


def _node_text(node) -> str:
    if node is None:
        return ""
    return node.text.decode(errors="replace").strip()


class TreeSitterParser:
    """Base class for all tree-sitter language parsers."""
    LANGUAGE     = "unknown"
    EXTENSIONS: set[str] = set()

    # Subclasses set these
    _TS_MODULE   = ""          # importlib module name e.g. "tree_sitter_python"
    _lang_obj    = None        # cached Language instance

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

        # Module-level doc
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
        """Override per language to extract file-level doc comment."""
        return ""

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        """Override per language to collect raw import/require names.
        Default returns empty — languages without an override produce no
        import edges (silently correct, not an error)."""
        return []

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        """Override per language to collect raw callee names inside a
        function/method/class body.  Default returns empty."""
        return []

    def _parse_symbols(self, root, src_bytes: bytes, resource: str, ts: str, parent_id: str) -> list[Concept]:
        """Override per language to extract functions, classes, etc."""
        return []

    def _make_concept(self, ctype: str, name: str, doc: str, sig: str,
                      resource: str, ts: str, parent_id: str,
                      lineno: int = 0, methods: list[str] | None = None,
                      node=None, src_bytes: bytes = b"") -> Concept:
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
        )


# ---------------------------------------------------------------------------
# Python parser (AST — unchanged, best quality)
# ---------------------------------------------------------------------------

class PythonParser:
    LANGUAGE   = "python"
    EXTENSIONS = {".py"}

    def parse_file(self, path: Path, repo_root: Path) -> list[Concept]:
        rel = str(path.relative_to(repo_root))
        ts  = _ts(path)

        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            tree   = ast.parse(source, filename=str(path))
        except SyntaxError as e:
            log.debug(f"Syntax error in {path}: {e}")
            err_title    = path.parent.name if path.name == "__init__.py" else path.stem
            resource_id_err = re.sub(r"\.py$", "", rel).replace(os.sep, "/")
            return [Concept(
                type="Module", title=err_title,
                description=f"Python module (parse error: {e})",
                resource=rel,
                tags=[self.LANGUAGE, err_title],
                timestamp=ts,
                concept_id=resource_id_err,
            )]

        module_doc = ast.get_docstring(tree) or ""
        resource_id = re.sub(r"\.py$", "", rel).replace(os.sep, "/")
        # __init__.py represents the package — use parent dir name as title
        if path.name == "__init__.py":
            module_title = path.parent.name
            module_tag   = path.parent.name
        else:
            module_title = path.stem
            module_tag   = path.stem

        module_concept = Concept(
            type="Module",
            title=module_title,
            description=_first_line(module_doc),
            docstring=module_doc,
            resource=rel,
            tags=[self.LANGUAGE, module_tag],
            timestamp=ts,
            concept_id=resource_id,
            imports=self._collect_imports(tree),
        )

        funcs   = []
        classes = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                c = self._parse_function(node, rel, ts, module_concept.concept_id)
                funcs.append(c)
                module_concept.related.append(c.concept_id)
            elif isinstance(node, ast.ClassDef):
                c = self._parse_class(node, rel, ts, module_concept.concept_id)
                classes.append(c)
                module_concept.related.append(c.concept_id)

        return [module_concept] + funcs + classes

    def _collect_imports(self, tree) -> list[str]:
        """Top-level import names for a module, used by okf.linker to
        cross-reference against manifest-derived Dependency concepts."""
        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
        return names

    def _collect_calls(self, node) -> list[str]:
        """Raw callee names referenced inside a function/method body, used
        by okf.linker to resolve call-graph edges between concepts."""
        names = []
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Name):
                    names.append(n.func.id)
                elif isinstance(n.func, ast.Attribute):
                    names.append(n.func.attr)
        return names

    def _parse_function(self, node, resource, ts, parent_id) -> Concept:
        doc     = ast.get_docstring(node) or ""
        params  = self._params(node)
        ret     = self._returns(node)
        sig     = self._sig(node, params, ret)
        resource_id = re.sub(r"\.py$", "", resource).replace(os.sep, "/")
        cid     = f"{resource_id}/{_safe_id(node.name)}"
        return Concept(
            type="Function", title=node.name,
            description=_first_line(doc), docstring=doc,
            resource=resource,
            tags=["python", "function"],
            timestamp=ts, signature=sig, params=params, returns=ret,
            source_lines=(node.lineno, node.end_lineno),
            concept_id=cid, related=[parent_id],
            calls_raw=self._collect_calls(node),
        )

    def _parse_class(self, node, resource, ts, parent_id) -> Concept:
        doc     = ast.get_docstring(node) or ""
        methods = [
            child.name for child in ast.iter_child_nodes(node)
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef)
        ]
        resource_id = re.sub(r"\.py$", "", resource).replace(os.sep, "/")
        cid     = f"{resource_id}/{_safe_id(node.name)}"
        return Concept(
            type="Class", title=node.name,
            description=_first_line(doc), docstring=doc,
            resource=resource,
            tags=["python", "class"],
            timestamp=ts, methods=methods,
            source_lines=(node.lineno, node.end_lineno),
            concept_id=cid, related=[parent_id],
        )

    def _params(self, node) -> list[dict]:
        args    = node.args
        params  = []
        def_off = len(args.args) - len(args.defaults)
        for i, arg in enumerate(args.args):
            d_idx   = i - def_off
            default = ""
            if d_idx >= 0:
                try:
                    default = ast.unparse(args.defaults[d_idx])
                except Exception:
                    default = "..."
            annotation = ""
            if arg.annotation:
                try:
                    annotation = ast.unparse(arg.annotation)
                except Exception:
                    pass
            params.append({"name": arg.arg, "annotation": annotation, "default": default})
        return params

    def _returns(self, node) -> str:
        if node.returns:
            try:
                return ast.unparse(node.returns)
            except Exception:
                pass
        return ""

    def _sig(self, node, params, ret) -> str:
        parts  = []
        for p in params:
            s = p["name"]
            if p["annotation"]:
                s += f": {p['annotation']}"
            if p["default"]:
                s += f" = {p['default']}"
            parts.append(s)
        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        sig = f"{prefix} {node.name}({', '.join(parts)})"
        if ret:
            sig += f" -> {ret}"
        return sig


# ---------------------------------------------------------------------------
# JavaScript / TypeScript  (tree-sitter)
# ---------------------------------------------------------------------------

class JSTSParser(TreeSitterParser):
    LANGUAGE   = "javascript"
    EXTENSIONS = {".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs"}
    _TS_MODULE = "tree_sitter_javascript"
    _lang_obj  = None

    def _lang(self):
        if self.__class__._lang_obj is None:
            ext = getattr(self, "_path_ext", ".js")
            if ext in {".ts", ".tsx"}:
                try:
                    import tree_sitter_typescript as tsts
                    from tree_sitter import Language
                    # typescript grammar has .language_typescript() and .language_tsx()
                    if ext == ".tsx":
                        self.__class__._lang_obj = Language(tsts.language_tsx())
                    else:
                        self.__class__._lang_obj = Language(tsts.language_typescript())
                    return self.__class__._lang_obj
                except Exception:
                    pass
            import tree_sitter_javascript as tsjs
            from tree_sitter import Language
            self.__class__._lang_obj = Language(tsjs.language())
        return self.__class__._lang_obj

    def parse_file(self, path: Path, repo_root: Path) -> list[Concept]:
        self._path_ext = path.suffix.lower()
        self.__class__._lang_obj = None   # reset lang cache every parse to avoid TS→JS cross-contamination
        if self._path_ext in {".ts", ".tsx"}:
            self.LANGUAGE = "typescript"
        else:
            self.LANGUAGE = "javascript"
        return super().parse_file(path, repo_root)

    def _module_doc(self, root, src_bytes: bytes) -> str:
        # First block comment at top of file
        for child in root.children:
            if child.type == "comment":
                return _prev_comment(child.next_sibling or child, src_bytes) or \
                       _node_text(child).lstrip("/").lstrip("*").strip()
        return ""

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []

        for node in _find_all(root,
                               "function_declaration",
                               "class_declaration",
                               "method_definition",
                               "lexical_declaration",    # const foo = () => {}
                               "export_statement"):
            if node.type in {"function_declaration"}:
                name_node = node.child_by_field_name("name")
                if not name_node:
                    continue
                name   = _node_text(name_node)
                doc    = _prev_comment(node, src_bytes)
                params = self._js_params(node)
                ret    = self._js_return_type(node)
                sig    = f"function {name}({params})" + (f": {ret}" if ret else "")
                concepts.append(self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes))

            elif node.type == "class_declaration":
                name_node = node.child_by_field_name("name")
                if not name_node:
                    continue
                name    = _node_text(name_node)
                doc     = _prev_comment(node, src_bytes)
                methods = [
                    _node_text(m.child_by_field_name("name"))
                    for m in _find_all(node, "method_definition")
                    if m.child_by_field_name("name")
                ]
                sig = f"class {name}"
                concepts.append(self._make_concept(
                    "Class", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, methods=methods, node=node, src_bytes=src_bytes))

            elif node.type == "lexical_declaration":
                # const/let foo = (...) => ...  or  const foo = function(...) {}
                for decl in _find_all(node, "variable_declarator"):
                    name_node  = decl.child_by_field_name("name")
                    value_node = decl.child_by_field_name("value")
                    if not name_node or not value_node:
                        continue
                    if value_node.type not in {"arrow_function", "function"}:
                        continue
                    name   = _node_text(name_node)
                    doc    = _prev_comment(node, src_bytes)
                    params = self._js_params(value_node)
                    ret    = self._js_return_type(value_node)
                    sig    = f"const {name} = ({params}) =>" + (f": {ret}" if ret else "")
                    concepts.append(self._make_concept(
                        "Function", name, doc, sig, resource, ts, parent_id,
                        node.start_point[0]+1, node=value_node, src_bytes=src_bytes))

        return concepts

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        from okf.linker import js_collect_imports
        return js_collect_imports(root, src_bytes)

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        from okf.linker import js_collect_calls
        return js_collect_calls(node, src_bytes)

    def _js_params(self, node) -> str:
        params_node = node.child_by_field_name("parameters") or \
                      node.child_by_field_name("parameter")
        if not params_node:
            return ""
        return _node_text(params_node).strip("()")

    def _js_return_type(self, node) -> str:
        ret = node.child_by_field_name("return_type")
        return _node_text(ret).lstrip(":").strip() if ret else ""


# ---------------------------------------------------------------------------
# Go  (tree-sitter)
# ---------------------------------------------------------------------------

class GoParser(TreeSitterParser):
    LANGUAGE   = "go"
    EXTENSIONS = {".go"}
    _TS_MODULE = "tree_sitter_go"
    _lang_obj  = None

    def _module_doc(self, root, src_bytes: bytes) -> str:
        # Package comment: comment block before "package" clause
        for child in root.children:
            if child.type == "package_clause":
                return _prev_comment(child, src_bytes)
        return ""

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []

        for node in _find_all(root, "function_declaration", "method_declaration", "type_declaration"):

            if node.type == "function_declaration":
                name = _node_text(node.child_by_field_name("name"))
                if not name:
                    continue
                doc    = _prev_comment(node, src_bytes)
                params = self._go_params(node)
                ret    = self._go_return(node)
                sig    = f"func {name}({params})" + (f" {ret}" if ret else "")
                concepts.append(self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes))

            elif node.type == "method_declaration":
                name = _node_text(node.child_by_field_name("name"))
                recv = node.child_by_field_name("receiver")
                recv_text = _node_text(recv) if recv else ""
                if not name:
                    continue
                doc    = _prev_comment(node, src_bytes)
                params = self._go_params(node)
                ret    = self._go_return(node)
                sig    = f"func {recv_text} {name}({params})" + (f" {ret}" if ret else "")
                concepts.append(self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes))

            elif node.type == "type_declaration":
                # type Foo struct { ... } or type Foo interface { ... }
                for spec in _find_all(node, "type_spec"):
                    name_node = spec.child_by_field_name("name")
                    type_node = spec.child_by_field_name("type")
                    if not name_node:
                        continue
                    name    = _node_text(name_node)
                    doc     = _prev_comment(node, src_bytes)
                    is_iface = type_node and type_node.type == "interface_type"
                    ctype   = "Interface" if is_iface else "Class"
                    sig     = f"type {name} struct" if not is_iface else f"type {name} interface"
                    methods = [
                        _node_text(f.child_by_field_name("name") or f)
                        for f in _find_all(type_node or spec, "field_declaration", "method_spec")
                        if _node_text(f.child_by_field_name("name") or f)
                    ] if type_node else []
                    concepts.append(self._make_concept(
                        ctype, name, doc, sig, resource, ts, parent_id,
                        node.start_point[0]+1, methods=methods, node=node, src_bytes=src_bytes))

        return concepts

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        from okf.linker import go_collect_imports
        return go_collect_imports(root, src_bytes)

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        from okf.linker import go_collect_calls
        return go_collect_calls(node, src_bytes)

    def _go_params(self, node) -> str:
        p = node.child_by_field_name("parameters")
        return _node_text(p).strip("()") if p else ""

    def _go_return(self, node) -> str:
        r = node.child_by_field_name("result")
        return _node_text(r) if r else ""


# ---------------------------------------------------------------------------
# Java  (tree-sitter)
# ---------------------------------------------------------------------------

class JavaParser(TreeSitterParser):
    LANGUAGE   = "java"
    EXTENSIONS = {".java"}
    _TS_MODULE = "tree_sitter_java"
    _lang_obj  = None

    def _module_doc(self, root, src_bytes: bytes) -> str:
        for child in root.children:
            if child.type == "class_declaration":
                return _prev_comment(child, src_bytes)
        return ""

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []

        for node in _find_all(root, "class_declaration", "interface_declaration", "enum_declaration"):
            name_node = node.child_by_field_name("name")
            if not name_node:
                continue
            name = _node_text(name_node)
            doc  = _prev_comment(node, src_bytes)
            # strip /** */ markers from Javadoc
            doc  = re.sub(r"/\*+|\*+/", "", doc).strip().lstrip("*").strip()

            # collect methods
            methods = []
            for method in _find_all(node, "method_declaration", "constructor_declaration"):
                mname = method.child_by_field_name("name")
                if mname:
                    methods.append(_node_text(mname))
                    # emit method as Function concept
                    mdoc    = _prev_comment(method, src_bytes)
                    mdoc    = re.sub(r"/\*+|\*+/", "", mdoc).strip().lstrip("*").strip()
                    mparams = self._java_params(method)
                    mret    = _node_text(method.child_by_field_name("type"))
                    msig    = f"{mret} {_node_text(mname)}({mparams})"
                    concepts.append(self._make_concept(
                        "Function", _node_text(mname), mdoc, msig,
                        resource, ts, parent_id, method.start_point[0]+1,
                        node=method, src_bytes=src_bytes))

            mods = node.child_by_field_name("modifiers")
            mod_text = _node_text(mods) + " " if mods else ""
            sig  = f"{mod_text}class {name}" if node.type == "class_declaration" else \
                   f"{mod_text}interface {name}" if node.type == "interface_declaration" else \
                   f"enum {name}"
            concepts.insert(0, self._make_concept(
                "Class", name, doc, sig, resource, ts, parent_id,
                node.start_point[0]+1, methods=methods, node=node, src_bytes=src_bytes))

        return concepts

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        from okf.linker import java_collect_imports
        return java_collect_imports(root, src_bytes)

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        from okf.linker import java_collect_calls
        return java_collect_calls(node, src_bytes)

    def _java_params(self, node) -> str:
        p = node.child_by_field_name("parameters")
        return _node_text(p).strip("()") if p else ""


# ---------------------------------------------------------------------------
# Rust  (tree-sitter)
# ---------------------------------------------------------------------------

class RustParser(TreeSitterParser):
    LANGUAGE   = "rust"
    EXTENSIONS = {".rs"}
    _TS_MODULE = "tree_sitter_rust"
    _lang_obj  = None

    def _module_doc(self, root, src_bytes: bytes) -> str:
        # //! inner doc comments at file top
        lines = src_bytes.decode(errors="replace").splitlines()
        doc_lines = []
        for line in lines:
            s = line.strip()
            if s.startswith("//!"):
                doc_lines.append(s[3:].strip())
            elif s and not s.startswith("//"):
                break
        return "\n".join(doc_lines)

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []

        for node in _find_all(root, "function_item", "struct_item", "enum_item",
                               "trait_item", "impl_item"):

            if node.type == "function_item":
                name_node = node.child_by_field_name("name")
                if not name_node:
                    continue
                name   = _node_text(name_node)
                doc    = _prev_comment(node, src_bytes)
                params = self._rust_params(node)
                ret    = self._rust_return(node)
                vis    = _node_text(node.child_by_field_name("visibility_modifier"))
                sig    = f"{vis+' ' if vis else ''}fn {name}({params})" + (f" -> {ret}" if ret else "")
                concepts.append(self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes))

            elif node.type in {"struct_item", "enum_item", "trait_item"}:
                name_node = node.child_by_field_name("name")
                if not name_node:
                    continue
                name  = _node_text(name_node)
                doc   = _prev_comment(node, src_bytes)
                kind  = {"struct_item": "struct", "enum_item": "enum", "trait_item": "trait"}[node.type]
                vis   = _node_text(node.child_by_field_name("visibility_modifier"))
                sig   = f"{vis+' ' if vis else ''}{kind} {name}"
                fields = [
                    _node_text(f.child_by_field_name("name"))
                    for f in _find_all(node, "field_declaration")
                    if f.child_by_field_name("name")
                ]
                concepts.append(self._make_concept(
                    "Class", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, methods=fields, node=node, src_bytes=src_bytes))

            elif node.type == "impl_item":
                type_node = node.child_by_field_name("type")
                type_name = _node_text(type_node) if type_node else ""
                for fn in _find_all(node, "function_item"):
                    fn_name = _node_text(fn.child_by_field_name("name"))
                    if not fn_name:
                        continue
                    doc    = _prev_comment(fn, src_bytes)
                    params = self._rust_params(fn)
                    ret    = self._rust_return(fn)
                    vis    = _node_text(fn.child_by_field_name("visibility_modifier"))
                    sig    = f"impl {type_name} {{ {vis+' ' if vis else ''}fn {fn_name}({params})" + \
                             (f" -> {ret}" if ret else "") + " }"
                    concepts.append(self._make_concept(
                        "Function", fn_name, doc, sig, resource, ts, parent_id,
                        fn.start_point[0]+1, node=fn, src_bytes=src_bytes))

        return concepts

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        from okf.linker import rust_collect_imports
        return rust_collect_imports(root, src_bytes)

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        from okf.linker import rust_collect_calls
        return rust_collect_calls(node, src_bytes)

    def _rust_params(self, node) -> str:
        p = node.child_by_field_name("parameters")
        return _node_text(p).strip("()") if p else ""

    def _rust_return(self, node) -> str:
        r = node.child_by_field_name("return_type")
        return _node_text(r) if r else ""


# ---------------------------------------------------------------------------
# Ruby  (tree-sitter)
# ---------------------------------------------------------------------------

class RubyParser(TreeSitterParser):
    LANGUAGE   = "ruby"
    EXTENSIONS = {".rb"}
    _TS_MODULE = "tree_sitter_ruby"
    _lang_obj  = None

    def _module_doc(self, root, src_bytes: bytes) -> str:
        for child in root.children:
            if child.type not in {"comment", ""}:
                return _prev_comment(child, src_bytes)
        return ""

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []

        for node in _find_all(root, "method", "class", "module"):
            name_node = node.child_by_field_name("name")
            if not name_node:
                continue
            name = _node_text(name_node)
            doc  = _prev_comment(node, src_bytes)

            if node.type == "method":
                params = self._ruby_params(node)
                sig    = f"def {name}({params})"
                concepts.append(self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes))

            elif node.type in {"class", "module"}:
                methods = [
                    _node_text(m.child_by_field_name("name"))
                    for m in _find_all(node, "method")
                    if m.child_by_field_name("name")
                ]
                sig = f"class {name}" if node.type == "class" else f"module {name}"
                concepts.append(self._make_concept(
                    "Class", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, methods=methods, node=node, src_bytes=src_bytes))

        return concepts

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        from okf.linker import ruby_collect_imports
        return ruby_collect_imports(root, src_bytes)

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        from okf.linker import ruby_collect_calls
        return ruby_collect_calls(node, src_bytes)

    def _ruby_params(self, node) -> str:
        p = node.child_by_field_name("parameters") or node.child_by_field_name("method_parameters")
        return _node_text(p).strip("()") if p else ""


# ---------------------------------------------------------------------------
# SQL parser (tree-sitter)
# ---------------------------------------------------------------------------

class SQLParser(TreeSitterParser):
    LANGUAGE   = "sql"
    EXTENSIONS = {".sql"}
    _TS_MODULE = "tree_sitter_sql"
    _lang_obj  = None

    _KIND_MAP = {
        "create_table": "Table",
        "create_view": "View",
        "create_function": "Function",
        "create_procedure": "Function",
        "create_index": "Index",
        "create_trigger": "Trigger",
        "create_type": "Type",
    }

    def _module_doc(self, root, src_bytes: bytes) -> str:
        for child in root.children:
            if child.type not in {"comment", "marginalia", ""}:
                return _prev_comment(child, src_bytes)
        return ""

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []
        for stmt in root.children:
            if stmt.type != "statement" or not stmt.children:
                continue
            inner = stmt.children[0]
            ctype = self._KIND_MAP.get(inner.type)
            if ctype is None:
                continue

            name = self._sql_name(inner, ctype)
            if not name:
                continue
            doc = _prev_comment(inner, src_bytes)
            sig = _node_text(inner)
            if len(sig) > 200:
                sig = sig[:200] + " ..."

            if ctype == "Function":
                params = self._sql_params(inner)
                sig = f"{'CREATE OR REPLACE ' if any(c.type == 'keyword_replace' for c in inner.children) else 'CREATE '}{inner.type.upper().split('_')[1]} {name}({params})"
                concepts.append(self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    inner.start_point[0]+1, node=inner, src_bytes=src_bytes))
            else:
                cid = re.sub(r"\.[^/]+$", "", resource).replace(os.sep, "/")
                concepts.append(Concept(
                    type=ctype, title=name,
                    description=_first_line(doc) or f"{ctype} defined in {Path(resource).name}",
                    docstring=doc, signature=sig,
                    resource=resource, tags=[self.LANGUAGE, ctype.lower()],
                    timestamp=ts, source_lines=(inner.start_point[0]+1, inner.end_point[0]+1),
                    concept_id=f"{cid}/{_safe_id(name)}",
                    related=[parent_id],
                ))
        return concepts

    @staticmethod
    def _sql_name(node, ctype: str) -> str:
        for c in node.children:
            if c.type == "object_reference":
                for cc in c.children:
                    if cc.type == "identifier":
                        return _node_text(cc)
            if c.type == "identifier" and ctype == "Index":
                return _node_text(c)
        return ""

    @staticmethod
    def _sql_params(node) -> str:
        for c in node.children:
            if c.type == "function_arguments":
                return _node_text(c).strip("()")
        return ""


# ---------------------------------------------------------------------------
# Parser registry
# ---------------------------------------------------------------------------

def _get_parser(ext: str):
    if ext in {".py"}:
        return PythonParser()
    if ext in {".js", ".jsx", ".mjs", ".cjs"}:
        return JSTSParser()
    if ext in {".ts", ".tsx"}:
        p = JSTSParser()
        p._path_ext = ext
        return p
    if ext in {".go"}:
        return GoParser()
    if ext in {".java"}:
        return JavaParser()
    if ext in {".rs"}:
        return RustParser()
    if ext in {".rb"}:
        return RubyParser()
    if ext in {".sql"}:
        return SQLParser()
    return None



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Exact directory names to skip
SKIP_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", ".mypy_cache", ".pytest_cache",
    "node_modules", ".venv", "venv", "env", ".env", "dist", "build",
    ".tox", "htmlcov", ".eggs", "vendor", "target", "coverage",
    ".next", ".nuxt", "__snapshots__", ".cache", "tmp", "temp", "logs",
    "static", "media", "assets",
}

# Suffix-based skip patterns (replaces broken glob strings in sets)
SKIP_DIR_SUFFIXES = (".egg-info", ".dist-info")

def _safe_id(name: str) -> str:
    """Convert symbol name to safe file/concept ID."""
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", name).strip("_") or "unknown"


def _first_line(text: str) -> str:
    if not text:
        return ""
    return text.strip().splitlines()[0].strip()


def _git_info(repo_root: Path) -> dict:
    """Get git metadata for tagging. Returns empty dict if not a git repo."""
    info = {}
    try:
        branch = subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL, timeout=3
        ).decode().strip()
        info["branch"] = branch

        remote = subprocess.check_output(
            ["git", "-C", str(repo_root), "remote", "get-url", "origin"],
            stderr=subprocess.DEVNULL, timeout=3
        ).decode().strip()
        # extract repo name from remote URL
        repo_name = re.sub(r".*[:/](.+?)(\.git)?$", r"\1", remote)
        info["repo"] = repo_name
    except Exception:
        pass
    return info


def _make_tags(language: str, resource: str, concept_type: str, git: dict) -> list[str]:
    """Build standardised OKF tags for a concept.

    Tag categories (order is intentional — most stable first):
      lang:<language>        e.g. lang:python
      type:<ConceptType>     e.g. type:Function
      module:<top_dir>       e.g. module:StockAI  (top-level source folder)
      domain:<second_dir>    e.g. domain:RnD       (second-level folder)
      git:branch:<name>      e.g. git:branch:main
      git:repo:<name>        e.g. git:repo:TrainLLMs
    """
    tags = []
    tags.append(f"lang:{language}")
    tags.append(f"type:{concept_type}")

    # module + domain from resource path
    parts = resource.replace("\\", "/").replace(os.sep, "/").split("/")
    if parts:
        tags.append(f"module:{parts[0]}")
    if len(parts) > 1:
        tags.append(f"domain:{parts[1]}")

    if git.get("branch"):
        tags.append(f"git:branch:{git['branch']}")
    if git.get("repo"):
        tags.append(f"git:repo:{git['repo']}")

    return tags


def _dedup_concept_ids(concepts: list[Concept]) -> list[Concept]:
    seen: dict[str, int] = {}
    for c in concepts:
        base = c.concept_id
        if base in seen:
            seen[base] += 1
            c.concept_id = f"{base}_{seen[base]}"
        else:
            seen[base] = 0
    return concepts


# ---------------------------------------------------------------------------
# OKF document renderer
# ---------------------------------------------------------------------------

def _frontmatter(concept: Concept) -> str:
    fm: dict = {"type": concept.type}
    if concept.title:
        fm["title"] = concept.title
    if concept.description:
        fm["description"] = concept.description
    if concept.resource:
        fm["resource"] = concept.resource
    if concept.tags:
        fm["tags"] = concept.tags
    if concept.timestamp:
        fm["timestamp"] = concept.timestamp
    return "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True) + "---\n"


def _body(concept: Concept, all_concepts: dict[str, Concept]) -> str:
    lines = [f"# {concept.title}\n"]

    if concept.description:
        lines.append(f"{concept.description}\n")

    if concept.type == "Dependency" and concept.body_extra:
        be = concept.body_extra
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        lines.append(f"| Ecosystem | `{be.get('ecosystem', '')}` |")
        lines.append(f"| Version constraint | `{be.get('version_constraint', '')}` |")
        lines.append(f"| Source manifest | `{be.get('source_manifest', '')}` |")
        lines.append(f"| Dev dependency | `{'yes' if be.get('dev_dependency') else 'no'}` |")
        used_by = be.get("used_by") or []
        lines.append(f"| Used by | {len(used_by)} module(s) |")
        lines.append("")
        if used_by:
            lines.append("## Used By\n")
            for cid in used_by:
                rel_concept = all_concepts.get(cid)
                label = rel_concept.title if rel_concept else cid.split("/")[-1]
                lines.append(f"- [{label}](/{cid}.md)")
            lines.append("")
        return "\n".join(lines)

    if concept.signature:
        lines.append("## Signature\n")
        lang_fence = "python"
        for t in concept.tags:
            if t.startswith("lang:"):
                lang_fence = t.removeprefix("lang:")
                break
        lines.append(f"```{lang_fence}\n{concept.signature}\n```\n")

    if concept.docstring:
        lines.append("## Docstring\n")
        lines.append(f"{concept.docstring}\n")

    if concept.params:
        lines.append("## Parameters\n")
        lines.append("| Name | Type | Default |")
        lines.append("|------|------|---------|")
        for p in concept.params:
            lines.append(f"| `{p['name']}` | `{p['annotation'] or '—'}` | `{p['default'] or '—'}` |")
        lines.append("")

    if concept.returns:
        lines.append(f"## Returns\n`{concept.returns}`\n")

    if concept.methods:
        lines.append("## Methods\n")
        for m in concept.methods:
            lines.append(f"- `{m}`")
        lines.append("")

    if concept.source_lines and concept.source_lines[0]:
        start, end = concept.source_lines
        lines.append(f"## Source\nLines {start}–{end} in `{concept.resource}`\n")

    if concept.related:
        lines.append("## Related\n")
        for cid in concept.related:
            rel_concept = all_concepts.get(cid)
            if rel_concept:
                label = rel_concept.title
                # relative link: concept lives at concept_id + ".md" from bundle root
                lines.append(f"- [{label}](/{cid}.md)")
            else:
                # cid not found — may be stale; show as plain text
                label = cid.split("/")[-1]
                lines.append(f"- {label} *(unresolved)*")
        lines.append("")

    if concept.calls:
        lines.append("## Calls\n")
        for cid in concept.calls:
            rel_concept = all_concepts.get(cid)
            label = rel_concept.title if rel_concept else cid.split("/")[-1]
            lines.append(f"- [{label}](/{cid}.md)")
        lines.append("")

    if concept.called_by:
        lines.append("## Called By\n")
        for cid in concept.called_by:
            rel_concept = all_concepts.get(cid)
            label = rel_concept.title if rel_concept else cid.split("/")[-1]
            lines.append(f"- [{label}](/{cid}.md)")
        lines.append("")

    return "\n".join(lines)


def render_concept(concept: Concept, all_concepts: dict[str, Concept]) -> str:
    return _frontmatter(concept) + "\n" + _body(concept, all_concepts)


def render_dir_index(
    dir_path: str,
    subdirs: list[str],
    concepts: list["Concept"],
    bundle_name: str,
    all_map: dict[str, "Concept"],
) -> str:
    """Render index.md for a directory node in the resource tree."""
    title = dir_path.split("/")[-1] if dir_path else bundle_name
    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    fm = {
        "type": "Index",
        "title": title,
        "description": f"Knowledge index for {dir_path or bundle_name}",
        "resource": dir_path,
        "okf_version": "0.1" if not dir_path else None,
        "timestamp": ts,
    }
    # remove None values
    fm = {k: v for k, v in fm.items() if v is not None}

    lines = [
        "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True) + "---\n",
        f"# {title}\n",
    ]

    if subdirs:
        lines.append("## Subdirectories\n")
        for sd in sorted(subdirs):
            label = sd.split("/")[-1]
            lines.append(f"- [{label}]({label}/index.md)")
        lines.append("")

    if concepts:
        # group by type for readability
        by_type: dict[str, list] = {}
        for c in concepts:
            by_type.setdefault(c.type, []).append(c)

        def _plural(t: str) -> str:
            return "Dependencies" if t == "Dependency" else f"{t}s"

        for ctype in ("Module", "Class", "Function", "Method", "Dependency"):
            group = by_type.get(ctype, [])
            if not group:
                continue
            lines.append(f"## {_plural(ctype)}\n")
            for c in sorted(group, key=lambda x: x.title.lower()):
                filename = c.concept_id.split("/")[-1] + ".md"
                desc = f" — {c.description}" if c.description else ""
                lines.append(f"- [{c.title}]({filename}){desc}")
            lines.append("")

    return "\n".join(lines)


def render_root_index(bundle_name: str, top_dirs: list[str], total: int, ts: str) -> str:
    fm = {
        "type": "Index",
        "title": bundle_name,
        "description": f"OKF v0.1 bundle generated from the {bundle_name} codebase",
        "okf_version": "0.1",
        "timestamp": ts,
    }
    lines = [
        "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True) + "---\n",
        f"# {bundle_name}\n",
        f"OKF v0.1 knowledge bundle — {total} concepts across {len(top_dirs)} top-level directories.\n",
        "## Top-level Directories\n",
    ]
    for d in sorted(top_dirs):
        lines.append(f"- [{d}]({d}/index.md)")
    lines.append("")
    return "\n".join(lines)


def render_log(entries: list[str]) -> str:
    fm = {
        "type": "Log",
        "title": "Change Log",
        "description": "Chronological history of bundle generation",
        "timestamp": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    lines = [
        "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True) + "---\n",
        "# Change Log\n",
    ]
    for e in entries:
        lines.append(f"- {e}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# SUMMARY.md generator
# ---------------------------------------------------------------------------

def render_summary(
    bundle_name: str,
    concepts: list[Concept],
    output_dir: Path,
    git: dict,
) -> str:
    """Generate a single SUMMARY.md — the top-level entry point for OpenCode.

    Groups concepts by top-level domain (first path segment of resource),
    then by module within each domain. Includes concept counts, descriptions,
    and direct links so an AI agent can navigate the whole bundle from one file.
    """
    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ── Separate dependencies from code concepts ──────────────────────────
    code_concepts = [c for c in concepts if c.type != "Dependency"]
    dep_concepts  = [c for c in concepts if c.type == "Dependency"]

    # ── Group by domain → module → concepts ──────────────────────────────
    # domain  = first path segment  (e.g. "StockAI")
    # module  = resource path without extension (e.g. "StockAI/RnD/python/connectors/economic_data")
    domains: dict[str, dict[str, list[Concept]]] = defaultdict(lambda: defaultdict(list))

    for c in code_concepts:
        parts = c.resource.replace("\\", "/").replace(os.sep, "/").split("/")
        domain = parts[0] if parts else "root"
        module = re.sub(r"\.[^/]+$", "", c.resource).replace(os.sep, "/")
        domains[domain][module].append(c)

    # ── Stats ─────────────────────────────────────────────────────────────
    total      = len(concepts)
    n_modules  = len({re.sub(r"\.[^/]+$", "", c.resource) for c in code_concepts})
    n_domains  = len(domains)
    by_type    = {}
    for c in concepts:
        by_type[c.type] = by_type.get(c.type, 0) + 1

    # ── Languages ─────────────────────────────────────────────────────────
    langs: dict[str, int] = {}
    for c in concepts:
        for tag in c.tags:
            if tag.startswith("lang:"):
                lang = tag[5:]
                langs[lang] = langs.get(lang, 0) + 1
                break

    # ── Frontmatter ───────────────────────────────────────────────────────
    fm: dict = {
        "type":        "Index",
        "title":       f"{bundle_name} — Knowledge Summary",
        "description": f"Top-level OKF summary: {total} concepts across {n_domains} domains and {n_modules} modules",
        "okf_version": "0.1",
        "timestamp":   ts,
    }
    if git.get("repo"):
        fm["git_repo"] = git["repo"]
    if git.get("branch"):
        fm["git_branch"] = git["branch"]

    lines = [
        "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True) + "---\n",
        f"# {bundle_name} — Knowledge Summary\n",
        f"> OKF v0.1 bundle | {total:,} concepts | {n_domains} domains | {n_modules} modules\n",
    ]

    # ── Quick stats table ─────────────────────────────────────────────────
    lines.append("## Stats\n")
    lines.append("| Type | Count |")
    lines.append("|------|-------|")
    for ctype, count in sorted(by_type.items(), key=lambda x: -x[1]):
        lines.append(f"| {ctype} | {count:,} |")
    if langs:
        lines.append("")
        lines.append("| Language | Concepts |")
        lines.append("|----------|----------|")
        for lang, count in sorted(langs.items(), key=lambda x: -x[1]):
            lines.append(f"| {lang} | {count:,} |")
    lines.append("")

    # ── Domain map ────────────────────────────────────────────────────────
    lines.append("## Domain Map\n")
    lines.append("Use these links to navigate the bundle or prime an AI agent with focused context.\n")

    for domain in sorted(domains.keys()):
        modules    = domains[domain]
        dom_total  = sum(len(v) for v in modules.values())
        dom_index  = f"{domain}/index.md"
        lines.append(f"### [{domain}]({dom_index}) — {dom_total:,} concepts\n")

        # show up to 8 modules per domain, sorted by concept count desc
        sorted_mods = sorted(modules.items(), key=lambda x: -len(x[1]))
        for mod_path, mod_concepts in sorted_mods[:8]:
            n          = len(mod_concepts)
            mod_index  = f"{mod_path.rstrip('/')}/index.md"  # not entirely accurate but navigable
            # pick the module concept for description
            mod_desc   = ""
            for mc in mod_concepts:
                if mc.type == "Module" and mc.description:
                    mod_desc = f" — {mc.description[:80]}"
                    break
            lines.append(f"- [{mod_path}]({mod_index}) ({n} concepts){mod_desc}")

        if len(sorted_mods) > 8:
            lines.append(f"- *…and {len(sorted_mods) - 8} more modules*")
        lines.append("")

    # ── Dependencies (compact ecosystem summary) ──────────────────────────
    if dep_concepts:
        lines.append("## Dependencies\n")
        lines.append("> Full list at [`_dependencies/index.md`](/_dependencies/index.md) or `okf lookup --type Dependency`\n")
        eco_count: dict[str, int] = {}
        for c in dep_concepts:
            eco = c.body_extra.get("ecosystem", "?")
            eco_count[eco] = eco_count.get(eco, 0) + 1
        lines.append("| Ecosystem | Packages |")
        lines.append("|----------|----------|")
        for eco, count in sorted(eco_count.items(), key=lambda x: -x[1]):
            lines.append(f"| {eco} | {count:,} |")
        lines.append("")

    # ── Key concepts (top 20 by description quality) ──────────────────────
    lines.append("## Key Concepts\n")
    lines.append("Highest-value concepts across all domains (Classes and Functions with rich descriptions).\n")

    key = [
        c for c in concepts
        if c.type in {"Class", "Function"} and len(c.description) > 40
    ]
    key_sorted = sorted(key, key=lambda c: -len(c.description))[:20]

    if key_sorted:
        lines.append("| Concept | Type | Module | Description |")
        lines.append("|---------|------|--------|-------------|")
        for c in key_sorted:
            link   = f"[{c.title}](/{c.concept_id}.md)"
            module = "/".join(c.resource.replace(os.sep, "/").split("/")[:3])
            desc   = c.description[:60] + ("…" if len(c.description) > 60 else "")
            lines.append(f"| {link} | {c.type} | `{module}` | {desc} |")
        lines.append("")

    # ── OpenCode usage hint ───────────────────────────────────────────────
    lines.append("## Usage with OpenCode\n")
    lines.append("```bash")
    lines.append("# Prime full context")
    lines.append("RUN cat ./okf_bundle/SUMMARY.md")
    lines.append("")
    lines.append("# Prime specific domain")
    if domains:
        lines.append(f"RUN cat ./okf_bundle/{sorted(domains.keys())[0]}/index.md")
    else:
        lines.append("RUN cat ./okf_bundle/<domain>/index.md")
    lines.append("")
    lines.append("# Find a concept")
    lines.append("RUN find ./okf_bundle -name '<ConceptName>.md' | xargs cat")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def write_summary(
    bundle_name: str,
    concepts: list[Concept],
    output_dir: Path,
    git: dict,
) -> Path:
    """Write SUMMARY.md to bundle root. Returns the path written."""
    content = render_summary(bundle_name, concepts, output_dir, git)
    out     = output_dir / "SUMMARY.md"
    out.write_text(content, encoding="utf-8")
    return out

# ---------------------------------------------------------------------------
# LLM enrichment (optional)
# ---------------------------------------------------------------------------

ENRICH_PROMPT = """\
You are enriching an OKF (Open Knowledge Format) knowledge bundle for a codebase.

Given this code concept, return a JSON object with two fields:

  "description" - one clear sentence (max 20 words) summarising what it does,
                   specific enough to be useful to a developer or AI agent.
  "docstring"    - a full docstring in Google style:
                     - First line: one-sentence summary.
                     - Args section (if it has parameters).
                     - Returns section (if it returns something).
                     - Raises section (if relevant).
                   Omit sections that do not apply.

Rules:
- Both fields must reference specific names or behaviour from THIS concept.
- Do NOT invent parameters or return types that are not in the signature.
- If the existing docstring is already detailed (>80 chars), improve it slightly
  rather than replacing it completely.
- Reply with ONLY the JSON object, no markdown fences, no preamble.

Concept type: {type}
Name: {title}
Existing docstring: {docstring}
Signature: {signature}
Parameters: {params}
Returns: {returns}
"""


def enrich_concept(concept: Concept, client, model: str) -> Concept:
    needs_desc = not concept.description or len(concept.description) <= 120
    needs_doc  = not concept.docstring or len(concept.docstring) <= 80

    # nothing to do
    if not needs_desc and not needs_doc:
        return concept

    # only enrich functions and classes — modules get description from first docstring line
    if concept.type not in {"Function", "Class", "Method"}:
        if needs_desc and concept.docstring:
            concept.description = concept.docstring.strip().splitlines()[0][:120]
        return concept

    # build param summary for the prompt
    params_summary = ", ".join(
        p["name"] + (f": {p['annotation']}" if p.get("annotation") else "")
        for p in (concept.params or [])
    ) or "none"

    prompt = ENRICH_PROMPT.format(
        type=concept.type,
        title=concept.title,
        docstring=concept.docstring[:500] if concept.docstring else "none",
        signature=concept.signature or "none",
        params=params_summary,
        returns=concept.returns or "none",
    )

    raw = ""  # ensure always bound before try/except
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.1,
        )
        raw = (resp.choices[0].message.content or "").strip()

        # strip markdown fences if model wraps anyway
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw).strip()

        data = json.loads(raw)

        if needs_desc and data.get("description"):
            concept.description = data["description"].strip()

        if needs_doc and data.get("docstring"):
            concept.docstring = data["docstring"].strip()

    except json.JSONDecodeError:
        # fallback: treat whole response as description only
        if needs_desc and raw:
            concept.description = raw.splitlines()[0][:120]
        log.debug(f"JSON parse failed for {concept.title}, used fallback")
    except Exception as e:
        log.debug(f"Enrichment failed for {concept.title}: {e}")

    return concept


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def _walk_source_dirs(root: Path) -> set[str]:
    """All non-hidden, non-skipped directories under root (relative posix paths,
    '' for root itself). Used so directories with no parseable concepts —
    including genuinely empty ones — still appear in the bundle layout."""
    dirs = {""}
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        rel_parts = path.relative_to(root).parts
        if any(
            part.startswith(".") or
            part in SKIP_DIRS or
            any(part.endswith(sfx) for sfx in SKIP_DIR_SUFFIXES)
            for part in rel_parts
        ):
            continue
        dirs.add("/".join(rel_parts))
    return dirs


def scan_codebase(root: Path, exclude: list[str] | None = None) -> list[Concept]:
    git = _git_info(root)
    if git:
        log.info(f"Git: repo={git.get('repo','?')} branch={git.get('branch','?')}")

    if not root.exists() or not root.is_dir():
        log.warning(f"Source directory does not exist or is not a directory: {root}")
        return []

    exclude = exclude or []
    concepts = []
    all_paths = sorted(root.rglob("*"))
    log.info(f"Scanning {len(all_paths)} paths...")

    for path in all_paths:
        rel = path.relative_to(root)
        # per-run exclude patterns (e.g. --exclude tests, --exclude docs)
        if any(part in exclude for part in rel.parts):
            continue
        # skip hidden / vendor dirs (only check relative to root, not absolute prefix)
        if any(
            part.startswith(".") or
            part in SKIP_DIRS or
            any(part.endswith(sfx) for sfx in SKIP_DIR_SUFFIXES)
            for part in rel.parts
        ):
            continue
        if not path.is_file():
            continue
        if manifest_scanner.is_manifest_file(path):
            try:
                raw_deps = manifest_scanner.scan_manifest(path, root)
                for d in raw_deps:
                    # Merge standardised tags with ecosystem-specific tags from the scanner
                    base = _make_tags(language="manifest", resource=d["resource"],
                                      concept_type=d["type"], git=git)
                    existing = set(d.get("tags", []))
                    merged = list(dict.fromkeys(base + [t for t in existing if not t.startswith(("lang:", "type:", "module:", "domain:", "git:"))]))
                    c = Concept(
                        type=d["type"], title=d["title"],
                        description=d["description"], resource=d["resource"],
                        tags=merged,
                        timestamp=d["timestamp"], concept_id=d["concept_id"],
                        body_extra=d.get("body_extra", {}),
                    )
                    concepts.append(c)
                log.debug(f"Parsed manifest {path}: {len(raw_deps)} deps")
            except Exception as e:
                log.warning(f"Failed to parse manifest {path}: {e}")
            continue
        parser = _get_parser(path.suffix.lower())
        if parser is None:
            continue
        try:
            file_concepts = parser.parse_file(path, root)
            for c in file_concepts:
                c.tags = _make_tags(
                    language=parser.LANGUAGE,
                    resource=c.resource,
                    concept_type=c.type,
                    git=git,
                )
            concepts.extend(file_concepts)
            log.debug(f"Parsed {path}: {len(file_concepts)} concepts")
        except Exception as e:
            log.warning(f"Failed to parse {path}: {e}")

    if not concepts:
        log.warning(f"No recognized source files found under {root} — bundle will be empty.")
        return concepts

    from okf.linker import link_all
    stats = link_all(concepts)
    log.info(stats.summary_line())

    return concepts


# ---------------------------------------------------------------------------
# Writer  (domain/resource-path layout)
# ---------------------------------------------------------------------------

def _concept_output_path(concept: Concept, output_dir: Path) -> Path:
    """Map concept_id to output .md path, mirroring the source tree."""
    return output_dir.joinpath(*concept.concept_id.split("/")).with_suffix(".md")


def write_bundle(
    concepts: list[Concept],
    output_dir: Path,
    bundle_name: str,
    log_entries: list[str],
    source_dirs: set[str] | None = None,
):
    output_dir.mkdir(parents=True, exist_ok=True)

    concepts = _dedup_concept_ids(concepts)
    all_map: dict[str, Concept] = {c.concept_id: c for c in concepts}

    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ── 1. Write every concept file (skip already-enriched ones) ────────────
    enrich_enabled = os.environ.get("OKF_ENRICH") == "1"
    for c in concepts:
        out_path = _concept_output_path(c, output_dir)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # If enrichment is enabled and file already exists with rich content,
        # skip overwriting — the enrichment pass already wrote the best version
        if enrich_enabled and out_path.exists():
            try:
                existing = out_path.read_text(encoding="utf-8", errors="replace")
                fm_parts = existing.split("---", 2)
                if len(fm_parts) >= 2:
                    fm = yaml.safe_load(fm_parts[1]) or {}
                    if len(fm.get("description", "")) > 60:
                        continue  # keep enriched version
            except Exception:
                pass
        out_path.write_text(render_concept(c, all_map), encoding="utf-8")

    # ── 2. Build directory tree from all concept paths ────────────────────
    # dir_path (relative to output_dir) → {"subdirs": set, "concepts": list}
    dir_tree: dict[str, dict] = {}

    def _ensure_dir(rel: str):
        if rel not in dir_tree:
            dir_tree[rel] = {"subdirs": set(), "concepts": []}

    def _register_ancestors(rel_dir: str):
        parts = rel_dir.split("/") if rel_dir else []
        for i in range(len(parts)):
            parent = "/".join(parts[:i]) if i > 0 else ""
            child  = "/".join(parts[:i+1])
            _ensure_dir(parent)
            _ensure_dir(child)
            dir_tree[parent]["subdirs"].add(child)

    for c in concepts:
        out_path = _concept_output_path(c, output_dir)
        rel_dir = str(out_path.parent.relative_to(output_dir)).replace(os.sep, "/")
        if rel_dir == ".":
            rel_dir = ""
        _ensure_dir(rel_dir)
        dir_tree[rel_dir]["concepts"].append(c)
        _register_ancestors(rel_dir)

    # ── 2b. Register directories with no concepts at all (empty folders, or
    #        folders containing only files in unsupported formats) so they
    #        still show up in the navigation instead of disappearing ───────
    for rel_dir in (source_dirs or set()):
        rel_dir = rel_dir.replace(os.sep, "/")
        _ensure_dir(rel_dir)
        _register_ancestors(rel_dir)

    # ── 3. Write index.md at every directory level ────────────────────────
    for rel_dir, node in dir_tree.items():
        dir_abs = output_dir / rel_dir if rel_dir else output_dir
        dir_abs.mkdir(parents=True, exist_ok=True)
        index_content = render_dir_index(
            dir_path=rel_dir,
            subdirs=list(node["subdirs"]),
            concepts=node["concepts"],
            bundle_name=bundle_name,
            all_map=all_map,
        )
        (dir_abs / "index.md").write_text(index_content, encoding="utf-8")

    # ── 4. Root index ─────────────────────────────────────────────────────
    top_dirs = sorted(dir_tree.get("", {}).get("subdirs", set()))
    (output_dir / "index.md").write_text(
        render_root_index(bundle_name, top_dirs, len(concepts), ts),
        encoding="utf-8",
    )

    # ── 5. Log ────────────────────────────────────────────────────────────
    (output_dir / "log.md").write_text(render_log(log_entries), encoding="utf-8")

    # return summary grouped by type (for printing)
    by_type: dict[str, list] = {}
    for c in concepts:
        by_type.setdefault(c.type, []).append(c)
    return by_type


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def setup_logging():
    level = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    setup_logging()

    # --summarize mode: regenerate SUMMARY.md from existing bundle (no re-scan)
    if len(sys.argv) >= 2 and sys.argv[1] == "--summarize":
        bundle_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path("okf_bundle").resolve()
        if not bundle_dir.exists():
            log.error(f"Bundle directory not found: {bundle_dir}")
            sys.exit(1)
        log.info(f"Regenerating SUMMARY.md from existing bundle: {bundle_dir}")
        # load concepts from existing bundle by parsing all .md files
        from okf.pairs import load_bundle as _load_md
        raw = _load_md(bundle_dir)
        # reconstruct minimal Concept objects for summary
        regen_concepts = []
        for r in raw:
            c = Concept(
                type=r.get("type",""),
                title=r.get("title",""),
                description=r.get("description",""),
                resource=r.get("resource",""),
                tags=r.get("tags",[]),
                concept_id=r.get("concept_id",""),
            )
            regen_concepts.append(c)
        out = write_summary(bundle_dir.name, regen_concepts, bundle_dir, {})
        log.info(f"SUMMARY.md written -> {out}")
        return

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    source_dir = Path(sys.argv[1]).resolve()
    output_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path("okf_bundle").resolve()

    # Parse --exclude flags (can be repeated)
    exclude = []
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == "--exclude" and i + 1 < len(sys.argv):
            exclude.append(sys.argv[i + 1])
            i += 2
        else:
            i += 1

    if not source_dir.exists():
        log.error(f"Source directory not found: {source_dir}")
        sys.exit(1)

    bundle_name = source_dir.name
    log.info(f"Scanning: {source_dir}")
    log.info(f"Output:   {output_dir}")
    if exclude:
        log.info(f"Excluding: {', '.join(exclude)}")

    # --- Scan ---
    concepts = scan_codebase(source_dir, exclude=exclude)
    log.info(f"Found {len(concepts)} concepts")

    if not concepts:
        log.warning(
            "No concepts found — the source directory is empty or has no "
            "recognized source files. Writing an empty bundle anyway."
        )

    # --- Optional LLM enrichment (resumable) ---
    enrich = os.environ.get("OKF_ENRICH") == "1"
    if enrich:
        api_key     = os.environ.get("OKF_API_KEY", "")
        base_url    = os.environ.get("OKF_BASE_URL", "https://api.anthropic.com/v1")
        model       = os.environ.get("OKF_MODEL", "claude-sonnet-4-6")
        max_workers = int(os.environ.get("OKF_MAX_WORKERS", "2"))

        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=base_url)
            log.info(f"LLM enrichment enabled: {model} @ {base_url}")

            # Prepare output dirs and lookup so we can write each file immediately
            output_dir.mkdir(parents=True, exist_ok=True)
            concepts = _dedup_concept_ids(concepts)
            all_map_enrich: dict[str, Concept] = {c.concept_id: c for c in concepts}

            def _concept_path(c: Concept) -> Path:
                return _concept_output_path(c, output_dir)

            def _is_already_enriched(c: Concept) -> bool:
                """Return True if the on-disk .md already has rich description + docstring."""
                p = _concept_path(c)
                if not p.exists():
                    return False
                try:
                    raw = p.read_text(encoding="utf-8", errors="replace")
                    parts = raw.split("---", 2)
                    if len(parts) < 3:
                        return False
                    fm = yaml.safe_load(parts[1]) or {}
                    desc = fm.get("description", "")
                    has_doc = "## Docstring" in parts[2] and len(parts[2]) > 200
                    return len(desc) > 120 and has_doc
                except Exception:
                    return False

            def _enrich_and_write(c: Concept) -> Concept:
                enriched = enrich_concept(c, client, model)
                path = _concept_path(enriched)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(render_concept(enriched, all_map_enrich), encoding="utf-8")
                return enriched

            to_enrich   = [c for c in concepts if c.type in {"Function", "Class", "Method"} and not _is_already_enriched(c)]
            skipped_ok  = sum(1 for c in concepts if c.type in {"Function", "Class", "Method"} and _is_already_enriched(c))
            log.info(f"To enrich: {len(to_enrich)}  |  already done (skipped): {skipped_ok}")

            done = errors = 0
            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {pool.submit(_enrich_and_write, c): c for c in to_enrich}
                for future in tqdm(as_completed(futures), total=len(futures), desc="Enriching"):
                    try:
                        future.result()
                        done += 1
                    except Exception as e:
                        errors += 1
                        log.debug(f"Enrichment error: {e}")

            log.info(f"Enrichment complete: {done} enriched, {errors} errors, {skipped_ok} skipped")

        except ImportError:
            log.warning("openai not installed — skipping enrichment")

    # --- Write bundle ---
    log_entries = [
        f"{datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} — Bundle generated from `{source_dir}`",
        f"  Source files scanned: {len(set(c.resource for c in concepts))}",
        f"  Total concepts: {len(concepts)}",
        f"  LLM enrichment: {'enabled' if enrich else 'disabled'}",
    ]

    by_type = write_bundle(
        concepts, output_dir, bundle_name, log_entries,
        source_dirs=_walk_source_dirs(source_dir),
    )

    # --- Write SUMMARY.md ---
    git = _git_info(source_dir)
    summary_path = write_summary(bundle_name, concepts, output_dir, git)
    log.info(f"SUMMARY.md written -> {summary_path}")

    # --- Summary ---
    print(f"\n{'='*55}")
    print(f"  Bundle: {bundle_name}")
    print(f"  Output: {output_dir}")
    print(f"  {'Type':<15} {'Concepts':>8}")
    print(f"  {'-'*24}")
    for ctype, items in sorted(by_type.items()):
        print(f"  {ctype:<15} {len(items):>8}")
    print(f"  {'─'*24}")
    print(f"  {'TOTAL':<15} {len(concepts):>8}")
    print(f"{'='*55}\n")
    log.info(f"OKF bundle written → {output_dir}")


if __name__ == "__main__":
    main()
