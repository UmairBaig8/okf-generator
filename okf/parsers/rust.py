"""Rust parser (tree-sitter). Extracts: functions, methods, structs, enums, traits, impl blocks, generics, attributes (#[derive]), visibility, doc comments (/// //!), imports, calls."""

from okf.parsers.base import _prev_comment, _find_all, _node_text, TreeSitterParser

def _rust_vis_node(node):
    """Find visibility_modifier child by iterating children (no field name)."""
    for child in node.children:
        if child.type == "visibility_modifier":
            return child
    return None
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
                vis    = _node_text(_rust_vis_node(node))
                tp     = self._rust_type_params(node)
                sig    = f"{vis+' ' if vis else ''}fn {name}({params})" + (f" -> {ret}" if ret else "")
                fc = self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, node=node, src_bytes=src_bytes,
                    type_params=tp)
                fc.decorators = self._rust_attributes(node)
                if vis:
                    fc.visibility = [vis]
                concepts.append(fc)

            elif node.type in {"struct_item", "enum_item", "trait_item"}:
                name_node = node.child_by_field_name("name")
                if not name_node:
                    continue
                name  = _node_text(name_node)
                doc   = _prev_comment(node, src_bytes)
                kind  = {"struct_item": "struct", "enum_item": "enum", "trait_item": "trait"}[node.type]
                vis   = _node_text(_rust_vis_node(node))
                tp    = self._rust_type_params(node)
                sig   = f"{vis+' ' if vis else ''}{kind} {name}"
                fields = [
                    _node_text(f.child_by_field_name("name"))
                    for f in _find_all(node, "field_declaration")
                    if f.child_by_field_name("name")
                ]
                cc = self._make_concept(
                    "Class", name, doc, sig, resource, ts, parent_id,
                    node.start_point[0]+1, methods=fields, node=node, src_bytes=src_bytes,
                    type_params=tp)
                cc.decorators = self._rust_attributes(node)
                if vis:
                    cc.visibility = [vis]
                concepts.append(cc)

            elif node.type == "impl_item":
                type_node = node.child_by_field_name("type")
                type_name = _node_text(type_node) if type_node else ""
                impl_tp = self._rust_type_params(node)
                for fn in _find_all(node, "function_item"):
                    fn_name = _node_text(fn.child_by_field_name("name"))
                    if not fn_name:
                        continue
                    doc    = _prev_comment(fn, src_bytes)
                    params = self._rust_params(fn)
                    ret    = self._rust_return(fn)
                    vis    = _node_text(_rust_vis_node(fn))
                    tp     = self._rust_type_params(fn) or impl_tp
                    sig    = f"impl {type_name} {{ {vis+' ' if vis else ''}fn {fn_name}({params})" + \
                             (f" -> {ret}" if ret else "") + " }"
                    fc = self._make_concept(
                        "Function", fn_name, doc, sig, resource, ts, parent_id,
                        fn.start_point[0]+1, node=fn, src_bytes=src_bytes,
                        type_params=tp)
                    if vis:
                        fc.visibility = [vis]
                    concepts.append(fc)

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

    def _rust_attributes(self, node):
        """Collect preceding #[attribute] items for a Rust node."""
        decs = []
        sib = node.prev_named_sibling if hasattr(node, 'prev_named_sibling') else None
        while sib is not None:
            if sib.type == "attribute_item":
                attr_node = next((c for c in sib.children if c.type == "attribute"), None)
                if attr_node:
                    decs.insert(0, _node_text(attr_node))
            elif sib.type not in ("attribute_item", "comment", ""):
                break
            sib = sib.prev_named_sibling if hasattr(sib, 'prev_named_sibling') else None
        return decs

    def _rust_type_params(self, node):
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
