"""
okf/manifest_scanner.py

Extracts dependency/build-manifest concepts (type: Dependency) from
known manifest files, parallel to the existing AST/tree-sitter code
scanners. Zero external deps for the first pass (requirements.txt,
pyproject.toml, package.json) — stdlib only.

Design notes:
- Each dependency becomes ONE concept dict, same shape as functions/
  classes/modules emitted by okf_generator.py's AST scanners, so it
  flows through write_bundle() / okf_lookup.py / okf_to_pairs.py
  unmodified.
- Concept "type" is "Dependency" (new value alongside Function/Class/
  Module).
- Concept ID convention: f"{ecosystem}:{name}" to avoid collisions
  between e.g. a pip package and an npm package with the same name.
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[no-redef]


# Filenames this scanner knows how to handle. Extend this dict as new
# manifest types are added (Gemfile, build.gradle, Package.swift, ...).
MANIFEST_HANDLERS: dict[str, str] = {
    "requirements.txt": "parse_requirements_txt",
    "pyproject.toml": "parse_pyproject_toml",
    "package.json": "parse_package_json",
    "Cargo.toml": "parse_cargo_toml",
    "Cargo.lock": "parse_cargo_lock",
    "yarn.lock": "parse_yarn_lock",
    "pnpm-lock.yaml": "parse_pnpm_lock",
    "go.mod": "parse_go_mod",
    "go.sum": "parse_go_sum",
    "poetry.lock": "parse_poetry_lock",
    "composer.json": "parse_composer_json",
    "pom.xml": "parse_pom_xml",
    "Gemfile": "parse_gemfile",
    "build.gradle": "parse_build_gradle",
    "build.gradle.kts": "parse_build_gradle",
    "Package.swift": "parse_package_swift",
    "project.clj": "parse_project_clj",
    "mix.exs": "parse_mix_exs",
}


def is_manifest_file(path: Path) -> bool:
    return path.name in MANIFEST_HANDLERS


def scan_manifest(path: Path, repo_root: Path) -> list[dict[str, Any]]:
    """Dispatch to the right parser and return Dependency concept dicts.
    Caller converts to Concept objects to avoid circular imports."""
    handler_name = MANIFEST_HANDLERS.get(path.name)
    if handler_name is None:
        return []
    handler = globals()[handler_name]
    raw_deps = handler(path)

    resource = str(path.relative_to(repo_root))
    ts = _ts(path)
    return [_build_concept(dep, resource, ts) for dep in raw_deps]


def _ts(path: Path) -> str:
    """ISO-8601 timestamp from file mtime."""
    import datetime
    mtime = path.stat().st_mtime
    return datetime.datetime.fromtimestamp(mtime, tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_concept(dep: dict[str, Any], resource: str, ts: str) -> dict[str, Any]:
    name = dep["name"]
    ecosystem = dep["ecosystem"]
    version = dep.get("version", "")
    dev = dep.get("dev", False)

    cid = f"_dependencies/{ecosystem}/{name}"
    description = f"{'Dev dependency' if dev else 'Dependency'} from {resource}"

    return {
        "type": "Dependency",
        "title": name,
        "description": description,
        "resource": resource,
        "tags": [
            f"ecosystem:{ecosystem}",
            "type:Dependency",
            f"manifest:{Path(resource).name}",
            *([f"version:{version}"] if version else []),
        ],
        "timestamp": ts,
        "concept_id": cid,
        "body_extra": {
            "ecosystem": ecosystem,
            "version_constraint": version,
            "dev_dependency": dev,
            "source_manifest": resource,
        },
    }


# ---------------------------------------------------------------------
# Per-format parsers. Each returns list[{"name", "ecosystem", "version",
# "dev"}].
# ---------------------------------------------------------------------

_REQ_LINE_RE = re.compile(
    r"^\s*([A-Za-z0-9_.\-]+)\s*(?P<spec>[=<>!~]=?[A-Za-z0-9_.\-,*]*)?\s*(?:#.*)?$"
)


def parse_requirements_txt(path: Path) -> list[dict[str, Any]]:
    deps = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue  # skip blank lines, comments, -r/-e/--index-url flags
        m = _REQ_LINE_RE.match(line)
        if not m:
            continue
        name = m.group(1)
        spec = m.group("spec") or ""
        deps.append({"name": name, "ecosystem": "pip", "version": spec, "dev": False})
    return deps


def parse_pyproject_toml(path: Path) -> list[dict[str, Any]]:
    data = tomllib.loads(path.read_text(encoding="utf-8", errors="ignore"))
    deps = []

    # PEP 621 standard deps
    project = data.get("project", {})
    for entry in project.get("dependencies", []):
        name, version = _split_pep508(entry)
        deps.append({"name": name, "ecosystem": "pip", "version": version, "dev": False})

    # PEP 621 optional / dev groups
    for group, entries in project.get("optional-dependencies", {}).items():
        for entry in entries:
            name, version = _split_pep508(entry)
            deps.append({"name": name, "ecosystem": "pip", "version": version, "dev": True})

    # Poetry-style (legacy but still common)
    poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    for name, spec in poetry_deps.items():
        if name.lower() == "python":
            continue
        version = spec if isinstance(spec, str) else spec.get("version", "")
        deps.append({"name": name, "ecosystem": "pip", "version": version, "dev": False})

    return deps


def _split_pep508(entry: str) -> tuple[str, str]:
    m = re.match(r"^([A-Za-z0-9_.\-]+)\s*(.*)$", entry.strip())
    if not m:
        return entry, ""
    return m.group(1), m.group(2)


def parse_package_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    deps = []
    for name, version in data.get("dependencies", {}).items():
        deps.append({"name": name, "ecosystem": "npm", "version": version, "dev": False})
    for name, version in data.get("devDependencies", {}).items():
        deps.append({"name": name, "ecosystem": "npm", "version": version, "dev": True})
    return deps


def parse_cargo_toml(path: Path) -> list[dict[str, Any]]:
    """Rust. [dependencies] / [dev-dependencies] / [build-dependencies].
    Values may be a plain version string or an inline table
    {version="1.0", features=[...]}."""
    data = tomllib.loads(path.read_text(encoding="utf-8", errors="ignore"))
    deps = []

    def _collect(table_name: str, dev: bool) -> None:
        for name, spec in data.get(table_name, {}).items():
            if isinstance(spec, str):
                version = spec
            elif isinstance(spec, dict):
                version = spec.get("version", "")
            else:
                version = ""
            deps.append({"name": name, "ecosystem": "cargo", "version": version, "dev": dev})

    _collect("dependencies", dev=False)
    _collect("dev-dependencies", dev=True)
    _collect("build-dependencies", dev=True)
    return deps


_GO_REQUIRE_LINE_RE = re.compile(r"^\s*([^\s]+)\s+(v[^\s]+)")


def parse_go_mod(path: Path) -> list[dict[str, Any]]:
    """Go. Handles both single-line `require module v1.2.3` and
    block form `require (\n  module v1.2.3\n)`. Marks `// indirect`
    deps as dev=True since they aren't direct project dependencies."""
    deps = []
    in_require_block = False
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("require ("):
            in_require_block = True
            continue
        if in_require_block and line == ")":
            in_require_block = False
            continue

        target = None
        if in_require_block:
            target = line
        elif line.startswith("require "):
            target = line[len("require "):]
        else:
            continue

        is_indirect = "// indirect" in target
        target = target.split("//")[0].strip()
        m = _GO_REQUIRE_LINE_RE.match(target)
        if not m:
            continue
        name, version = m.group(1), m.group(2)
        deps.append({"name": name, "ecosystem": "go", "version": version, "dev": is_indirect})
    return deps


