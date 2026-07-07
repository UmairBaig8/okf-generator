"""Plugin system — discovers parser and manifest plugins via Python entry points.

Parser plugins register in the ``okf.parsers`` group.
Manifest plugins register in the ``okf.manifests`` group.

Example ``pyproject.toml`` for a parser plugin::

    [project.entry-points."okf.parsers"]
    cobol = "okf_parser_cobol:Parser"

Example for a manifest plugin::

    [project.entry-points."okf.manifests"]
    pdm = "okf_manifest_pdm:Handler"
"""

import logging
from pathlib import Path
from typing import Any

from okf.parsers.base import Concept

log = logging.getLogger("okf_gen")

# ---------------------------------------------------------------------------
# ParserPlugin interface
# ---------------------------------------------------------------------------

class ParserPlugin:
    """Minimal interface a parser plugin must satisfy.

    Subclass and override ``parse_file``. Set ``LANGUAGE`` and ``EXTENSIONS``
    as class attributes.
    """
    LANGUAGE: str = "unknown"
    EXTENSIONS: set[str] = set()

    def parse_file(self, path: Path, repo_root: Path) -> list[Concept]:
        raise NotImplementedError

    def collect_imports(self, root_node: Any, source_bytes: bytes) -> list[str]:
        return []

    def collect_calls(self, root_node: Any, source_bytes: bytes) -> list[str]:
        return []


# ---------------------------------------------------------------------------
# ManifestPlugin interface
# ---------------------------------------------------------------------------

class ManifestPlugin:
    """Interface for a manifest handler plugin.

    Set ``MANIFEST_FILES`` to the list of filenames this handler recognises.
    The ``parse`` method receives the file path and repo root and returns
    a list of raw dependency dicts (same shape as ``manifest_scanner.py``
    handlers).
    """
    MANIFEST_FILES: list[str] = []

    def parse(self, path: Path, repo_root: Path) -> list[dict[str, Any]]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Built-in parser entry points
# ---------------------------------------------------------------------------

_BUILTIN_PARSERS: dict[str, str] = {
    "python":     "okf.parsers.python:PythonParser",
    "javascript": "okf.parsers.javascript:JSTSParser",
    "go":         "okf.parsers.go:GoParser",
    "java":       "okf.parsers.java:JavaParser",
    "rust":       "okf.parsers.rust:RustParser",
    "ruby":       "okf.parsers.ruby:RubyParser",
    "c":          "okf.parsers.c:CParser",
    "cpp":        "okf.parsers.cpp:CppParser",
    "csharp":     "okf.parsers.csharp:CSharpParser",
    "sql":        "okf.parsers.sql:SQLParser",
    "swift":      "okf.parsers.swift:SwiftParser",
    "kotlin":     "okf.parsers.kotlin:KotlinParser",
    "php":        "okf.parsers.php:PHPParser",
    "dart":       "okf.parsers.dart:DartParser",
    "scala":      "okf.parsers.scala:ScalaParser",
    "julia":      "okf.parsers.julia:JuliaParser",
}


# ---------------------------------------------------------------------------
# Built-in manifest entry points
# ---------------------------------------------------------------------------

