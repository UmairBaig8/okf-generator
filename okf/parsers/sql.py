"""SQL parser (tree-sitter). Extracts: tables (with columns, PK, FK, constraints), views, functions/procedures, indexes, triggers."""
import os
import re
from pathlib import Path

from okf.parsers.base import Concept, _prev_comment, _node_text, _safe_id, _first_line, TreeSitterParser

class SQLParser(TreeSitterParser):
    LANGUAGE   = "sql"
    EXTENSIONS = {".sql"}
    _TS_MODULE = "tree_sitter_sql"
    _lang_obj  = None

    _KIND_MAP = {
        "create_table": "Table",
        "create_view": "View",
        "create_function": "Function",
        "create_procedure": "Function",
        "create_index": "Index",
        "create_trigger": "Trigger",
        "create_type": "Type",
    }

    def _module_doc(self, root, src_bytes: bytes) -> str:
        for child in root.children:
            if child.type not in {"comment", "marginalia", ""}:
                return _prev_comment(child, src_bytes)
        return ""

    def _parse_symbols(self, root, src_bytes, resource, ts, parent_id):
        concepts = []
        for stmt in root.children:
            if stmt.type != "statement" or not stmt.children:
                continue
            inner = stmt.children[0]
            ctype = self._KIND_MAP.get(inner.type)
            if ctype is None:
                continue

            name = self._sql_name(inner, ctype)
            if not name:
                continue
            doc = _prev_comment(inner, src_bytes)
            sig = _node_text(inner)
            if len(sig) > 200:
                sig = sig[:200] + " ..."

            if ctype == "Function":
                params = self._sql_params(inner)
                sig = f"{'CREATE OR REPLACE ' if any(c.type == 'keyword_replace' for c in inner.children) else 'CREATE '}{inner.type.upper().split('_')[1]} {name}({params})"
                concepts.append(self._make_concept(
                    "Function", name, doc, sig, resource, ts, parent_id,
                    inner.start_point[0]+1, node=inner, src_bytes=src_bytes))
            else:
                cid = re.sub(r"\.[^/]+$", "", resource).replace(os.sep, "/")
                cc = Concept(
                    type=ctype, title=name,
                    description=_first_line(doc) or f"{ctype} defined in {Path(resource).name}",
                    docstring=doc, signature=sig,
                    resource=resource, tags=[self.LANGUAGE, ctype.lower()],
                    timestamp=ts, source_lines=(inner.start_point[0]+1, inner.end_point[0]+1),
                    concept_id=f"{cid}/{_safe_id(name)}",
                    related=[parent_id],
                )
                # Extract column definitions for CREATE TABLE
                if inner.type == "create_table":
                    sql_cols = []
                    for child in inner.children:
                        if child.type == "column_definitions":
                            for col in child.children:
                                if col.type == "column_definition":
                                    col_name = _node_text(col.child_by_field_name("name"))
                                    col_type = _node_text(col.child_by_field_name("type"))
                                    # Collect constraints
                                    constraints = []
                                    fk_ref = ""
                                    for c2 in col.children:
                                        t = c2.type
                                        if t == "keyword_primary":
                                            constraints.append("PRIMARY KEY")
                                        elif t == "keyword_unique":
                                            constraints.append("UNIQUE")
                                        elif t == "keyword_not":
                                            constraints.append("NOT NULL")
                                        elif t == "keyword_null":
                                            pass  # handled by NOT above
                                        elif t == "keyword_default":
                                            pass  # next child is the default value
                                        elif t == "keyword_references":
                                            # next child is object_reference
                                            pass
                                        elif t == "object_reference":
                                            has_ref = False
                                            for ref_child in col.children:
                                                if ref_child.type == "keyword_references":
                                                    has_ref = True
                                                if ref_child is c2 and has_ref:
                                                    break
                                            if not has_ref:
                                                continue
                                            fk_ref = _node_text(c2)
                                    col_constraint = " ".join(constraints)
                                    if fk_ref:
                                        col_constraint += f" REFERENCES {fk_ref}" if col_constraint else f"REFERENCES {fk_ref}"
                                    sql_cols.append({"name": col_name, "type": col_type, "visibility": col_constraint})
                    cc.fields = sql_cols
                concepts.append(cc)
        return concepts

    @staticmethod
    def _sql_name(node, ctype: str) -> str:
        for c in node.children:
            if c.type == "object_reference":
                for cc in c.children:
                    if cc.type == "identifier":
                        return _node_text(cc)
            if c.type == "identifier" and ctype == "Index":
                return _node_text(c)
        return ""

    @staticmethod
    def _sql_params(node) -> str:
        for c in node.children:
            if c.type == "function_arguments":
                return _node_text(c).strip("()")
        return ""
