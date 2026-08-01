"""Scala parser (tree-sitter). Extracts: classes, objects, traits, enums, functions, methods, visibility, params, return types."""
from okf.parsers.base import TreeSitterParser, _find_all, _node_text, _prev_comment


class ScalaParser(TreeSitterParser):
    LANGUAGE   = "scala"
    EXTENSIONS = {".scala", ".sc"}
    _TS_MODULE = "tree_sitter_scala"
    _lang_obj  = None

    def _module_doc(self, root, src_bytes: bytes) -> str:
        return _prev_comment(root, src_bytes)

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []
        decl_types = ("class_definition", "object_definition", "trait_definition",
                      "enum_definition", "function_definition")

        for node in _find_all(root, *decl_types):
            doc = _prev_comment(node, src_bytes)

            if node.type == "class_definition":
                name = _node_text(node.child_by_field_name("name"))
                if not name:
                    continue
                methods = self._scala_methods(node)
                concepts.append(self._make_concept(
                    "Class", name, doc, f"class {name}", resource, ts, parent_id,
                    node.start_point[0]+1, methods=methods,
                    node=node, src_bytes=src_bytes))

            elif node.type == "object_definition":
                name = _node_text(node.child_by_field_name("name"))
                if not name:
                    continue
                methods = self._scala_methods(node)
                concepts.append(self._make_concept(
                    "Class", name, doc, f"object {name}", resource, ts, parent_id,
                    node.start_point[0]+1, methods=methods,
                    node=node, src_bytes=src_bytes))

            elif node.type == "trait_definition":
                name = _node_text(node.child_by_field_name("name"))
                if not name:
                    continue
                methods = self._scala_methods(node)
                concepts.append(self._make_concept(
                    "Interface", name, doc, f"trait {name}", resource, ts, parent_id,
                    node.start_point[0]+1, methods=methods,
                    node=node, src_bytes=src_bytes))

            elif node.type == "enum_definition":
                ename = _node_text(node.child_by_field_name("name"))
                if not ename:
                    continue
                cases = []
                body = node.child_by_field_name("body")
                if body:
                    for case in _find_all(body, "enum_case"):
                        cn = case.child_by_field_name("name")
                        if cn:
                            cases.append(_node_text(cn))
                concepts.append(self._make_concept(
                    "Enum", ename, doc, f"enum {ename}", resource, ts, parent_id,
                    node.start_point[0]+1, methods=cases,
                    node=node, src_bytes=src_bytes))

        # Top-level function_definitions (not inside class/object/trait body)
        for node in _find_all(root, "function_definition"):
            parent = node.parent
            if parent and parent.type != "body":
                continue
            name = _node_text(node.child_by_field_name("name"))
            if not name:
                continue
            doc = _prev_comment(node, src_bytes)
            sig = self._scala_fn_sig(node)
            concepts.append(self._make_concept(
                "Function", name, doc, sig, resource, ts, parent_id,
                node.start_point[0]+1, node=node, src_bytes=src_bytes))

        # Methods inside class/object/trait
        for cls_node in _find_all(root, "class_definition", "object_definition", "trait_definition"):
            body = cls_node.child_by_field_name("body")
            if not body:
                continue
            for m in _find_all(body, "function_definition"):
                mname = _node_text(m.child_by_field_name("name"))
                if not mname:
                    continue
                mdoc = _prev_comment(m, src_bytes) or doc
                sig = self._scala_fn_sig(m)
                vis = self._scala_visibility(m)
                fn = self._make_concept(
                    "Function", mname, mdoc, sig, resource, ts, parent_id,
                    m.start_point[0]+1, node=m, src_bytes=src_bytes)
                if vis:
                    fn.visibility = vis
                concepts.append(fn)

        return concepts

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        imports = []
        for imp in _find_all(root, "import_statement"):
            imports.append(_node_text(imp))
        return imports

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        calls = []
        for fc in _find_all(node, "call_expression", "method_invocation"):
            fn = fc.child_by_field_name("function") or fc.child_by_field_name("name")
            t = _node_text(fn) if fn else ""
            if t:
                calls.append(t)
        return calls

    def _scala_fn_sig(self, node) -> str:
        name = _node_text(node.child_by_field_name("name"))
        params = _node_text(node.child_by_field_name("parameters")) or "()"
        ret = _node_text(node.child_by_field_name("return_type"))
        ret_str = f": {ret}" if ret else ""
        return f"def {name}{params}{ret_str}"

    def _scala_visibility(self, node) -> list[str]:
        for child in node.children:
            if child.type in ("private", "protected"):
                return [child.type]
        return []

    def _scala_methods(self, node) -> list[str]:
        body = node.child_by_field_name("body")
        if not body:
            return []
        methods = []
        for m in _find_all(body, "function_definition"):
            mn = _node_text(m.child_by_field_name("name"))
            if mn:
                methods.append(mn)
        return methods