def parse_composer_json(path: Path) -> list[dict[str, Any]]:
    """PHP. Same shape as package.json: require / require-dev.
    Skips the synthetic "php" platform entry."""
    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    deps = []
    for name, version in data.get("require", {}).items():
        if name.lower() == "php" or name.startswith("ext-"):
            continue
        deps.append({"name": name, "ecosystem": "composer", "version": version, "dev": False})
    for name, version in data.get("require-dev", {}).items():
        deps.append({"name": name, "ecosystem": "composer", "version": version, "dev": True})
    return deps


def parse_pom_xml(path: Path) -> list[dict[str, Any]]:
    """Java/Maven. Reads <dependencies><dependency> entries.
    Name is rendered as groupId:artifactId since artifactId alone
    often collides across libraries. Namespace-agnostic via local-name
    matching since pom.xml typically declares a default xmlns."""
    tree = ET.parse(path)
    root = tree.getroot()

    def local(tag: str) -> str:
        return tag.split("}")[-1] if "}" in tag else tag

    deps = []
    for dep_el in root.iter():
        if local(dep_el.tag) != "dependency":
            continue
        group_id = artifact_id = version = scope = ""
        for child in dep_el:
            tag = local(child.tag)
            if tag == "groupId":
                group_id = (child.text or "").strip()
            elif tag == "artifactId":
                artifact_id = (child.text or "").strip()
            elif tag == "version":
                version = (child.text or "").strip()
            elif tag == "scope":
                scope = (child.text or "").strip()
        if not artifact_id:
            continue
        name = f"{group_id}:{artifact_id}" if group_id else artifact_id
        dev = scope in ("test", "provided")
        deps.append({"name": name, "ecosystem": "maven", "version": version, "dev": dev})
    return deps


