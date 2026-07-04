"""C# parser (tree-sitter). Extracts: classes, interfaces, structs, enums, methods, generics, inheritance, attributes, visibility, fields, imports, calls."""

from okf.parsers.base import _find_all, _node_text, TreeSitterParser

class CSharpParser(TreeSitterParser):
    LANGUAGE   = "csharp"
    EXTENSIONS = {".cs"}
    _TS_MODULE = "tree_sitter_c_sharp"
    _lang_obj  = None

    def _module_doc(self, root, src_bytes: bytes) -> str:
        return ""

    def _cs_type_params(self, node):
        tp = None
        for child in node.children:
            if child.type == "type_parameter_list":
                tp = child
                break
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

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []
        for node in _find_all(root, "class_declaration", "struct_declaration", "interface_declaration", "method_declaration", "local_function_statement"):
            if node.type == "class_declaration":
                name = _node_text(node.child_by_field_name("name"))
                if not name:
                    continue
                tp = self._cs_type_params(node)
                methods = [
                    _node_text(m.child_by_field_name("name"))
                    for m in _find_all(node, "method_declaration")
                    if m.child_by_field_name("name")
                ]
                # Extract base_list
                bases = []
                for child in node.children:
                    if child.type == "base_list":
                        for sub in child.children:
                            if sub.type in ("identifier", "generic_name", "qualified_name", "name"):
                                bases.append(_node_text(sub))
                # Extract attributes
                decs = []
                vis = []
                for child in node.children:
                    if child.type == "attribute_list":
                        for attr in child.children:
                            if attr.type == "attribute":
                                decs.append(_node_text(attr))
                    elif child.type == "modifier":
                        vis.append(_node_text(child))
                # Extract fields
                cs_fields = []
                for child in node.children:
                    if child.type == "declaration_list":
                        for member in child.children:
                            if member.type == "field_declaration":
                                fvis = " ".join(_node_text(c) for c in member.children if c.type == "modifier")
                                vd = next((c for c in member.children if c.type == "variable_declaration"), None)
                                if vd:
                                    ftype = _node_text(vd.child_by_field_name("type"))
                                    decl = next((c for c in vd.children if c.type == "variable_declarator"), None)
                                    fname = _node_text(decl.child_by_field_name("name")) if decl else ""
                                    cs_fields.append({"name": fname, "type": ftype, "visibility": fvis})
                            elif member.type == "property_declaration":
                                pname = _node_text(member.child_by_field_name("name"))
                                ptype = _node_text(member.child_by_field_name("type"))
                                pvis = " ".join(_node_text(c) for c in member.children if c.type == "modifier")
                                cs_fields.append({"name": pname, "type": ptype, "visibility": pvis})
                cc = self._make_concept("Class", name, "", f"class {name}", resource, ts, parent_id, node.start_point[0]+1, methods=methods, node=node, src_bytes=src_bytes, type_params=tp)
                cc.inheritance = bases
                cc.decorators = decs
                cc.visibility = vis
                cc.fields = cs_fields
                concepts.append(cc)
            elif node.type == "interface_declaration":
                iname = _node_text(node.child_by_field_name("name"))
                if not iname:
                    continue
                # Extract base_list
                ibases = []
                for child in node.children:
                    if child.type == "base_list":
                        for sub in child.children:
                            if sub.type in ("identifier", "generic_name", "qualified_name", "name"):
                                ibases.append(_node_text(sub))
                # Extract methods
                imethods = []
                for child in node.children:
                    if child.type == "declaration_list":
                        for m in child.children:
                            if m.type == "method_declaration":
                                mn = m.child_by_field_name("name")
                                if mn:
                                    imethods.append(_node_text(mn))
                ic = self._make_concept("Interface", iname, "", f"interface {iname}", resource, ts, parent_id, node.start_point[0]+1, methods=imethods, node=node, src_bytes=src_bytes)
                ic.inheritance = ibases
                concepts.append(ic)
            elif node.type == "struct_declaration":
                sname = _node_text(node.child_by_field_name("name"))
                if not sname:
                    continue
                smethods = [
                    _node_text(m.child_by_field_name("name"))
                    for m in _find_all(node, "method_declaration")
                    if m.child_by_field_name("name")
                ]
                sc = self._make_concept("Class", sname, "", f"struct {sname}", resource, ts, parent_id, node.start_point[0]+1, methods=smethods, node=node, src_bytes=src_bytes)
                concepts.append(sc)
            elif node.type in ("method_declaration", "local_function_statement"):
                name = _node_text(node.child_by_field_name("name"))
                if not name:
                    continue
                params_node = node.child_by_field_name("parameter_list")
                params = _node_text(params_node).strip("()") if params_node else ""
                ret = _node_text(node.child_by_field_name("return_type"))
                tp = self._cs_type_params(node)
                # Extract attributes and modifiers
                decs = []
                vis = []
                for child in node.children:
                    if child.type == "attribute_list":
                        for attr in child.children:
                            if attr.type == "attribute":
                                decs.append(_node_text(attr))
                    elif child.type == "modifier":
                        vis.append(_node_text(child))
                sig = f"{ret + ' ' if ret else ''}{name}({params})"
                fc = self._make_concept("Function", name, "", sig, resource, ts, parent_id, node.start_point[0]+1, node=node, src_bytes=src_bytes, type_params=tp)
                fc.decorators = decs
                fc.visibility = vis
                concepts.append(fc)
        return concepts
