"""C++ parser (tree-sitter). Extracts: functions, classes, methods, templates/generics, inheritance, visibility, calls."""
import os

from okf.parsers.base import _prev_comment, _find_all, _node_text, _safe_id, TreeSitterParser

class CppParser(TreeSitterParser):
    LANGUAGE   = "cpp"
    EXTENSIONS = {".cpp", ".cxx", ".cc", ".hpp", ".hh"}
    _TS_MODULE = "tree_sitter_cpp"
    _lang_obj  = None

    def _module_doc(self, root, src_bytes: bytes) -> str:
        for child in root.children:
            if child.type == "comment":
                return _prev_comment(child.next_sibling or child, src_bytes) or _node_text(child).lstrip("/ *").strip()
        return ""

    def _cpp_template_prefix(self, node) -> str:
        """Return 'template<...>' prefix if node is inside a template_declaration."""
        parent = node.parent
        while parent is not None:
            if parent.type == "template_declaration":
                tpl = parent.child_by_field_name("parameters")
                if tpl:
                    return f"template<{_node_text(tpl)}> "
                return "template<> "
            parent = parent.parent
        return ""

    def _cpp_template_params(self, node):
        """Extract template params from node or its template_declaration parent."""
        # C++ wraps templated declarations in template_declaration nodes
        parent = node.parent
        while parent is not None:
            if parent.type == "template_declaration":
                tpl = parent.child_by_field_name("parameters")
                if tpl:
                    text = _node_text(tpl)
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
            parent = parent.parent
        return []

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []
        seen = set()
        for node in _find_all(root, "function_definition", "class_specifier", "struct_specifier"):
            name = None
            if node.type == "function_definition":
                decl = node.child_by_field_name("declarator") or node.child_by_field_name("function_declarator")
                if decl:
                    name = _node_text(decl.child_by_field_name("declarator") or decl.child_by_field_name("field_identifier") or decl)
            elif node.type in ("class_specifier", "struct_specifier"):
                if node.parent and node.parent.type in ("template_declaration",):
                    name = _node_text(node.child_by_field_name("name"))
                elif not node.parent or node.parent.type not in ("function_definition", "parameter_declaration", "field_declaration"):
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
                tp    = self._cpp_template_params(node)
                tpl_prefix = self._cpp_template_prefix(node)
                sig   = f"{tpl_prefix}{ret + ' ' if ret else ''}{name}({params})"
                # Extract modifiers (static, virtual, const, override, etc.)
                cpp_vis = []
                for child in node.children:
                    if child.type in ("storage_class_specifier", "virtual", "override", "const"):
                        cpp_vis.append(_node_text(child))
                # Determine parent: if inside a class, link to class instead of module
                f_parent_id = parent_id
                pn = node.parent
                while pn is not None:
                    if pn.type in ("class_specifier", "struct_specifier"):
                        pname = _node_text(pn.child_by_field_name("name"))
                        if pname:
                            res_id = resource.replace(os.sep, "/")
                            f_parent_id = f"{res_id}/{_safe_id(pname)}"
                        break
                    pn = pn.parent
                cpp_fc = self._make_concept("Function", name, doc, sig, resource, ts, f_parent_id, node.start_point[0]+1, node=node, src_bytes=src_bytes, type_params=tp)
                cpp_fc.visibility = cpp_vis
                concepts.append(cpp_fc)
            elif node.type in ("class_specifier", "struct_specifier"):
                name = _node_text(node.child_by_field_name("name"))
                if not name:
                    continue
                doc = _prev_comment(node, src_bytes)
                ctype = "Class"
                tp = self._cpp_template_params(node)
                # Extract base classes from base_class_clause
                bases = []
                for child in node.children:
                    if child.type == "base_class_clause":
                        for sub in child.children:
                            if sub.type in ("type_identifier", "template_type"):
                                bases.append(_node_text(sub))
                methods = [
                    _node_text(m.child_by_field_name("declarator") or m.child_by_field_name("function_declarator")).split("(")[0].strip()
                    for m in _find_all(node, "function_definition")
                    if m.child_by_field_name("declarator") or m.child_by_field_name("function_declarator")
                ]
                tpl_prefix = self._cpp_template_prefix(node)
                cc = self._make_concept(ctype, name, doc, f"{tpl_prefix}{node.type.replace('_specifier','')} {name}", resource, ts, parent_id, node.start_point[0]+1, methods=methods, node=node, src_bytes=src_bytes, type_params=tp)
                cc.inheritance = bases
                concepts.append(cc)
        return concepts