_BUILTIN_MANIFESTS: dict[str, str] = {
    "requirements.txt":  "okf.manifest_scanner:parse_requirements_txt",
    "pyproject.toml":    "okf.manifest_scanner:parse_pyproject_toml",
    "package.json":      "okf.manifest_scanner:parse_package_json",
    "Cargo.toml":        "okf.manifest_scanner:parse_cargo_toml",
    "Cargo.lock":        "okf.manifest_scanner:parse_cargo_lock",
    "yarn.lock":         "okf.manifest_scanner:parse_yarn_lock",
    "pnpm-lock.yaml":    "okf.manifest_scanner:parse_pnpm_lock",
    "go.mod":            "okf.manifest_scanner:parse_go_mod",
    "go.sum":            "okf.manifest_scanner:parse_go_sum",
    "poetry.lock":       "okf.manifest_scanner:parse_poetry_lock",
    "composer.json":     "okf.manifest_scanner:parse_composer_json",
    "pom.xml":           "okf.manifest_scanner:parse_pom_xml",
    "Gemfile":           "okf.manifest_scanner:parse_gemfile",
    "build.gradle":      "okf.manifest_scanner:parse_build_gradle",
    "build.gradle.kts":  "okf.manifest_scanner:parse_build_gradle",
    "Package.swift":     "okf.manifest_scanner:parse_package_swift",
    "project.clj":       "okf.manifest_scanner:parse_project_clj",
    "mix.exs":           "okf.manifest_scanner:parse_mix_exs",
    "Dockerfile":        "okf.manifest_scanner:parse_dockerfile",
    "Containerfile":     "okf.manifest_scanner:parse_dockerfile",
    "docker-compose.yml": "okf.manifest_scanner:parse_docker_compose",
    "docker-compose.yaml": "okf.manifest_scanner:parse_docker_compose",
}


# ---------------------------------------------------------------------------
# Registry (cached singleton)
# ---------------------------------------------------------------------------

_registry: dict[str, type[ParserPlugin]] | None = None
_manifest_registry: dict[str, str] | None = None
_errors: list[str] = []


def discover_parsers() -> dict[str, type[ParserPlugin]]:
    """Discover all parsers (built-in + external plugins) and return
    ``{extension: parser_class}`` mapping.

    External plugins are discovered via ``importlib.metadata.entry_points``
    (group ``okf.parsers``).  Built-in parsers are registered internally.

    The result is cached after first call.
    """
    global _registry, _errors
    if _registry is not None:
        return _registry

    _errors = []
    ext_map: dict[str, type[ParserPlugin]] = {}

    def _load_all(namespace: str, source: str):
        for name, dotted_path in source.items():
            try:
                mod_path, cls_name = dotted_path.rsplit(":", 1)
                import importlib
                mod = importlib.import_module(mod_path)
                cls: type[ParserPlugin] = getattr(mod, cls_name)
                for ext in cls.EXTENSIONS:
                    ext_map[ext] = cls
            except Exception as e:
                _errors.append(f"{namespace}/{name}: {e}")
                log.debug(f"Failed to load parser {namespace}/{name}: {e}")

    # 1. Load built-in parsers
    _load_all("builtin", _BUILTIN_PARSERS)

    # 2. Load external plugins via entry points
    _load_entry_points("okf.parsers", "plugin", ext_map, lambda cls: [(ext, cls) for ext in cls.EXTENSIONS])

    _registry = ext_map
    return _registry


def discover_manifests() -> dict[str, str]:
    """Discover manifest handlers and return ``{filename: handler_function_path}``.

    External manifest plugins are discovered via ``importlib.metadata.entry_points``
    (group ``okf.manifests``).
    """
    global _manifest_registry
    if _manifest_registry is not None:
        return _manifest_registry

    result: dict[str, str] = {}

    # 1. Load built-in manifests
    for name, dotted_path in _BUILTIN_MANIFESTS.items():
        result[name] = dotted_path

    # 2. Load external manifest plugins via entry points
    def _on_load(cls):
        if hasattr(cls, "MANIFEST_FILES"):
            return [(f, f"{cls.__module__}:{cls.__qualname__}") for f in cls.MANIFEST_FILES]
        return []

    _load_entry_points("okf.manifests", "manifest", result, _on_load)

    _manifest_registry = result
    return result


def _load_entry_points(group: str, namespace: str, target: dict, expand_fn) -> None:
    """Load entry points from *group* into *target* using *expand_fn* to
    produce ``(key, value)`` pairs from each loaded class."""
    global _errors
    try:
        from importlib.metadata import entry_points
        for ep in entry_points(group=group):
            try:
                cls = ep.load()
                for k, v in expand_fn(cls):
                    target[k] = v
            except Exception as e:
                _errors.append(f"{namespace}/{ep.name}: {e}")
                log.warning(f"Failed to load {namespace} {ep.name}: {e}")
    except Exception as e:
        log.debug(f"Entry point discovery for {group} failed: {e}")


