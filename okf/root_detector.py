"""Project root detection — walk up the directory tree to find the project root.

Supports all languages by checking for common project marker files.
Falls back to `.git/` directory as the universal marker.
"""

import os
from pathlib import Path

# Priority-ordered list of marker files that signal a project root.
# `.git` is checked separately (it's a directory, not a file).
PROJECT_MARKERS: list[str] = [
    "pyproject.toml",        # Python
    "Cargo.toml",            # Rust
    "package.json",          # Node / JavaScript / TypeScript
    "go.mod",                # Go
    "pom.xml",               # Java / Maven
    "build.gradle.kts",      # Kotlin / Gradle
    "build.gradle",          # Java / Gradle
    "Gemfile",               # Ruby
    "composer.json",         # PHP
    "Package.swift",         # Swift
    "deps.edn",              # Clojure
    "mix.exs",               # Elixir
    "project.clj",           # Clojure / Leiningen
    "rebar.config",          # Erlang
    "CMakeLists.txt",        # C / C++
    "BUILD.bazel",           # Bazel
    "BUILD",                 # Bazel / generic build
    "setup.py",              # Python (legacy)
    "Pipfile",               # Python (legacy)
    "Cargo.toml",            # Rust
    "*.csproj",              # C# (checked at directory level)
    ".sln",                  # C# solution
]


def detect_root(start: Path | None = None, max_depth: int = 10) -> Path:
    """Walk up from `start` (default: cwd) to find the project root.

    Checks for language-specific markers first, then falls back to `.git/`.
    Returns the first directory that contains a marker, or `start` if none found.

    Args:
        start: Directory to start searching from (default: current working directory).
        max_depth: Maximum number of parent directories to traverse.

    Returns:
        Absolute path to the detected project root.
    """
    if start is None:
        start = Path.cwd()
    start = start.resolve()

    current = start
    for _ in range(max_depth):
        # Check language-specific marker files
        for marker in PROJECT_MARKERS:
            if marker.startswith("*."):
                # Glob pattern (e.g., *.csproj) — check directory contents
                ext = marker[1:]
                try:
                    for f in current.iterdir():
                        if f.suffix == ext:
                            return current
                except PermissionError:
                    continue
            else:
                if (current / marker).exists():
                    return current

        # Check for .git directory (universal)
        if (current / ".git").is_dir():
            return current

        # Stop at filesystem root
        parent = current.parent
        if parent == current:
            break
        current = parent

    return start
