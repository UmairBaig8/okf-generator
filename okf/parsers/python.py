"""Python parser using stdlib ast module. Extracts: functions (sync/async), classes, methods, params with annotations+defaults, return types, decorators, inheritance, fields, docstrings, calls."""
import os
import re

import ast

from pathlib import Path

from okf.parsers.base import Concept, log, _ts, _safe_id, _first_line

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
                # Emit methods as individual Function concepts
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                        mc = self._parse_function(child, rel, ts, c.concept_id)
                        mc.decorators = self._py_decorators(child)
                        funcs.append(mc)
                        c.related.append(mc.concept_id)

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

    def _py_decorators(self, node) -> list[str]:
        decs = []
        for d in node.decorator_list:
            try:
                decs.append(ast.unparse(d))
            except Exception:
                pass
        return decs

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
            decorators=self._py_decorators(node),
        )

    def _parse_class(self, node, resource, ts, parent_id) -> Concept:
        doc     = ast.get_docstring(node) or ""
        methods = [
            child.name for child in ast.iter_child_nodes(node)
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef)
        ]
        bases = []
        for b in node.bases:
            try:
                bases.append(ast.unparse(b))
            except Exception:
                pass
        # Extract fields (annotated class-level assignments)
        py_fields = []
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                ftype = ""
                try:
                    ftype = ast.unparse(child.annotation)
                except Exception:
                    pass
                py_fields.append({"name": child.target.id, "type": ftype, "visibility": ""})
        resource_id = re.sub(r"\.py$", "", resource).replace(os.sep, "/")
        cid     = f"{resource_id}/{_safe_id(node.name)}"
        return Concept(
            type="Class", title=node.name,
            description=_first_line(doc), docstring=doc,
            resource=resource,
            tags=["python", "class"],
            timestamp=ts, methods=methods,
            inheritance=bases,
            decorators=self._py_decorators(node),
            fields=py_fields,
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
