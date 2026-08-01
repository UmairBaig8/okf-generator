"""Julia parser (tree-sitter). Extracts: functions, structs, abstract types, constants."""
from okf.parsers.base import TreeSitterParser, _find_all, _node_text, _prev_comment


class JuliaParser(TreeSitterParser):
    LANGUAGE   = "julia"
    EXTENSIONS = {".jl"}
    _TS_MODULE = "tree_sitter_julia"
    _lang_obj  = None

    def _module_doc(self, root, src_bytes: bytes) -> str:
        return _prev_comment(root, src_bytes)

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []

        for node in _find_all(root, "function_definition", "struct_definition",
                               "abstract_definition", "const_statement",
                               "macro_definition"):
            doc = _prev_comment(node, src_bytes)

            if node.type == "function_definition":
                sig_node = node.named_child(0) if node.named_child_count > 0 else None
                name = self._julia_fn_name(sig_node)
                if not name:
                    continue
                sig = self._julia_fn_sig(sig_node)
                concepts.append(self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes))

            elif node.type == "struct_definition":
                th = node.named_child(0) if node.named_child_count > 0 else None
                name = self._julia_type_name(th)
                if not name:
                    continue
                fields = []
                for i in range(1, node.named_child_count):
                    f = node.named_child(i)
                    if f.type == "typed_expression":
                        fields.append(_node_text(f))
                concepts.append(self._make_concept(
                    "Class", name, doc, f"struct {name}", resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes))

            elif node.type == "abstract_definition":
                th = node.named_child(0) if node.named_child_count > 0 else None
                name = self._julia_type_name(th)
                if not name:
                    continue
                concepts.append(self._make_concept(
                    "Interface", name, doc, f"abstract type {name}",
                    resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes))

            elif node.type == "const_statement":
                assign = node.named_child(0) if node.named_child_count > 0 else None
                name = ""
                if assign:
                    for i in range(assign.named_child_count):
                        if assign.named_child(i).type == "identifier":
                            name = _node_text(assign.named_child(i))
                            break
                if not name:
                    continue
                sig = _node_text(assign)
                concepts.append(self._make_concept(
                    "Constant", name, doc, f"const {sig}",
                    resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes))

            elif node.type == "macro_definition":
                name = _node_text(node.child_by_field_name("name"))
                if not name:
                    continue
                concepts.append(self._make_concept(
                    "Function", name, doc, f"macro {name}(...)",
                    resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes))

        return concepts

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        imports = []
        for imp in _find_all(root, "import_statement", "using_statement"):
            imports.append(_node_text(imp))
        return imports

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        calls = []
        for fc in _find_all(node, "call_expression"):
            fn = fc.child_by_field_name("function")
            t = _node_text(fn) if fn else ""
            if t and t != "function":
                calls.append(t)
        return calls

    def _julia_fn_name(self, sig_node) -> str:
        if sig_node is None:
            return ""
        text = _node_text(sig_node)
        # First word before ( or :: is the function name
        for sep in ("(", "::"):
            idx = text.find(sep)
            if idx > 0:
                return text[:idx].strip()
        return text.split()[0] if text else ""

    def _julia_fn_sig(self, sig_node) -> str:
        if sig_node is None:
            return ""
        return _node_text(sig_node)

    def _julia_type_name(self, type_head) -> str:
        if type_head is None:
            return ""
        for i in range(type_head.named_child_count):
            nc = type_head.named_child(i)
            if nc.type == "identifier":
                return _node_text(nc)
        return _node_text(type_head)
