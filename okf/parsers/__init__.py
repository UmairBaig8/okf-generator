"""Parser registry — delegates to plugin system.

For backward compatibility, retains imports and a ``get_parser()`` that
forwards to :mod:`okf.plugin`.
"""

# Retained for backward compat — external code may import these directly.
from okf.parsers.c import CParser  # noqa: F401
from okf.parsers.cpp import CppParser  # noqa: F401
from okf.parsers.csharp import CSharpParser  # noqa: F401
from okf.parsers.dart import DartParser  # noqa: F401
from okf.parsers.go import GoParser  # noqa: F401
from okf.parsers.java import JavaParser  # noqa: F401
from okf.parsers.javascript import JSTSParser  # noqa: F401
from okf.parsers.julia import JuliaParser  # noqa: F401
from okf.parsers.kotlin import KotlinParser  # noqa: F401
from okf.parsers.php import PHPParser  # noqa: F401
from okf.parsers.python import PythonParser  # noqa: F401
from okf.parsers.ruby import RubyParser  # noqa: F401
from okf.parsers.rust import RustParser  # noqa: F401
from okf.parsers.scala import ScalaParser  # noqa: F401
from okf.parsers.sql import SQLParser  # noqa: F401
from okf.parsers.swift import SwiftParser  # noqa: F401

# Deprecated — kept for third-party code that imports EXTENSION_MAP.
# The plugin registry (okf.plugin.discover_parsers) is the canonical source.
EXTENSION_MAP: dict[str, type] = {}


def get_parser(ext: str):
    """Return a parser instance for *ext* via the plugin registry."""
    from okf.plugin import get_parser as _plugin_get
    return _plugin_get(ext)
