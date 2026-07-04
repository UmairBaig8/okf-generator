"""Kotlin parser (tree-sitter). Extracts: classes, data classes, interfaces, objects, enums, generics, functions, typealiases, constructor params, visibility, inheritance, imports, calls."""
import os

from okf.parsers.base import _prev_comment, _find_all, _node_text, _safe_id, TreeSitterParser

def _kotlin_is_interface(node) -> bool:
    for child in node.children:
        if child.type == "interface":
            return True
    return False
class KotlinParser(TreeSitterParser):
    LANGUAGE   = "kotlin"
    EXTENSIONS = {".kt", ".kts"}
    _TS_MODULE = "tree_sitter_kotlin"
    _lang_obj  = None

    def _module_doc(self, root, src_bytes: bytes) -> str:
        for child in root.children:
            if child.type not in ("comment", ""):
                return _prev_comment(child, src_bytes)
        return ""

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []

        for node in _find_all(root, "class_declaration", "object_declaration",
                               "function_declaration", "type_alias"):

            if node.type == "class_declaration":
                name_node = node.child_by_field_name("name")
                if not name_node:
                    continue
                name = _node_text(name_node)
                doc = _prev_comment(node, src_bytes)
                is_iface = _kotlin_is_interface(node)
                ctype = "Interface" if is_iface else "Class"
                # Collect modifiers
                decs = []
                vis = []
                for child in node.children:
                    if child.type == "modifiers":
                        for mod in child.children:
                            if mod.type == "annotation":
                                decs.append(_node_text(mod))
                            elif mod.type == "visibility_modifier":
                                vis.append(_node_text(mod))
                            elif mod.type == "class_modifier":
                                t = _node_text(mod)
                                if t not in ("interface",):
                                    vis.append(t if t != "class" else "")

                # Type parameters
                tp = []
                for child in node.children:
                    if child.type == "type_parameters":
                        for tp_node in child.children:
                            if tp_node.type == "type_parameter":
                                tp.append(_node_text(tp_node.child_by_field_name("name") or tp_node))

                # Inheritance
                bases = []
                for child in node.children:
                    if child.type == "delegation_specifiers":
                        for spec in child.children:
                            if spec.type == "delegation_specifier":
                                for c2 in spec.children:
                                    if c2.type in ("user_type", "identifier", "constructor_invocation"):
                                        bases.append(_node_text(c2).split("(")[0].strip())

                # Members
                body = None
                for child in node.children:
                    if child.type in ("class_body", "enum_class_body"):
                        body = child
                        break
                methods = []
                if body:
                    for member in body.children:
                        if member.type == "function_declaration":
                            mn = member.child_by_field_name("name")
                            if mn:
                                methods.append(_node_text(mn))
                                mdoc = _prev_comment(member, src_bytes)
                                msig = self._kotlin_fn_sig(member)
                                mparent_id = f"{resource.replace(os.sep, '/')}/{_safe_id(name)}"
                                mc = self._make_concept("Function", _node_text(mn), mdoc, msig, resource, ts, mparent_id, member.start_point[0]+1, node=member, src_bytes=src_bytes)
                                concepts.append(mc)
                        elif member.type == "property_declaration":
                            # val/var at class level = field
                            pname_node = member.child_by_field_name("name")
                            if pname_node:
                                methods.append(_node_text(pname_node))

                # Fields from property_declaration inside class_body
                # and from primary constructor parameters (data class properties)
                fields = []
                # Primary constructor parameters
                for child in node.children:
                    if child.type == "primary_constructor":
                        for params_node in child.children:
                            if params_node.type == "class_parameters":
                                for param in params_node.children:
                                    if param.type == "class_parameter":
                                        pname = _node_text(param.child_by_field_name("name")) or \
                                                _node_text(next((c for c in param.children if c.type == "identifier"), None))
                                        ptype_node = None
                                        for c in param.children:
                                            if c.type in ("user_type", "nullable_type", "array_type", "type_identifier"):
                                                ptype_node = c
                                                break
                                        ptype = _node_text(ptype_node) if ptype_node else ""
                                        fvis = " ".join(vis)
                                        if pname:
                                            fields.append({"name": pname, "type": ptype, "visibility": fvis})
                # Body-level property declarations
                if body:
                    for member in body.children:
                        if member.type == "property_declaration":
                            pname = _node_text(member.child_by_field_name("name"))
                            ptype_node = None
                            for c in member.children:
                                if c.type == "user_type":
                                    ptype_node = c
                                    break
                            ptype = _node_text(ptype_node) if ptype_node else ""
                            fvis = " ".join(vis)
                            if pname:
                                fields.append({"name": pname, "type": ptype, "visibility": fvis})

                sig = f"{'interface ' if is_iface else 'class '}{name}"
                cc = self._make_concept(ctype, name, doc, sig, resource, ts, parent_id, node.start_point[0]+1, methods=methods, node=node, src_bytes=src_bytes, type_params=tp)
                cc.inheritance = bases
                cc.decorators = decs
                cc.visibility = vis
                cc.fields = fields
                concepts.append(cc)

            elif node.type == "object_declaration":
                name_node = node.child_by_field_name("name")
                if not name_node:
                    continue
                name = _node_text(name_node)
                doc = _prev_comment(node, src_bytes)
                # Type parameters
                tp = []
                for child in node.children:
                    if child.type == "type_parameters":
                        for tp_node in child.children:
                            if tp_node.type == "type_parameter":
                                tp.append(_node_text(tp_node.child_by_field_name("name") or tp_node))
                methods = []
                body = None
                for child in node.children:
                    if child.type == "class_body":
                        body = child
                        break
                if body:
                    for member in body.children:
                        if member.type == "function_declaration":
                            mn = member.child_by_field_name("name")
                            if mn:
                                methods.append(_node_text(mn))
                                mdoc = _prev_comment(member, src_bytes)
                                msig = self._kotlin_fn_sig(member)
                                mparent_id = f"{resource.replace(os.sep, '/')}/{_safe_id(name)}"
                                mc = self._make_concept("Function", _node_text(mn), mdoc, msig, resource, ts, mparent_id, member.start_point[0]+1, node=member, src_bytes=src_bytes)
                                concepts.append(mc)
                cc = self._make_concept("Class", name, doc, f"object {name}", resource, ts, parent_id, node.start_point[0]+1, methods=methods, node=node, src_bytes=src_bytes, type_params=tp)
                concepts.append(cc)

            elif node.type == "function_declaration":
                name_node = node.child_by_field_name("name")
                if not name_node:
                    continue
                # Skip if inside a class body (already emitted as method)
                p = node.parent
                in_class = False
                while p is not None:
                    if p.type in ("class_body", "enum_class_body"):
                        in_class = True
                        break
                    p = p.parent
                if in_class:
                    continue
                name = _node_text(name_node)
                doc = _prev_comment(node, src_bytes)
                sig = self._kotlin_fn_sig(node)
                # Modifiers
                vis = []
                for child in node.children:
                    if child.type == "modifiers":
                        for mod in child.children:
                            if mod.type == "visibility_modifier":
                                vis.append(_node_text(mod))
                fc = self._make_concept("Function", name, doc, sig, resource, ts, parent_id, node.start_point[0]+1, node=node, src_bytes=src_bytes)
                fc.visibility = vis
                concepts.append(fc)

            elif node.type == "type_alias":
                name_node = node.child_by_field_name("name")
                if not name_node:
                    continue
                name = _node_text(name_node)
                doc = _prev_comment(node, src_bytes)
                concepts.append(self._make_concept("Type", name, doc, f"typealias {name}", resource, ts, parent_id, node.start_point[0]+1, node=node, src_bytes=src_bytes))

        return concepts

    def _kotlin_fn_sig(self, node) -> str:
        name = _node_text(node.child_by_field_name("name"))
        params_node = None
        for child in node.children:
            if child.type == "function_value_parameters":
                params_node = child
                break
        params = _node_text(params_node).strip("()") if params_node else ""
        # Return type
        ret = ""
        for child in node.children:
            if child.type == "user_type":
                ret = _node_text(child)
                break
            if child.type in ("type_identifier",):
                ret = _node_text(child)
                break
        sig = f"fun {name}({params})"
        if ret:
            sig += f": {ret}"
        return sig

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        names = []
        for node in _find_all(root, "import"):
            for child in node.children:
                if child.type in ("identifier", "qualified_identifier"):
                    t = _node_text(child)
                    if t and t != "import":
                        names.append(t)
        return names

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        names = []
        for call in _find_all(node, "call_expression"):
            for child in call.children:
                if child.type in ("identifier", "navigation_expression"):
                    names.append(_node_text(child))
        return names
