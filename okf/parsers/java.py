"""Java parser (tree-sitter). Extracts: classes, interfaces, enums, methods, constructors, Javadoc, generics, annotations, visibility, inheritance, fields, imports, calls."""

import re
from okf.parsers.base import _prev_comment, _find_all, _node_text, _parse_doc_tags, TreeSitterParser

class JavaParser(TreeSitterParser):
    LANGUAGE   = "java"
    EXTENSIONS = {".java"}
    _TS_MODULE = "tree_sitter_java"
    _lang_obj  = None

    def _module_doc(self, root, src_bytes: bytes) -> str:
        for child in root.children:
            if child.type == "class_declaration":
                return _prev_comment(child, src_bytes)
        return ""

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []

        for node in _find_all(root, "class_declaration", "interface_declaration", "enum_declaration"):
            name_node = node.child_by_field_name("name")
            if not name_node:
                continue
            name = _node_text(name_node)
            doc  = _prev_comment(node, src_bytes)
            # strip /** */ markers from Javadoc
            doc  = re.sub(r"/\*+|\*+/", "", doc).strip().lstrip("*").strip()

            # collect methods
            methods = []
            for method in _find_all(node, "method_declaration", "constructor_declaration"):
                mname = method.child_by_field_name("name")
                if mname:
                    methods.append(_node_text(mname))
                    # emit method as Function concept
                    mdoc    = _prev_comment(method, src_bytes)
                    mdoc    = re.sub(r"/\*+|\*+/", "", mdoc).strip().lstrip("*").strip()
                    mparams = self._java_params(method)
                    mret    = _node_text(method.child_by_field_name("type"))
                    msig    = f"{mret} {_node_text(mname)}({mparams})"
                    tp = self._java_type_params(method)
                    mdec = []
                    mvis = []
                    for child in method.children:
                        if child.type == "modifiers":
                            for c in child.children:
                                if c.type in ("annotation", "marker_annotation"):
                                    mdec.append(_node_text(c))
                                else:
                                    mvis.append(_node_text(c))
                    mc = self._make_concept(
                        "Function", _node_text(mname), mdoc, msig,
                        resource, ts, parent_id, method.start_point[0]+1,
                        node=method, src_bytes=src_bytes, type_params=tp)
                    mc.decorators = mdec
                    mc.visibility = mvis
                    parsed_params, parsed_returns = _parse_doc_tags(mdoc, "java")
                    if parsed_params:
                        mc.params = parsed_params
                    if parsed_returns:
                        mc.returns = parsed_returns
                    concepts.append(mc)

            # Extract fields
            java_fields = []
            for body_child in node.children:
                if body_child.type == "class_body":
                    for member in body_child.children:
                        if member.type == "field_declaration":
                            ftype = _node_text(member.child_by_field_name("type"))
                            decl = member.child_by_field_name("declarator")
                            fname = _node_text(decl.child_by_field_name("name")) if decl else ""
                            fvis = ""
                            for mc in member.children:
                                if mc.type == "modifiers":
                                    fvis = " ".join(_node_text(c) for c in mc.children if c.type not in ("annotation", "marker_annotation"))
                            if fname:
                                java_fields.append({"name": fname, "type": ftype, "visibility": fvis})
            # Collect modifiers, annotations, inheritance, and visibility
            bases = []
            decs = []
            vis = []
            extra_mod_text = ""
            for child in node.children:
                if child.type == "modifiers":
                    for c in child.children:
                        if c.type in ("annotation", "marker_annotation"):
                            decs.append(_node_text(c))
                        else:
                            extra_mod_text += _node_text(c) + " "
                            vis.append(_node_text(c))
                elif child.type == "superclass":
                    for ch in child.children:
                        if ch.type in ("type_identifier", "scoped_type_identifier"):
                            bases.append(_node_text(ch))
                elif child.type == "super_interfaces":
                    for ci in child.children:
                        if ci.type == "type_list":
                            for tc in ci.children:
                                if tc.type in ("type_identifier", "scoped_type_identifier"):
                                    bases.append(_node_text(tc))
                        elif ci.type in ("type_identifier", "scoped_type_identifier"):
                            bases.append(_node_text(ci))
            tp = self._java_type_params(node)
            sig  = f"{extra_mod_text}class {name}" if node.type == "class_declaration" else \
                   f"{extra_mod_text}interface {name}" if node.type == "interface_declaration" else \
                   f"enum {name}"
            cc = self._make_concept(
                "Class", name, doc, sig, resource, ts, parent_id,
                node.start_point[0]+1, methods=methods, node=node, src_bytes=src_bytes,
                type_params=tp)
            cc.inheritance = bases
            cc.decorators = decs
            cc.visibility = vis
            cc.fields = java_fields
            concepts.insert(0, cc)

        return concepts

    def _collect_imports(self, root, src_bytes: bytes) -> list[str]:
        from okf.linker import java_collect_imports
        return java_collect_imports(root, src_bytes)

    def _collect_calls(self, node, src_bytes: bytes) -> list[str]:
        from okf.linker import java_collect_calls
        return java_collect_calls(node, src_bytes)

    def _java_params(self, node) -> str:
        p = node.child_by_field_name("parameters")
        return _node_text(p).strip("()") if p else ""

    def _java_type_params(self, node):
        tp = node.child_by_field_name("type_parameters")
        if not tp:
            return []
        text = _node_text(tp)
        inner = text.strip("<>").strip()
        if not inner:
            return []
        # Split on commas respecting nested <>
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
