"""Swift parser (tree-sitter). Extracts: classes, structs, enums, protocols (→Interface), generics, methods, functions, typealiases, doc comments, inheritance, calls."""
import os

from okf.parsers.base import _prev_comment, _find_all, _node_text, _safe_id, TreeSitterParser

class SwiftParser(TreeSitterParser):
    LANGUAGE   = "swift"
    EXTENSIONS = {".swift"}
    _TS_MODULE = "tree_sitter_swift"
    _lang_obj  = None

    def _module_doc(self, root, src_bytes: bytes) -> str:
        for child in root.children:
            if child.type not in ("comment", "multiline_comment", ""):
                return _prev_comment(child, src_bytes)
        return ""

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []

        for node in _find_all(root,
                               "class_declaration", "struct_declaration",
                               "protocol_declaration", "enum_declaration",
                               "function_declaration", "typealias_declaration",
                               "init_declaration"):

            if node.type in ("class_declaration", "protocol_declaration"):
                # struct, enum, class all use class_declaration — detect from keyword child
                keyword = ""
                for c in node.children:
                    if c.type in ("struct", "class", "enum", "protocol"):
                        keyword = c.type
                        break
                name_node = next((c for c in node.children if c.type == "type_identifier"), None)
                if not name_node:
                    continue
                name = _node_text(name_node)
                doc = _prev_comment(node, src_bytes)
                is_protocol_like = keyword == "protocol"
                ctype = "Interface" if is_protocol_like else "Class"
                kind_name = keyword
                sig = f"{kind_name} {name}"

                # Type parameters
                tp = []
                for child in node.children:
                    if child.type == "type_parameters":
                        for tp_node in child.children:
                            if tp_node.type == "type_parameter":
                                tp.append(_node_text(tp_node.child_by_field_name("identifier") or tp_node))
                            elif tp_node.type == "identifier":
                                tp.append(_node_text(tp_node))

                # Inheritance
                bases = []
                for child in node.children:
                    if child.type == "inheritance_specifier":
                        for item in child.children:
                            if item.type in ("type_identifier", "identifier", "user_type"):
                                bases.append(_node_text(item))

                # Members
                body = None
                for child in node.children:
                    if child.type in ("class_body", "protocol_body", "enum_class_body"):
                        body = child
                        break
                methods = []
                if body:
                    for member in body.children:
                        if member.type == "function_declaration":
                            mname_node = next((c for c in member.children if c.type in ("simple_identifier", "identifier")), None)
                            if mname_node:
                                methods.append(_node_text(mname_node))
                                # Emit method
                                mdoc = _prev_comment(member, src_bytes)
                                msig = self._swift_fn_sig(member)
                                mparent_id = f"{resource.replace(os.sep, '/')}/{_safe_id(name)}"
                                mc = self._make_concept("Function", _node_text(mname_node), mdoc, msig, resource, ts, mparent_id, member.start_point[0]+1, node=member, src_bytes=src_bytes)
                                concepts.append(mc)
                        elif member.type == "init_declaration":
                            methods.append("init")
                            mdoc = _prev_comment(member, src_bytes)
                            msig = self._swift_init_sig(member)
                            mparent_id = f"{resource.replace(os.sep, '/')}/{_safe_id(name)}"
                            mc = self._make_concept("Function", "init", mdoc, msig, resource, ts, mparent_id, member.start_point[0]+1, node=member, src_bytes=src_bytes)
                            concepts.append(mc)

                cc = self._make_concept(ctype, name, doc, sig, resource, ts, parent_id, node.start_point[0]+1, methods=methods, node=node, src_bytes=src_bytes, type_params=tp)
                cc.inheritance = bases
                concepts.append(cc)

            elif node.type == "function_declaration":
                name_node = next((c for c in node.children if c.type in ("simple_identifier", "identifier")), None)
                if not name_node:
                    continue
                # Skip if inside a type body (already emitted as method)
                p = node.parent
                in_type = False
                while p is not None:
                    if p.type in ("class_body", "protocol_body", "enum_class_body"):
                        in_type = True
                        break
                    p = p.parent
                if in_type:
                    continue
                name = _node_text(name_node)
                doc = _prev_comment(node, src_bytes)
                sig = self._swift_fn_sig(node)
                concepts.append(self._make_concept("Function", name, doc, sig, resource, ts, parent_id, node.start_point[0]+1, node=node, src_bytes=src_bytes))

            elif node.type == "typealias_declaration":
                name_node = node.child_by_field_name("name") or next((c for c in node.children if c.type in ("simple_identifier", "identifier")), None)
                if not name_node:
                    continue
                name = _node_text(name_node)
                doc = _prev_comment(node, src_bytes)
                concepts.append(self._make_concept("Type", name, doc, f"typealias {name}", resource, ts, parent_id, node.start_point[0]+1, node=node, src_bytes=src_bytes))

        return concepts

    def _swift_fn_sig(self, node) -> str:
        name_node = next((c for c in node.children if c.type in ("simple_identifier", "identifier")), None)
        name = _node_text(name_node) if name_node else "?"
        params_node = None
        for child in node.children:
            if child.type in ("value_arguments", "parameter"):
                params_node = child
                break
        params = _node_text(params_node) if params_node else ""
        # Return type
        ret = ""
        for child in node.children:
            if child.type == "type_annotation" or (child.type == "input_parameters" and child.next_sibling and child.next_sibling.type in ("output_type", "return_type")):
                ret = _node_text(child)
                break
            if child.type in ("output_type",):
                ret = _node_text(child)
                break
        sig = f"func {name}({params.strip('()')})"
        if ret:
            sig += f" -> {ret}"
        # throws
        for child in node.children:
            if child.type == "throws":
                sig += " throws"
                break
        return sig

    def _swift_init_sig(self, node) -> str:
        params_node = None
        for child in node.children:
            if child.type in ("value_arguments", "parameter"):
                params_node = child
                break
        params = _node_text(params_node) if params_node else ""
        sig = f"init({params.strip('()')})"
        for child in node.children:
            if child.type == "throws":
                sig += " throws"
                break
        return sig

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        names = []
        for node in _find_all(root, "import_declaration"):
            for child in node.children:
                if child.type in ("identifier", "simple_identifier"):
                    t = _node_text(child)
                    if t and t != "import":
                        names.append(t)
        return names

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        names = []
        for call in _find_all(node, "call_expression"):
            for child in call.children:
                if child.type in ("identifier", "simple_identifier", "navigation_expression"):
                    if child.type == "navigation_expression":
                        names.append(_node_text(child))
                    else:
                        names.append(_node_text(child))
            # Also check call_suffix
            for child in call.children:
                if child.type == "call_suffix" and child.prev_sibling:
                    names.append(_node_text(child.prev_sibling))
        return names
