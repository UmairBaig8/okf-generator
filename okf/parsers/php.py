"""PHP parser (tree-sitter). Extracts: functions, classes, interfaces, traits, enums, methods, enums cases, visibility, params, return types, docblocks."""
from okf.parsers.base import TreeSitterParser, _find_all, _node_text, _prev_comment


class PHPParser(TreeSitterParser):
    LANGUAGE   = "php"
    EXTENSIONS = {".php", ".phtml"}
    _TS_MODULE = "tree_sitter_php"
    _lang_obj  = None

    def _lang(self):
        if self.__class__._lang_obj is None:
            import importlib
            mod = importlib.import_module(self._TS_MODULE)
            from tree_sitter import Language
            self.__class__._lang_obj = Language(mod.language_php())
        return self.__class__._lang_obj

    def _module_doc(self, root, src_bytes: bytes) -> str:
        return _prev_comment(root, src_bytes)

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []
        decl_types = ("class_declaration", "interface_declaration", "trait_declaration",
                      "enum_declaration", "function_definition")

        for node in _find_all(root, *decl_types):
            doc = _prev_comment(node, src_bytes)

            if node.type == "function_definition":
                name = _node_text(node.child_by_field_name("name"))
                if not name:
                    continue
                sig = self._php_func_sig(node)
                concepts.append(self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes))

            elif node.type in ("class_declaration", "interface_declaration", "trait_declaration"):
                name = _node_text(node.child_by_field_name("name"))
                if not name:
                    continue
                ctype = {"interface_declaration": "Interface",
                         "trait_declaration": "Class",
                         "class_declaration": "Class"}[node.type]
                if node.type == "interface_declaration":
                    ctype = "Interface"
                inherits = self._php_inheritance(node)
                methods = []
                body = node.child_by_field_name("body") or node.child_by_field_name("declaration_list")
                if body:
                    for child in body.named_children:
                        if child.type == "method_declaration":
                            mn = _node_text(child.child_by_field_name("name"))
                            if mn:
                                methods.append(mn)
                concepts.append(self._make_concept(
                    ctype, name, doc,
                    f"{node.type.split('_')[0]} {name}" + (f" extends {inherits[0]}" if inherits else ""),
                    resource, ts, parent_id,
                    node.start_point[0]+1, methods=methods,
                    node=node, src_bytes=src_bytes))

            elif node.type == "enum_declaration":
                name = _node_text(node.child_by_field_name("name"))
                if not name:
                    continue
                cases = []
                for case_node in _find_all(node, "enum_case"):
                    cn = _node_text(case_node.child_by_field_name("name"))
                    if cn:
                        cases.append(cn)
                concepts.append(self._make_concept(
                    "Enum", name, doc,
                    f"enum {name}", resource, ts, parent_id,
                    node.start_point[0]+1, methods=cases,
                    node=node, src_bytes=src_bytes))

        # Emit class methods as individual Function concepts
        for cls_node in _find_all(root, "class_declaration", "interface_declaration",
                                   "trait_declaration"):
            body = cls_node.child_by_field_name("body") or cls_node.child_by_field_name("declaration_list")
            if not body:
                continue
            for child in body.named_children:
                if child.type != "method_declaration":
                    continue
                mname = _node_text(child.child_by_field_name("name"))
                if not mname:
                    continue
                mdoc = _prev_comment(child, src_bytes) or doc
                vis = self._php_visibility(child)
                sig = self._php_func_sig(child)
                fn_concept = self._make_concept(
                    "Function", mname, mdoc, sig, resource, ts, parent_id,
                    child.start_point[0]+1, node=child, src_bytes=src_bytes)
                if vis:
                    fn_concept.visibility = vis
                concepts.append(fn_concept)

        return concepts

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        imports = []
        for use in _find_all(root, "namespace_use_declaration"):
            clause = use.child_by_field_name("clause") or use
            for c in _find_all(clause, "namespace_name", "name"):
                t = _node_text(c)
                if t:
                    imports.append(t)
        return imports

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        calls = []
        for fn in _find_all(node, "function_call_expression"):
            n = fn.child_by_field_name("function") or fn.child_by_field_name("name")
            t = _node_text(n)
            if t:
                calls.append(t)
        return calls

    def _php_func_sig(self, node) -> str:
        name = _node_text(node.child_by_field_name("name"))
        params = node.child_by_field_name("parameters")
        params_text = _node_text(params) if params else "()"
        ret = node.child_by_field_name("return_type")
        ret_text = _node_text(ret) if ret else ""
        if ret_text.startswith(": "):
            ret_text = ret_text[2:]
        elif ret_text.startswith(":"):
            ret_text = ret_text[1:]
        return f"function {name}{params_text}" + (f": {ret_text}" if ret_text else "")

    def _php_visibility(self, node) -> list[str]:
        vis = []
        for child in node.children:
            if child.type == "visibility_modifier":
                t = _node_text(child).lower()
                if t in ("public", "private", "protected"):
                    vis.append(t)
        return vis

    def _php_inheritance(self, node) -> list[str]:
        parents = []
        for child in node.children:
            if child.type in ("base_clause", "extends_clause", "implements_clause"):
                for n in _find_all(child, "name", "named_type"):
                    t = _node_text(n)
                    if t:
                        parents.append(t)
        return parents