# ---------------------------------------------------------------------
# DSL-source manifests. These embed dependency declarations inside
# executable source (Ruby/Groovy/Kotlin/Swift/Clojure/Elixir), so we
# can't use a structured parser — regex against the relevant block is
# the pragmatic approach. Each is intentionally conservative: it's
# fine to miss exotic/dynamic declarations, but should not crash on
# them.
# ---------------------------------------------------------------------

_GEM_LINE_RE = re.compile(
    r'^\s*gem\s+["\']([^"\']+)["\']'              # gem "name"
    r'(?:\s*,\s*["\']([^"\']+)["\'])?'             # optional , "version"
)


def parse_gemfile(path: Path) -> list[dict[str, Any]]:
    """Ruby. Tracks `group :test do ... end` / `group :development do`
    blocks to mark contained gems as dev=True. Ignores non-gem lines
    (source, ruby version pragma, etc.)."""
    deps = []
    dev_depth = 0
    depth = 0
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        group_start = re.match(r'^group\s*\(?\s*:(\w+)', line)
        if group_start and "do" in line:
            depth += 1
            if group_start.group(1) in ("test", "development"):
                dev_depth = depth
            continue
        if line == "end":
            if depth == dev_depth:
                dev_depth = 0
            depth = max(0, depth - 1)
            continue

        m = _GEM_LINE_RE.match(line)
        if not m:
            continue
        name, version = m.group(1), m.group(2) or ""
        deps.append({"name": name, "ecosystem": "rubygems", "version": version, "dev": dev_depth > 0})
    return deps


# Matches both Groovy ("group:artifact:version") and Kotlin DSL
# implementation("group:artifact:version") forms.
_GRADLE_DEP_RE = re.compile(
    r'\b(implementation|api|compile|testImplementation|androidTestImplementation|'
    r'runtimeOnly|compileOnly|kapt|annotationProcessor)\s*[\(\s]\s*'
    r'["\']([\w.\-]+):([\w.\-]+):([\w.\-+]+)["\']'
)

_GRADLE_DEV_CONFIGS = {"testImplementation", "androidTestImplementation", "kapt", "annotationProcessor"}


