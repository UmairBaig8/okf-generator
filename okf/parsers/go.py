"""Go parser (tree-sitter). Extracts: functions, methods, structs, interfaces, const/var declarations, generics (1.18+), GoDoc, imports, calls."""

from okf.parsers.base import _prev_comment, _find_all, _node_text, TreeSitterParser

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

        for node in _find_all(root, "function_declaration", "method_declaration", "type_declaration",
                               "const_declaration", "var_declaration"):

            doc = _prev_comment(node, src_bytes)

            if node.type == "function_declaration":
                name = _node_text(node.child_by_field_name("name"))
                if not name:
                    continue
                params = self._go_params(node)
                ret    = self._go_return(node)
                tp     = self._go_type_params(node)
                sig    = f"func {name}({params})" + (f" {ret}" if ret else "")
                concepts.append(self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes,
                    type_params=tp))

            elif node.type == "method_declaration":
                name = _node_text(node.child_by_field_name("name"))
                recv = node.child_by_field_name("receiver")
                recv_text = _node_text(recv) if recv else ""
                if not name:
                    continue
                params = self._go_params(node)
                ret    = self._go_return(node)
                tp     = self._go_type_params(node)
                sig    = f"func {recv_text} {name}({params})" + (f" {ret}" if ret else "")
                concepts.append(self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes,
                    type_params=tp))

            elif node.type == "type_declaration":
                # type Foo struct { ... } or type Foo interface { ... }
                for spec in _find_all(node, "type_spec"):
                    name_node = spec.child_by_field_name("name")
                    type_node = spec.child_by_field_name("type")
                    if not name_node:
                        continue
                    name    = _node_text(name_node)
                    is_iface = type_node and type_node.type == "interface_type"
                    ctype   = "Interface" if is_iface else "Class"
                    tp      = self._go_type_params(spec)
                    sig     = f"type {name} struct" if not is_iface else f"type {name} interface"
                    methods = [
                        _node_text(f.child_by_field_name("name") or f)
                        for f in _find_all(type_node or spec, "field_declaration", "method_spec")
                        if _node_text(f.child_by_field_name("name") or f)
                    ] if type_node else []
                    concepts.append(self._make_concept(
                        ctype, name, doc, sig, resource, ts, parent_id,
                        node.start_point[0]+1, methods=methods, node=node, src_bytes=src_bytes,
                        type_params=tp))

            elif node.type == "const_declaration":
                for spec in node.children:
                    if spec.type != "const_spec":
                        continue
                    n = spec.child_by_field_name("name")
                    if not n:
                        continue
                    cname = _node_text(n)
                    cdoc = _prev_comment(spec, src_bytes) or doc
                    t = spec.child_by_field_name("type")
                    tstr = _node_text(t) if t else ""
                    v = spec.child_by_field_name("value")
                    vstr = _node_text(v) if v else ""
                    sig = f"const {cname}" + (f" {tstr}" if tstr else "") + (f" = {vstr}" if vstr else "")
                    concepts.append(self._make_concept(
                        "Constant", cname, cdoc, sig, resource, ts, parent_id,
                        spec.start_point[0]+1, node=spec, src_bytes=src_bytes))

            elif node.type == "var_declaration":
                for spec in node.children:
                    if spec.type != "var_spec":
                        continue
                    n = spec.child_by_field_name("name")
                    if not n:
                        continue
                    vname = _node_text(n)
                    vdoc = _prev_comment(spec, src_bytes) or doc
                    t = spec.child_by_field_name("type")
                    tstr = _node_text(t) if t else ""
                    v = spec.child_by_field_name("value")
                    vstr = _node_text(v) if v else ""
                    sig = f"var {vname}" + (f" {tstr}" if tstr else "") + (f" = {vstr}" if vstr else "")
                    concepts.append(self._make_concept(
                        "Variable", vname, vdoc, sig, resource, ts, parent_id,
                        spec.start_point[0]+1, node=spec, src_bytes=src_bytes))

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

    def _go_type_params(self, node):
        tp = node.child_by_field_name("type_parameters")
        if not tp:
            return []
        text = _node_text(tp)
        inner = text.strip("[]").strip()
        if not inner:
            return []
        parts, depth, buf = [], 0, []
        for ch in inner:
            if ch == "," and depth == 0:
                parts.append("".join(buf).strip())
                buf = []
            else:
                if ch in "[]":
                    depth += 1 if ch == "[" else -1
                buf.append(ch)
        if buf:
            parts.append("".join(buf).strip())
        return [p for p in parts if p]
