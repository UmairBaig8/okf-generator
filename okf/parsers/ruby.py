"""Ruby parser (tree-sitter). Extracts: methods (def), classes, modules, YARD/doc comments, visibility, calls, inheritance."""

from okf.parsers.base import _prev_comment, _find_all, _node_text, _parse_doc_tags, TreeSitterParser

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

        for node in _find_all(root, "method", "singleton_method", "class", "module"):
            name_node = node.child_by_field_name("name")
            if not name_node:
                continue
            name = _node_text(name_node)
            doc  = _prev_comment(node, src_bytes)

            if node.type == "method":
                params = self._ruby_params(node)
                sig    = f"def {name}({params})"
                mc = self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes)
                parsed_params, parsed_returns = _parse_doc_tags(doc, "ruby")
                if parsed_params:
                    mc.params = parsed_params
                if parsed_returns:
                    mc.returns = parsed_returns
                concepts.append(mc)

            elif node.type == "singleton_method":
                params = self._ruby_params(node)
                sig    = f"def self.{name}({params})"
                mc = self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes)
                mc.visibility = ["singleton"]
                parsed_params, parsed_returns = _parse_doc_tags(doc, "ruby")
                if parsed_params:
                    mc.params = parsed_params
                if parsed_returns:
                    mc.returns = parsed_returns
                concepts.append(mc)

            elif node.type in {"class", "module"}:
                methods = [
                    _node_text(m.child_by_field_name("name"))
                    for m in _find_all(node, "method", "singleton_method")
                    if m.child_by_field_name("name")
                ]
                sig = f"class {name}" if node.type == "class" else f"module {name}"
                bases = []
                if node.type == "class":
                    sc = node.child_by_field_name("superclass")
                    if sc:
                        for ch in sc.children:
                            if ch.type == "constant":
                                bases.append(_node_text(ch))
                cc = self._make_concept(
                    "Class", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, methods=methods, node=node, src_bytes=src_bytes)
                cc.inheritance = bases
                concepts.append(cc)

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
