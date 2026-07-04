"""JavaScript/TypeScript parser (tree-sitter). Extracts: functions, arrow fns, methods, classes, interfaces, type aliases, enums, JSDoc, generics, visibility, class fields, decorators, imports, calls."""
import os

from pathlib import Path

from okf.parsers.base import Concept, _prev_comment, _find_all, _node_text, _parse_doc_tags, _safe_id, TreeSitterParser

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
                               "interface_declaration",
                               "type_alias_declaration",
                               "enum_declaration",
                               "export_statement"):
            if node.type in {"function_declaration"}:
                name_node = node.child_by_field_name("name")
                if not name_node:
                    continue
                name   = _node_text(name_node)
                doc    = _prev_comment(node, src_bytes)
                params = self._js_params(node)
                ret    = self._js_return_type(node)
                tp     = self._js_type_params(node)
                sig    = f"function {name}({params})" + (f": {ret}" if ret else "")
                fc = self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes,
                    type_params=tp)
                parsed_params, parsed_returns = _parse_doc_tags(doc, self.LANGUAGE)
                if parsed_params:
                    fc.params = parsed_params
                if parsed_returns:
                    fc.returns = parsed_returns
                concepts.append(fc)

            elif node.type == "class_declaration":
                name_node = node.child_by_field_name("name")
                if not name_node:
                    continue
                name    = _node_text(name_node)
                doc     = _prev_comment(node, src_bytes)
                tp      = self._js_type_params(node)
                methods = [
                    _node_text(m.child_by_field_name("name"))
                    for m in _find_all(node, "method_definition")
                    if m.child_by_field_name("name")
                ]
                # Extract class fields
                ts_fields = []
                for body_child in node.children:
                    if body_child.type == "class_body":
                        for member in body_child.children:
                            if member.type == "public_field_definition":
                                fname_node = member.child_by_field_name("name")
                                ftype_node = member.child_by_field_name("type")
                                fname = _node_text(fname_node) if fname_node else ""
                                ftype_text = _node_text(ftype_node).lstrip(":").strip() if ftype_node else ""
                                fvis = ""
                                for mc in member.children:
                                    if mc.type in ("accessibility_modifier", "static", "readonly"):
                                        fvis += _node_text(mc) + " "
                                ts_fields.append({"name": fname, "type": ftype_text, "visibility": fvis.strip()})
                sig = f"class {name}"
                # Extract heritage (extends / implements)
                bases = []
                for child in node.children:
                    if child.type == "class_heritage":
                        for sub in child.children:
                            if sub.type in ("extends_clause", "implements_clause"):
                                for item in sub.children:
                                    if item.type in ("identifier", "type_identifier", "nested_type_identifier"):
                                        bases.append(_node_text(item))
                cc = self._make_concept(
                    "Class", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, methods=methods, node=node, src_bytes=src_bytes,
                    type_params=tp)
                cc.inheritance = bases
                cc.fields = ts_fields
                concepts.append(cc)

            elif node.type == "method_definition":
                # Emit class methods as individual Function concepts
                mname_node = node.child_by_field_name("name")
                if not mname_node:
                    continue
                mname  = _node_text(mname_node)
                mdoc   = _prev_comment(node, src_bytes)
                mparams = self._js_params(node)
                mret   = self._js_return_type(node)
                mtp    = self._js_type_params(node)
                msig   = f"{mname}({mparams})" + (f": {mret}" if mret else "")
                # Extract visibility/access modifiers
                mvis = []
                for child in node.children:
                    if child.type in ("accessibility_modifier", "static", "abstract", "readonly", "override"):
                        mvis.append(_node_text(child))
                # Link to the nearest enclosing class as parent
                mparent_id = parent_id
                p = node.parent
                while p is not None:
                    if p.type == "class_declaration":
                        pname = _node_text(p.child_by_field_name("name"))
                        mparent_id = f"{resource.replace(os.sep, '/')}/{_safe_id(pname)}" if pname else parent_id
                        break
                    p = p.parent
                mc = self._make_concept(
                    "Function", mname, mdoc, msig, resource, ts, mparent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes, type_params=mtp)
                mc.visibility = mvis
                parsed_params, parsed_returns = _parse_doc_tags(mdoc, self.LANGUAGE)
                if parsed_params:
                    mc.params = parsed_params
                if parsed_returns:
                    mc.returns = parsed_returns
                concepts.append(mc)

            elif node.type == "interface_declaration":
                iname_node = node.child_by_field_name("name")
                if not iname_node:
                    continue
                iname = _node_text(iname_node)
                idoc  = _prev_comment(node, src_bytes)
                # Extract heritage (extends)
                ibases = []
                for child in node.children:
                    if child.type in ("class_heritage", "extends_type_clause"):
                        if child.type == "extends_type_clause":
                            for item in child.children:
                                if item.type in ("identifier", "type_identifier", "nested_type_identifier"):
                                    ibases.append(_node_text(item))
                        else:
                            for sub in child.children:
                                if sub.type == "extends_clause":
                                    for item in sub.children:
                                        if item.type in ("identifier", "type_identifier", "nested_type_identifier"):
                                            ibases.append(_node_text(item))
                # Collect interface members
                imethods = []
                for body_child in node.children:
                    if body_child.type == "interface_body":
                        for member in body_child.children:
                            if member.type in ("method_signature", "property_signature"):
                                msig_name = member.child_by_field_name("name")
                                if msig_name:
                                    imethods.append(_node_text(msig_name))
                ic = self._make_concept(
                    "Interface", iname, idoc, f"interface {iname}", resource, ts, parent_id,
                    node.start_point[0]+1, methods=imethods, node=node, src_bytes=src_bytes)
                ic.inheritance = ibases
                concepts.append(ic)

            elif node.type == "type_alias_declaration":
                taname_node = node.child_by_field_name("name")
                taname = _node_text(taname_node) if taname_node else ""
                if taname:
                    tadoc = _prev_comment(node, src_bytes)
                    concepts.append(self._make_concept(
                        "Type", taname, tadoc, f"type {taname} = …", resource, ts, parent_id,
                        node.start_point[0]+1, node=node, src_bytes=src_bytes))

            elif node.type == "enum_declaration":
                ename_node = node.child_by_field_name("name")
                ename = _node_text(ename_node) if ename_node else ""
                if ename:
                    edoc = _prev_comment(node, src_bytes)
                    emembers = []
                    for child in node.children:
                        if child.type == "enum_body":
                            for member in child.children:
                                if member.type == "property_identifier":
                                    emembers.append(_node_text(member))
                    concepts.append(self._make_concept(
                        "Class", ename, edoc, f"enum {ename}", resource, ts, parent_id,
                        node.start_point[0]+1, methods=emembers, node=node, src_bytes=src_bytes))

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

    def _js_type_params(self, node):
        tp = node.child_by_field_name("type_parameters")
        if not tp:
            return []
        text = _node_text(tp)
        inner = text.strip("<>").strip()
        if not inner:
            return []
        parts, depth, buf = [], 0, []
        for ch in inner:
            if ch == "," and depth == 0:
                parts.append("".join(buf).strip())
                buf = []
            else:
                if ch in "<>":
                    depth += 1 if ch == "<" else -1
                buf.append(ch)
        if buf:
            parts.append("".join(buf).strip())
        return [p for p in parts if p]