def parse_build_gradle(path: Path) -> list[dict[str, Any]]:
    """Gradle (Groovy or Kotlin DSL). Only matches the common
    `configuration "group:artifact:version"` string-notation form;
    does not resolve version catalogs (libs.versions.toml) or
    dynamically-built coordinates."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    deps = []
    for m in _GRADLE_DEP_RE.finditer(text):
        config, group, artifact, version = m.groups()
        name = f"{group}:{artifact}"
        deps.append({
            "name": name,
            "ecosystem": "gradle",
            "version": version,
            "dev": config in _GRADLE_DEV_CONFIGS,
        })
    return deps


_SWIFT_PKG_RE = re.compile(
    r'\.package\(\s*(?:name:\s*["\']([^"\']+)["\']\s*,\s*)?'
    r'url:\s*["\']([^"\']+)["\']\s*,\s*'
    r'(?:from:\s*["\']([^"\']+)["\']|exact:\s*["\']([^"\']+)["\']|\.upToNextMajor\(from:\s*["\']([^"\']+)["\']\))'
)


def parse_package_swift(path: Path) -> list[dict[str, Any]]:
    """Swift Package Manager. Extracts the repo name from the URL as
    the dependency name (SwiftPM has no separate package name field
    in most .package() declarations). Version is whichever of
    from/exact/upToNextMajor was used."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    deps = []
    for m in _SWIFT_PKG_RE.finditer(text):
        explicit_name, url, v_from, v_exact, v_upto = m.groups()
        version = v_from or v_exact or v_upto or ""
        name = explicit_name or url.rstrip("/").rsplit("/", 1)[-1].removesuffix(".git")
        deps.append({"name": name, "ecosystem": "swiftpm", "version": version, "dev": False})
    return deps


_CLOJURE_DEP_RE = re.compile(r'\[\s*([\w.\-]+/[\w.\-]+|[\w.\-]+)\s+"([^"]+)"\s*\]')