def get_parser(ext: str) -> ParserPlugin | None:
    """Return a parser instance for *ext* (e.g. ``.py``), or ``None``."""
    import okf.parsers.javascript as jsts
    registry = discover_parsers()
    cls = registry.get(ext)
    if cls is None:
        return None
    from okf.parsers.javascript import JSTSParser
    if cls is JSTSParser and ext in {".ts", ".tsx"}:
        p = cls()
        p._path_ext = ext
        return p
    return cls()


def plugin_errors() -> list[str]:
    """Return list of load errors from last discovery."""
    return list(_errors)


def list_plugins() -> dict:
    """Return a dict with ``parsers`` and ``manifests`` lists."""
    parsers = discover_parsers()
    manifests = discover_manifests()

    seen_parsers: dict[str, dict] = {}
    for ext, cls in parsers.items():
        lang = getattr(cls, "LANGUAGE", "unknown")
        if lang not in seen_parsers:
            seen_parsers[lang] = {
                "language": lang,
                "extensions": set(),
                "class": f"{cls.__module__}.{cls.__qualname__}",
            }
        seen_parsers[lang]["extensions"].add(ext)

    parser_list = sorted(seen_parsers.values(), key=lambda x: x["language"])
    for r in parser_list:
        r["extensions"] = sorted(r["extensions"])

    manifest_list = sorted(
        [{"file": k, "handler": v} for k, v in manifests.items()],
        key=lambda x: x["file"],
    )

    return {"parsers": parser_list, "manifests": manifest_list}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cli():
    """``okf plugin`` subcommand entry point."""
    import sys
    args = sys.argv[1:]  # ["okf plugin", "list", ...] → take from index 1

    if not args or args[0] in {"-h", "--help"}:
        print(__doc__)
        return

    cmd = args[0]

    if cmd == "list":
        data = list_plugins()
        errors = plugin_errors()
        parsers = data["parsers"]
        manifests = data["manifests"]

        print(f"\n  Parsers ({len(parsers)} languages, {len(discover_parsers())} extensions):\n")
        for p in parsers:
            exts = ", ".join(p["extensions"])
            print(f"    {p['language']:15s} [{exts}]")

        print(f"\n  Manifests ({len(manifests)} files):\n")
        for m in manifests:
            print(f"    {m['file']:25s} → {m['handler']}")

        if errors:
            print(f"\n  Errors ({len(errors)}):")
            for e in errors:
                print(f"    ! {e}")
        print()

    elif cmd == "install":
        if len(args) < 2:
            print("Usage: okf plugin install <package_name>")
            return
        pkg = args[1]
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", pkg],
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Install failed:\n{result.stderr}")
            return
        print(f"Installed {pkg}")
        # Verify the plugin loads
        _reset_registry()
        try:
            discover_parsers()
            errors = plugin_errors()
            if errors:
                print(f"Plugin loaded with {len(errors)} error(s):")
                for e in errors:
                    print(f"  ! {e}")
            else:
                print("Plugin registered successfully.")
        except Exception as e:
            print(f"Plugin load failed: {e}")

    elif cmd == "uninstall":
        if len(args) < 2:
            print("Usage: okf plugin uninstall <package_name>")
            return
        pkg = args[1]
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", pkg],
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Uninstall failed:\n{result.stderr}")
            return
        print(f"Uninstalled {pkg}")
        _reset_registry()

    else:
        print(f"Unknown plugin command: {cmd!r}")
        print("Available: list, install, uninstall")


def _reset_registry():
    """Force re-discovery on next call (used after install/uninstall)."""
    global _registry, _errors
    _registry = None
    _errors = []
