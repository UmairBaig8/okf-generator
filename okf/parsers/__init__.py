"""Parser registry — maps file extensions to parser instances via get_parser().
Add new languages by importing the class and adding an entry to EXTENSION_MAP."""

from okf.parsers.python import PythonParser
from okf.parsers.javascript import JSTSParser
from okf.parsers.go import GoParser
from okf.parsers.java import JavaParser
from okf.parsers.rust import RustParser
from okf.parsers.ruby import RubyParser
from okf.parsers.c import CParser
from okf.parsers.cpp import CppParser
from okf.parsers.csharp import CSharpParser
from okf.parsers.sql import SQLParser
from okf.parsers.swift import SwiftParser
from okf.parsers.kotlin import KotlinParser

# Extension → parser class mapping.
# JS/TS is special-cased in get_parser() because it sets _path_ext for grammar selection.
EXTENSION_MAP: dict[str, type] = {
    ".py": PythonParser,
    ".js": JSTSParser,
    ".jsx": JSTSParser,
    ".mjs": JSTSParser,
    ".cjs": JSTSParser,
    ".ts": JSTSParser,
    ".tsx": JSTSParser,
    ".go": GoParser,
    ".java": JavaParser,
    ".rs": RustParser,
    ".rb": RubyParser,
    ".c": CParser,
    ".h": CParser,
    ".cpp": CppParser,
    ".cxx": CppParser,
    ".cc": CppParser,
    ".hpp": CppParser,
    ".hh": CppParser,
    ".cs": CSharpParser,
    ".sql": SQLParser,
    ".swift": SwiftParser,
    ".kt": KotlinParser,
    ".kts": KotlinParser,
}


def get_parser(ext: str):
    """Return a parser instance for the given file extension, or None."""
    cls = EXTENSION_MAP.get(ext)
    if cls is None:
        return None
    if cls is JSTSParser and ext in {".ts", ".tsx"}:
        p = cls()
        p._path_ext = ext
        return p
    return cls()
