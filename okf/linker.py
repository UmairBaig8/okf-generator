"""
okf/linker.py  — cross-reference pass for the okf-generator pipeline.

Adds two edge types on top of the flat concept list produced by
scan_codebase(), before write_bundle() serialises anything:

  1. imports / used_by   —  code Module concept  <->  Dependency concept
  2. calls / called_by   —  code Function/Class   <->  code Function/Class

Coverage
--------
Code languages:   Python (AST), JavaScript, TypeScript, Go, Java, Rust, Ruby
Manifest ecosystems (dep-index side only):
  pip, npm, cargo, go, maven, gradle, rubygems, composer, swiftpm, clojars, hex

Languages that have manifests but no code parser yet (PHP/Composer,
Clojure/Clojars, Elixir/Hex, Swift/SwiftPM) are indexed on the
Dependency side so they'll link automatically once a parser is added;
no action needed here.

Integration — generator.py wiring required
-------------------------------------------
See PATCH NOTES at bottom of file.  Short version:

  1.  Concept dataclass — four new fields (imports, calls_raw, calls, called_by).
  2.  Each language parser — populate concept.imports on Module concepts
      and concept.calls_raw on Function/Class/Method concepts.
  3.  scan_codebase() — call link_all(concepts) before return.
  4.  generator._body() — render Calls / Called By / Used By sections.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field

log = logging.getLogger("okf_gen")


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

@dataclass
class LinkStats:
    imports_resolved: int = 0
    imports_unresolved: int = 0
    calls_resolved: int = 0
    calls_ambiguous: int = 0
    calls_unresolved: int = 0
    unresolved_import_names: set = field(default_factory=set)
    unresolved_call_names: set = field(default_factory=set)

    def summary_line(self) -> str:
        return (
            f"Linking: {self.imports_resolved} dep-links resolved "
            f"({self.imports_unresolved} unresolved stdlib/internal), "
            f"{self.calls_resolved} call edges resolved "
            f"({self.calls_ambiguous} ambiguous, {self.calls_unresolved} unresolved)"
        )


# ---------------------------------------------------------------------------
# Ecosystem map — parser LANGUAGE string -> manifest_scanner ecosystem string
#
# Java maps to both maven AND gradle since both parsers exist; we check both.
# Languages with manifests but no code parser (php, clojure, elixir, swift)
# appear on the Dependency side only — they'll auto-link once a parser lands.
# ---------------------------------------------------------------------------

LANG_TO_ECOSYSTEMS: dict[str, list[str]] = {
    "python":     ["pip"],
    "javascript": ["npm"],
    "typescript": ["npm"],
    "go":         ["go"],
    "rust":       ["cargo"],
    "java":       ["maven", "gradle"],
    "ruby":       ["rubygems"],
}

# Bare module names that are stdlib / built-in and should never be linked
# to a manifest dependency, regardless of language.  These are the most
# common false-positive sources; the list is intentionally conservative.
_STDLIB_PREFIXES = {
    # Python stdlib top-level modules
    "os", "sys", "re", "io", "abc", "ast", "csv", "copy", "time", "json",
    "math", "enum", "uuid", "pdb", "pprint", "shutil", "struct", "types",
    "typing", "hashlib", "logging", "pathlib", "inspect", "functools",
    "itertools", "operator", "datetime", "threading", "multiprocessing",
    "subprocess", "collections", "contextlib", "dataclasses", "traceback",
    "warnings", "unittest", "textwrap", "string", "random", "socket",
    "urllib", "http", "email", "html", "xml", "configparser", "argparse",
    "tempfile", "weakref", "gc", "platform", "signal", "atexit",
    # Go stdlib prefixes
    "fmt", "os", "io", "log", "net", "sync", "time", "sort", "math",
    "strings", "strconv", "errors", "bytes", "bufio", "context",
    "encoding", "runtime", "reflect", "testing",
    # Rust core/std
    "std", "core", "alloc",
    # Java java.* and javax.*
    "java", "javax", "sun", "com.sun",
    # JS/Node built-ins
    "path", "fs", "os", "url", "http", "https", "crypto", "events",
    "stream", "util", "buffer", "child_process", "cluster", "dns",
    "net", "tls", "readline", "vm", "assert", "querystring", "zlib",
    # Ruby stdlib
    "json", "csv", "date", "time", "uri", "net", "open", "set",
    "fileutils", "pathname", "tempfile", "yaml", "logger", "digest",
    "base64", "erb", "forwardable", "singleton", "observer",
}


def _is_stdlib(name: str) -> bool:
    root = name.split(".")[0].split("/")[0].split("::")[0].lower()
    return root in _STDLIB_PREFIXES


# ---------------------------------------------------------------------------
# Import name normalisation
# ---------------------------------------------------------------------------

def _normalize_import(raw: str, lang: str) -> str | None:
    """Reduce a raw import string to the top-level package name as it
    appears in the manifest.  Returns None for relative/internal imports."""
    raw = raw.strip().strip("\"'")
    if not raw:
        return None

    if lang == "python":
        if raw.startswith("."):          # relative import
            return None
        name = raw.split(".")[0]
        return None if _is_stdlib(name) else name

    if lang in ("javascript", "typescript"):
        if raw.startswith(".") or raw.startswith("/"):  # relative
            return None
        if raw.startswith("@"):
            parts = raw.split("/")
            name = "/".join(parts[:2]) if len(parts) >= 2 else raw
        else:
            name = raw.split("/")[0]
        return None if _is_stdlib(name) else name

    if lang == "go":
        # stdlib: single path segment with no dot (fmt, os, sync…)
        if "/" not in raw and "." not in raw:
            return None
        return raw   # full module path is the key in go.mod

    if lang == "rust":
        if raw in ("std", "core", "alloc", "crate", "super", "self"):
            return None
        name = raw.split("::")[0]
        return None if _is_stdlib(name) else name

    if lang == "java":
        # top-level group: java.util.List → "java" (stdlib)
        # org.springframework → top two segments → "org.springframework"
        parts = raw.split(".")
        if _is_stdlib(parts[0]):
            return None
        return ".".join(parts[:2]) if len(parts) >= 2 else parts[0]

    if lang == "ruby":
        if raw.startswith(".") or raw.startswith("/"):  # require_relative
            return None
        name = raw.split("/")[0].split(".")[0]
        return None if _is_stdlib(name) else name

    return raw.split(".")[0].split("/")[0] or None


# ---------------------------------------------------------------------------
# Feature 1: Dependency-to-code linking
# ---------------------------------------------------------------------------

def build_dep_index(concepts: list) -> dict[tuple[str, str], str]:
    """{ (ecosystem, dep_name): concept_id }  — built from Dependency concepts."""
    index: dict[tuple[str, str], str] = {}
    for c in concepts:
        if c.type != "Dependency":
            continue
        ecosystem = c.body_extra.get("ecosystem")
        if not ecosystem:
            for tag in c.tags:
                if tag.startswith("ecosystem:"):
                    ecosystem = tag[len("ecosystem:"):]
                    break
        if ecosystem:
            # index on both exact title and lower-cased to handle npm case variations
            index[(ecosystem, c.title)] = c.concept_id
            index[(ecosystem, c.title.lower())] = c.concept_id
    return index


def link_dependencies(concepts: list, stats: LinkStats) -> None:
    """Mutates concepts in place.

    Module concepts gain resolved Dependency concept_ids in concept.related.
    Dependency concepts gain body_extra["used_by"] = sorted list of module
    concept_ids (rendered by generator._body's Dependency table).
    """
    dep_index = build_dep_index(concepts)
    used_by: dict[str, set] = defaultdict(set)

    for c in concepts:
        if c.type != "Module":
            continue
        raw_imports: list[str] = getattr(c, "imports", None) or []
        if not raw_imports:
            continue

        lang = next(
            (tag[len("lang:"):] for tag in c.tags if tag.startswith("lang:")),
            "python",
        )
        ecosystems = LANG_TO_ECOSYSTEMS.get(lang, [])
        if not ecosystems:
            continue

        for raw in raw_imports:
            name = _normalize_import(raw, lang)
            if name is None:
                stats.imports_unresolved += 1
                continue

            dep_id = None
            for eco in ecosystems:
                dep_id = dep_index.get((eco, name)) or dep_index.get((eco, name.lower()))
                if dep_id:
                    break

            if dep_id is None:
                stats.imports_unresolved += 1
                stats.unresolved_import_names.add(f"{lang}:{name}")
                continue

            stats.imports_resolved += 1
            if dep_id not in c.related:
                c.related.append(dep_id)
            used_by[dep_id].add(c.concept_id)

    by_id = {c.concept_id: c for c in concepts}
    for dep_id, module_ids in used_by.items():
        dep = by_id.get(dep_id)
        if dep is not None:
            dep.body_extra["used_by"] = sorted(module_ids)


# ---------------------------------------------------------------------------
# Feature 2: Call-graph edges
# ---------------------------------------------------------------------------

def _build_name_index(concepts: list) -> dict[str, list]:
    """{ bare_name: [concept, …] }  — may have multiple entries per name."""
    index: dict[str, list] = defaultdict(list)
    for c in concepts:
        if c.type in ("Function", "Class", "Method"):
            index[c.title].append(c)
    return index


def _tag_value(c, prefix: str) -> str | None:
    for tag in c.tags:
        if tag.startswith(prefix):
            return tag[len(prefix):]
    return None


def _same_file(a, b) -> bool:
    return a.resource == b.resource


def _same_domain(a, b) -> bool:
    dom_a = _tag_value(a, "domain:")
    dom_b = _tag_value(b, "domain:")
    return dom_a is not None and dom_a == dom_b


def _resolve_callee(caller, raw: str, name_index: dict[str, list]):
    """Returns (resolved | None, [ambiguous candidates]).

    Resolution order (conservative):
      1. Exact name, same file       → certain
      2. Exact name, same domain     → likely
      3. Globally unique name        → probable
      4. Multiple matches            → ambiguous (don't guess)
    """
    bare = raw.rsplit(".", 1)[-1]  # strip obj.method → method
    candidates = name_index.get(bare)
    if not candidates:
        return None, []

    same_file = [c for c in candidates if _same_file(caller, c)]
    if len(same_file) == 1:
        return same_file[0], []

    same_dom = [c for c in candidates if _same_domain(caller, c)]
    if len(same_dom) == 1:
        return same_dom[0], []

    if len(candidates) == 1:
        return candidates[0], []

    return None, candidates   # ambiguous


def link_calls(concepts: list, stats: LinkStats) -> None:
    """Mutates concepts in place.

    caller.calls       = [resolved callee concept_ids]
    caller.possible_calls  (attribute added dynamically) = [ambiguous ids]
    callee.called_by   = [sorted caller concept_ids]
    """
    name_index = _build_name_index(concepts)
    by_id = {c.concept_id: c for c in concepts}
    called_by: dict[str, set] = defaultdict(set)

    for caller in concepts:
        raw_calls: list[str] = getattr(caller, "calls_raw", None) or []
        if not raw_calls:
            continue

        for raw in raw_calls:
            resolved, ambiguous = _resolve_callee(caller, raw, name_index)
            if resolved is not None:
                if resolved.concept_id == caller.concept_id:
                    continue   # skip self-recursion noise
                if resolved.concept_id not in caller.calls:
                    caller.calls.append(resolved.concept_id)
                called_by[resolved.concept_id].add(caller.concept_id)
                stats.calls_resolved += 1
            elif ambiguous:
                if not hasattr(caller, "possible_calls"):
                    caller.possible_calls = []
                for cand in ambiguous:
                    if cand.concept_id not in caller.possible_calls:
                        caller.possible_calls.append(cand.concept_id)
                stats.calls_ambiguous += 1
            else:
                stats.calls_unresolved += 1
                stats.unresolved_call_names.add(raw)

    for callee_id, caller_ids in called_by.items():
        callee = by_id.get(callee_id)
        if callee is not None:
            callee.called_by = sorted(caller_ids)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def link_all(concepts: list) -> LinkStats:
    """Run both linking passes. Call once after scan_codebase() has
    assembled the full concept list (code + Dependency concepts) and
    before write_bundle() writes anything to disk."""
    stats = LinkStats()
    link_dependencies(concepts, stats)
    link_calls(concepts, stats)
    return stats


# ---------------------------------------------------------------------------
# Import / call collectors — one function per language parser class.
# Called FROM generator.py parsers during parse_file() / _parse_symbols().
#
# These are standalone functions (not methods) so each parser can import
# them individually without circular imports.
# ---------------------------------------------------------------------------

# ── Python (AST) ─────────────────────────────────────────────────────────

def py_collect_imports(tree) -> list[str]:
    """Walk a Python AST and return all raw module names imported."""
    import ast as _ast
    names = []
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, _ast.ImportFrom):
            if node.module:
                names.append(node.module)
    return names


def py_collect_calls(node) -> list[str]:
    """Walk a Python function/class AST node and return raw callee names."""
    import ast as _ast
    names = []
    for n in _ast.walk(node):
        if isinstance(n, _ast.Call):
            if isinstance(n.func, _ast.Name):
                names.append(n.func.id)
            elif isinstance(n.func, _ast.Attribute):
                names.append(n.func.attr)
    return names


# ── JavaScript / TypeScript (tree-sitter) ────────────────────────────────

def _ts_find_all(node, *kinds):
    if node.type in kinds:
        yield node
    for child in node.children:
        yield from _ts_find_all(child, *kinds)


def js_collect_imports(root, src_bytes: bytes) -> list[str]:
    """ES module import + CommonJS require()."""
    names = []
    for node in _ts_find_all(root, "import_statement"):
        # string child holds the module path: 'react' or "react"
        for child in node.children:
            if child.type == "string":
                # string_fragment is the inner text without quotes
                for frag in child.children:
                    if frag.type == "string_fragment":
                        names.append(frag.text.decode(errors="replace"))
                        break
    # CommonJS require('x')
    for node in _ts_find_all(root, "call_expression"):
        fn = node.child_by_field_name("function") or (node.children[0] if node.children else None)
        if fn and fn.type == "identifier" and fn.text == b"require":
            args = node.child_by_field_name("arguments")
            if args:
                for child in args.children:
                    if child.type == "string":
                        for frag in child.children:
                            if frag.type == "string_fragment":
                                names.append(frag.text.decode(errors="replace"))
                                break
    return names


def js_collect_calls(node, src_bytes: bytes) -> list[str]:
    """call_expression children: identifier (bare) or member_expression (obj.method)."""
    names = []
    for n in _ts_find_all(node, "call_expression"):
        fn = n.child_by_field_name("function") or (n.children[0] if n.children else None)
        if fn is None:
            continue
        if fn.type == "identifier":
            names.append(fn.text.decode(errors="replace"))
        elif fn.type == "member_expression":
            # last child before closing is the method name (property)
            prop = fn.child_by_field_name("property")
            if prop:
                names.append(prop.text.decode(errors="replace"))
    return names


# ── Go (tree-sitter) ─────────────────────────────────────────────────────

def go_collect_imports(root, src_bytes: bytes) -> list[str]:
    """import_declaration → import_spec → interpreted_string_literal content."""
    names = []
    for node in _ts_find_all(root, "import_declaration"):
        for spec in _ts_find_all(node, "import_spec"):
            # path field or first interpreted_string_literal child
            path_node = spec.child_by_field_name("path")
            if path_node is None:
                for child in spec.children:
                    if child.type == "interpreted_string_literal":
                        path_node = child
                        break
            if path_node:
                raw = path_node.text.decode(errors="replace").strip('"')
                if raw:
                    names.append(raw)
    return names


def go_collect_calls(node, src_bytes: bytes) -> list[str]:
    """call_expression → function field.  Strips package prefix: fmt.Println → Println."""
    names = []
    for n in _ts_find_all(node, "call_expression"):
        fn = n.child_by_field_name("function")
        if fn is None:
            continue
        if fn.type == "selector_expression":
            # field child is the method name
            field_node = fn.child_by_field_name("field")
            if field_node:
                names.append(field_node.text.decode(errors="replace"))
        elif fn.type == "identifier":
            names.append(fn.text.decode(errors="replace"))
    return names


# ── Java (tree-sitter) ───────────────────────────────────────────────────

def _java_scoped_id_text(node) -> str:
    """Reconstruct a dotted name from a scoped_identifier tree."""
    if node is None:
        return ""
    if node.type == "identifier":
        return node.text.decode(errors="replace")
    if node.type == "scoped_identifier":
        left = node.child_by_field_name("scope")
        right = node.child_by_field_name("name")
        scope = _java_scoped_id_text(left) if left else ""
        r = right.text.decode(errors="replace") if right else ""
        return f"{scope}.{r}" if scope else r
    return node.text.decode(errors="replace") if node.text else ""


def java_collect_imports(root, src_bytes: bytes) -> list[str]:
    """import_declaration → scoped_identifier → top two dotted segments."""
    names = []
    for node in _ts_find_all(root, "import_declaration"):
        for child in node.children:
            if child.type == "scoped_identifier":
                full = _java_scoped_id_text(child)
                if full:
                    names.append(full)
    return names


def java_collect_calls(node, src_bytes: bytes) -> list[str]:
    """method_invocation → name field."""
    names = []
    for n in _ts_find_all(node, "method_invocation"):
        name_node = n.child_by_field_name("name")
        if name_node:
            names.append(name_node.text.decode(errors="replace"))
    return names


# ── Rust (tree-sitter) ───────────────────────────────────────────────────

def _rust_use_crate(node) -> str | None:
    """Extract the top-level crate name from a use_declaration subtree."""
    if node.type == "identifier":
        return node.text.decode(errors="replace")
    if node.type == "scoped_identifier":
        # scope::name — walk left to find root identifier
        scope = node.child_by_field_name("scope")
        if scope:
            return _rust_use_crate(scope)
        # fallback: first identifier child
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode(errors="replace")
    if node.type == "scoped_use_list":
        # crate::{A, B} — first child is identifier
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode(errors="replace")
    return None


def rust_collect_imports(root, src_bytes: bytes) -> list[str]:
    """use_declaration → crate name (first path segment)."""
    names = []
    for node in _ts_find_all(root, "use_declaration"):
        for child in node.children:
            if child.type in ("identifier", "scoped_identifier", "scoped_use_list"):
                crate = _rust_use_crate(child)
                if crate:
                    names.append(crate)
                break
    return names


def rust_collect_calls(node, src_bytes: bytes) -> list[str]:
    """call_expression and method_call_expression."""
    names = []
    for n in _ts_find_all(node, "call_expression"):
        fn = n.child_by_field_name("function")
        if fn is None:
            continue
        if fn.type == "identifier":
            names.append(fn.text.decode(errors="replace"))
        elif fn.type in ("scoped_identifier", "field_expression"):
            # last identifier segment
            name_node = fn.child_by_field_name("name") or fn.child_by_field_name("field")
            if name_node:
                names.append(name_node.text.decode(errors="replace"))
    for n in _ts_find_all(node, "method_call_expression"):
        name_node = n.child_by_field_name("name")
        if name_node:
            names.append(name_node.text.decode(errors="replace"))
    return names


# ── Ruby (tree-sitter) ───────────────────────────────────────────────────

def ruby_collect_imports(root, src_bytes: bytes) -> list[str]:
    """Top-level call nodes where the method is 'require' (not require_relative)."""
    names = []
    for node in _ts_find_all(root, "call"):
        # identifier child is the method name
        method_node = None
        for child in node.children:
            if child.type == "identifier":
                method_node = child
                break
        if method_node is None or method_node.text != b"require":
            continue
        # argument_list → string → string_content
        for child in node.children:
            if child.type == "argument_list":
                for arg in child.children:
                    if arg.type == "string":
                        for frag in arg.children:
                            if frag.type == "string_content":
                                names.append(frag.text.decode(errors="replace"))
    return names


def ruby_collect_calls(node, src_bytes: bytes) -> list[str]:
    """call nodes with an explicit receiver (obj.method) — captures method name."""
    names = []
    for n in _ts_find_all(node, "call"):
        # if the node has a receiver (obj.method), the method is an identifier child
        # after the dot; bare calls (helper) appear as plain identifiers
        children = [c for c in n.children if c.type not in {".", "(", ")", " "}]
        if len(children) >= 2:
            # last meaningful child before argument_list is the method name
            method_node = None
            for child in reversed(n.children):
                if child.type == "identifier":
                    method_node = child
                    break
            if method_node:
                names.append(method_node.text.decode(errors="replace"))
    return names
