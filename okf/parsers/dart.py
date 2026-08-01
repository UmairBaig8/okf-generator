"""Dart parser (tree-sitter). Extracts: classes, mixins, enums, functions, methods, constructors."""
from okf.parsers.base import TreeSitterParser, _find_all, _node_text, _prev_comment


class DartParser(TreeSitterParser):
    LANGUAGE   = "dart"
    EXTENSIONS = {".dart"}
    _TS_MODULE = "tree_sitter_dart"
    _lang_obj  = None

    def _module_doc(self, root, src_bytes: bytes) -> str:
        return _prev_comment(root, src_bytes)

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []

        for node in _find_all(root, "class_definition", "mixin_declaration",
                               "enum_declaration", "function_signature"):
            doc = _prev_comment(node, src_bytes)

            if node.type == "class_definition":
                name = _node_text(node.child_by_field_name("name"))
                if not name:
                    continue
                methods = self._dart_methods(node, src_bytes)
                concepts.append(self._make_concept(
                    "Class", name, doc,
                    f"class {name}", resource, ts, parent_id,
                    node.start_point[0]+1, methods=methods,
                    node=node, src_bytes=src_bytes))

            elif node.type == "mixin_declaration":
                name = _node_text(node.named_child(1)) if node.named_child_count > 1 else ""
                if not name:
                    continue
                methods = self._dart_methods(node, src_bytes)
                concepts.append(self._make_concept(
                    "Class", name, doc,
                    f"mixin {name}", resource, ts, parent_id,
                    node.start_point[0]+1, methods=methods,
                    node=node, src_bytes=src_bytes))

            elif node.type == "enum_declaration":
                ename = _node_text(node.child_by_field_name("name"))
                if not ename:
                    continue
                cases = []
                body = node.child_by_field_name("body")
                if body:
                    for ec in _find_all(body, "enum_constant", "identifier"):
                        cases.append(_node_text(ec))
                concepts.append(self._make_concept(
                    "Enum", ename, doc,
                    f"enum {ename}", resource, ts, parent_id,
                    node.start_point[0]+1, methods=cases,
                    node=node, src_bytes=src_bytes))

        # Top-level functions (function_signature not inside a class body)
        for node in _find_all(root, "function_signature"):
            doc = _prev_comment(node, src_bytes)
            # Skip if inside a class/mixin body
            parent = node.parent
            if parent and parent.type in ("method_signature",):
                continue
            name = _node_text(node.child_by_field_name("name"))
            if not name:
                continue
            sig = self._dart_fn_sig(node)
            concepts.append(self._make_concept(
                "Function", name, doc, sig, resource, ts, parent_id,
                node.start_point[0]+1, node=node, src_bytes=src_bytes))

        # Methods inside classes
        for cls_node in _find_all(root, "class_definition", "mixin_declaration"):
            body = cls_node.child_by_field_name("body")
            if not body:
                continue
            for fn_sig in _find_all(body, "function_signature"):
                mname = _node_text(fn_sig.child_by_field_name("name"))
                if not mname:
                    continue
                mdoc = _prev_comment(fn_sig, src_bytes) or doc
                sig = self._dart_fn_sig(fn_sig)
                concepts.append(self._make_concept(
                    "Function", mname, mdoc, sig, resource, ts, parent_id,
                    fn_sig.start_point[0]+1, node=fn_sig, src_bytes=src_bytes))
            for cs in _find_all(body, "constructor_signature"):
                cs_name = _node_text(cs.child_by_field_name("name"))
                cs_params = _node_text(cs.child_by_field_name("parameters"))
                if cs_name:
                    sig = f"{cs_name}({cs_params.strip('()')})"
                    concepts.append(self._make_concept(
                        "Function", cs_name, "", sig, resource, ts, parent_id,
                        cs.start_point[0]+1, node=cs, src_bytes=src_bytes))

        return concepts

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        imports = []
        for imp in _find_all(root, "import_declaration", "export_declaration"):
            uri = imp.child_by_field_name("uri")
            if uri:
                imports.append(_node_text(uri))
        return imports

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        calls = []
        for fc in _find_all(node, "function_expression"):
            name = _node_text(fc.child_by_field_name("name"))
            if name:
                calls.append(name)
        return calls

    def _dart_fn_sig(self, fn_sig) -> str:
        name = _node_text(fn_sig.child_by_field_name("name"))
        params = _node_text(
            fn_sig.child_by_field_name("parameters") or
            fn_sig.named_child(2) if fn_sig.named_child_count > 2 else None
        ) or "()"
        ret = _node_text(
            fn_sig.child_by_field_name("return_type") or
            fn_sig.named_child(0) if fn_sig.named_child_count > 0 else None
        ) or ""
        ret_str = f" {ret}" if ret else ""
        return f"{ret_str}{name}{params}".strip()

    def _dart_methods(self, node, src_bytes) -> list[str]:
        body = node.child_by_field_name("body")
        if not body:
            return []
        methods = []
        for fn_sig in _find_all(body, "function_signature"):
            mn = _node_text(fn_sig.child_by_field_name("name"))
            if mn:
                methods.append(mn)
        for cs in _find_all(body, "constructor_signature"):
            cn = _node_text(cs.child_by_field_name("name"))
            if cn:
                methods.append(cn)
        return methods
