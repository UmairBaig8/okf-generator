"""C parser (tree-sitter). Extracts: functions, structs, enums, typedefs, comments, calls."""

from okf.parsers.base import _prev_comment, _find_all, _node_text, TreeSitterParser

class CParser(TreeSitterParser):
    LANGUAGE   = "c"
    EXTENSIONS = {".c", ".h"}
    _TS_MODULE = "tree_sitter_c"
    _lang_obj  = None

    def _module_doc(self, root, src_bytes: bytes) -> str:
        for child in root.children:
            if child.type == "comment":
                return _prev_comment(child.next_sibling or child, src_bytes) or _node_text(child).lstrip("/ *").strip()
        return ""

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []
        seen = set()
        for node in _find_all(root, "function_definition", "struct_specifier"):
            name = None
            if node.type == "function_definition":
                decl = node.child_by_field_name("declarator")
                if decl:
                    name = _node_text(decl.child_by_field_name("declarator") or decl)
            elif node.type == "struct_specifier":
                # Only top-level structs, not params inside functions
                if node.parent and node.parent.type in ("parameter_declaration", "field_declaration"):
                    continue
                name = _node_text(node.child_by_field_name("name"))
            if not name or name in seen:
                continue
            seen.add(name)

            if node.type == "function_definition":
                decl = node.child_by_field_name("declarator")
                if not decl:
                    continue
                name = _node_text(decl.child_by_field_name("declarator") or decl)
                doc  = _prev_comment(node, src_bytes)
                params_node = decl.child_by_field_name("parameters")
                params = _node_text(params_node).strip("()") if params_node else ""
                ret   = _node_text(node.child_by_field_name("type"))
                sig   = f"{ret + ' ' if ret else ''}{name}({params})"
                concepts.append(self._make_concept("Function", name, doc, sig, resource, ts, parent_id, node.start_point[0]+1, node=node, src_bytes=src_bytes))
            elif node.type == "struct_specifier":
                name = _node_text(node.child_by_field_name("name"))
                if not name:
                    continue
                doc = _prev_comment(node, src_bytes)
                concepts.append(self._make_concept("Class", name, doc, f"struct {name}", resource, ts, parent_id, node.start_point[0]+1, node=node, src_bytes=src_bytes))
        return concepts