def parse_project_clj(path: Path) -> list[dict[str, Any]]:
    """Clojure/Leiningen. Pulls the vector immediately following
    :dependencies (and :profiles {:dev/:test ... :dependencies [...]}
    treated as dev). This is a regex approximation of an s-expression
    parser — good enough for the common, non-nested-reader-macro case."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    deps = []

    def _extract_block(after_key: str) -> str | None:
        idx = text.find(after_key)
        if idx == -1:
            return None
        start = text.find("[", idx)
        if start == -1:
            return None
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "[":
                depth += 1
            elif text[i] == "]":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        return None

    main_block = _extract_block(":dependencies")
    if main_block:
        for m in _CLOJURE_DEP_RE.finditer(main_block):
            name, version = m.groups()
            deps.append({"name": name, "ecosystem": "clojars", "version": version, "dev": False})

    # :profiles {:dev {:dependencies [...]}} — best-effort: scan any
    # :dependencies block that appears after a :dev or :test profile key.
    for profile_key in (":dev", ":test"):
        p_idx = text.find(profile_key)
        if p_idx == -1:
            continue
        dep_idx = text.find(":dependencies", p_idx)
        if dep_idx == -1:
            continue
        start = text.find("[", dep_idx)
        if start == -1:
            continue
        depth = 0
        block = None
        for i in range(start, len(text)):
            if text[i] == "[":
                depth += 1
            elif text[i] == "]":
                depth -= 1
                if depth == 0:
                    block = text[start:i + 1]
                    break
        if block:
            for m in _CLOJURE_DEP_RE.finditer(block):
                name, version = m.groups()
                deps.append({"name": name, "ecosystem": "clojars", "version": version, "dev": True})
    return deps


_ELIXIR_DEP_RE = re.compile(
    r'\{\s*:(\w+)\s*,\s*"([^"]+)"(?:\s*,\s*([^}]*))?\}'
)


def parse_cargo_lock(path: Path) -> list[dict[str, Any]]:
    """Rust/Cargo lockfile. [[package]] entries with name + version."""
    data = tomllib.loads(path.read_text(encoding="utf-8", errors="ignore"))
    deps = []
    for pkg in data.get("package", []):
        name = pkg.get("name", "")
        version = pkg.get("version", "")
        if name:
            deps.append({"name": name, "ecosystem": "cargo", "version": version, "dev": False})
    return deps


def parse_poetry_lock(path: Path) -> list[dict[str, Any]]:
    """Python/Poetry lockfile. [[package]] entries with name + version."""
    data = tomllib.loads(path.read_text(encoding="utf-8", errors="ignore"))
    deps = []
    for pkg in data.get("package", []):
        name = pkg.get("name", "")
        version = pkg.get("version", "")
        category = pkg.get("category", "")
        if name:
            deps.append({"name": name, "ecosystem": "pip", "version": version, "dev": category == "dev"})
    return deps


_GO_SUM_LINE_RE = re.compile(r"^(\S+)\s+(v\S+)\s+h1:")


def parse_go_sum(path: Path) -> list[dict[str, Any]]:
    """Go module checksum file. Skips /go.mod entries (go.mod checksums)."""
    deps = []
    seen = set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "/go.mod" in line:
            continue
        m = _GO_SUM_LINE_RE.match(line)
        if not m:
            continue
        key = m.group(1) + "@" + m.group(2)
        if key in seen:
            continue
        seen.add(key)
        deps.append({"name": m.group(1), "ecosystem": "go", "version": m.group(2), "dev": False})
    return deps


_YARN_LINE_RE = re.compile(r'^  version "([^"]+)"')


def parse_yarn_lock(path: Path) -> list[dict[str, Any]]:
    """Yarn lockfile (v1). Extracts package@version → name, version."""
    deps = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith('"') or (line and line[0].isalpha()):
            # package line: "package@version: or package@version:
            name_ver = line.strip().rstrip(":").strip('"')
            if "@" in name_ver and not name_ver.startswith("#"):
                at_idx = name_ver.rindex("@")
                name = name_ver[:at_idx]
                dep_key = name_ver
                deps.append({"name": name, "ecosystem": "npm", "version": "", "dev": False, "_key": dep_key})
        elif "  version " in line and deps:
            m = _YARN_LINE_RE.match(line)
            if m:
                deps[-1]["version"] = m.group(1)
    # Remove duplicates (same name, keep first occurrence)
    seen = set()
    result = []
    for d in deps:
        key = d["_key"]
        if key not in seen:
            seen.add(key)
            d.pop("_key")
            result.append(d)
    return result


def parse_pnpm_lock(path: Path) -> list[dict[str, Any]]:
    """pnpm lockfile (YAML). Extracts top-level package entries."""
    import yaml
    data = yaml.safe_load(path.read_text(encoding="utf-8", errors="ignore"))
    deps = []
    packages = data.get("packages", {}) if isinstance(data, dict) else {}
    for specifier, info in packages.items():
        # specifier looks like "/package-name@version" or "package-name@version"
        name_ver = specifier.lstrip("/")
        if "@" not in name_ver:
            continue
        at_idx = name_ver.rindex("@")
        name = name_ver[:at_idx]
        version = name_ver[at_idx + 1:]
        if info and isinstance(info, dict):
            dev = info.get("dev", False)
        else:
            dev = False
        deps.append({"name": name, "ecosystem": "npm", "version": version, "dev": dev})
    return deps


def parse_mix_exs(path: Path) -> list[dict[str, Any]]:
    """Elixir/Mix. Extracts the list inside `defp deps do [ ... ] end`.
    Marks a dep dev=True if its trailing options mention `only: :test`
    or `only: :dev`."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    deps = []

    m_fn = re.search(r"defp\s+deps\s+do(.*?)\n\s*end", text, re.DOTALL)
    if not m_fn:
        return deps
    body = m_fn.group(1)

    for m in _ELIXIR_DEP_RE.finditer(body):
        name, version, opts = m.groups()
        opts = opts or ""
        dev = bool(re.search(r":(dev|test)", opts))
        deps.append({"name": name, "ecosystem": "hex", "version": version, "dev": dev})
    return deps
