"""Generate an OKF (Open Knowledge Format) bundle from a codebase.

Walks a source directory and produces a conformant OKF v0.1 bundle whose
layout mirrors the source tree exactly (domain/resource-based), e.g.:

  <output>/
  ├── index.md                          # bundle root — lists top-level dirs
  ├── log.md                            # generation history
  │
  ├── StockAI/
  │   ├── index.md                      # lists subdirs + concepts
  │   └── RnD/
  │       └── python/
  │           └── connectors/
  │               ├── index.md          # lists all concepts in this folder
  │               ├── economic_data.md  # Module concept (one per source file)
  │               └── economic_data/
  │                   ├── WorldBankConnector.md  # Class concept
  │                   ├── get_indicator.md       # Function concept
  │                   └── search.md              # Function concept
  └── ...

Every directory gets an index.md listing its subdirectories and concepts
grouped by type (Module / Class / Function). This makes the bundle
navigable by domain, just like the original codebase.

Concept frontmatter (OKF v0.1 conformant):
  type         REQUIRED — Module | Function | Class | Method
  title        display name
  description  one-line summary (from docstring or LLM enrichment)
  resource     relative source file path
  tags         language, module name, etc.
  timestamp    ISO-8601 last-modified time of the source file

Supported languages:
  Python       full AST — functions, classes, params, return types, docstrings
  JS/TS/Go/Java/Rust/Ruby  tree-sitter — functions, classes, methods, doc comments
  SQL          dialect-tolerant regex — tables, views, functions/procedures, indexes

Config via env vars:
  OKF_API_KEY      API key for LLM enrichment
  OKF_BASE_URL     API base URL (default: http://localhost:8080/v1 — works with llama.cpp, Ollama, vLLM)
  OKF_MODEL        model name (default: local-model)
  OKF_ENRICH=1     enable LLM enrichment of descriptions + docstrings
  OKF_MAX_WORKERS  parallel enrichment workers (default: 2)
  LOG_LEVEL        default: INFO

Usage:
  python okf_generator.py <source_dir> [output_dir]

  source_dir   root of the codebase to scan
  output_dir   where to write the OKF bundle (default: ./okf_bundle)
"""

import json
import logging
import os
import re
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import yaml  # PyYAML
from tqdm import tqdm

from okf import manifest_scanner
from okf.parsers import get_parser
from okf.parsers.base import Concept, SKIP_DIRS, SKIP_DIR_SUFFIXES

log = logging.getLogger("okf_gen")

def _git_info(repo_root: Path) -> dict:
    """Get git metadata for tagging. Returns empty dict if not a git repo."""
    info = {}
    try:
        branch = subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL, timeout=3
        ).decode().strip()
        info["branch"] = branch

        remote = subprocess.check_output(
            ["git", "-C", str(repo_root), "remote", "get-url", "origin"],
            stderr=subprocess.DEVNULL, timeout=3
        ).decode().strip()
        # extract repo name from remote URL
        repo_name = re.sub(r".*[:/](.+?)(\.git)?$", r"\1", remote)
        info["repo"] = repo_name
    except Exception:
        pass
    return info


def _make_tags(language: str, resource: str, concept_type: str, git: dict) -> list[str]:
    """Build standardised OKF tags for a concept.

    Tag categories (order is intentional — most stable first):
      lang:<language>        e.g. lang:python
      type:<ConceptType>     e.g. type:Function
      module:<top_dir>       e.g. module:StockAI  (top-level source folder)
      domain:<second_dir>    e.g. domain:RnD       (second-level folder)
      git:branch:<name>      e.g. git:branch:main
      git:repo:<name>        e.g. git:repo:TrainLLMs
    """
    tags = []
    tags.append(f"lang:{language}")
    tags.append(f"type:{concept_type}")

    # module + domain from resource path
    parts = resource.replace("\\", "/").replace(os.sep, "/").split("/")
    if parts:
        tags.append(f"module:{parts[0]}")
    if len(parts) > 1:
        tags.append(f"domain:{parts[1]}")

    if git.get("branch"):
        tags.append(f"git:branch:{git['branch']}")
    if git.get("repo"):
        tags.append(f"git:repo:{git['repo']}")

    return tags


def _dedup_concept_ids(concepts: list[Concept]) -> list[Concept]:
    seen: dict[str, int] = {}
    for c in concepts:
        base = c.concept_id
        if base in seen:
            seen[base] += 1
            c.concept_id = f"{base}_{seen[base]}"
        else:
            seen[base] = 0
    return concepts


# ---------------------------------------------------------------------------
# OKF document renderer
# ---------------------------------------------------------------------------

def _frontmatter(concept: Concept) -> str:
    fm: dict = {"type": concept.type}
    if concept.title:
        fm["title"] = concept.title
    if concept.description:
        fm["description"] = concept.description
    if concept.resource:
        fm["resource"] = concept.resource
    if concept.tags:
        fm["tags"] = concept.tags
    if concept.timestamp:
        fm["timestamp"] = concept.timestamp
    return "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True) + "---\n"


def _body(concept: Concept, all_concepts: dict[str, Concept]) -> str:
    lines = [f"# {concept.title}\n"]

    if concept.description:
        lines.append(f"{concept.description}\n")

    if concept.type == "Dependency" and concept.body_extra:
        be = concept.body_extra
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        lines.append(f"| Ecosystem | `{be.get('ecosystem', '')}` |")
        lines.append(f"| Version constraint | `{be.get('version_constraint', '')}` |")
        lines.append(f"| Source manifest | `{be.get('source_manifest', '')}` |")
        lines.append(f"| Dev dependency | `{'yes' if be.get('dev_dependency') else 'no'}` |")
        used_by = be.get("used_by") or []
        lines.append(f"| Used by | {len(used_by)} module(s) |")
        lines.append("")
        if used_by:
            lines.append("## Used By\n")
            for cid in used_by:
                rel_concept = all_concepts.get(cid)
                label = rel_concept.title if rel_concept else cid.split("/")[-1]
                lines.append(f"- [{label}](/{cid}.md)")
            lines.append("")
        return "\n".join(lines)

    if concept.signature:
        lines.append("## Signature\n")
        lang_fence = "python"
        for t in concept.tags:
            if t.startswith("lang:"):
                lang_fence = t.removeprefix("lang:")
                break
        sig = concept.signature
        # Strip existing markdown fences if concept already has them
        sig = re.sub(r"^```\w*\s*", "", sig)
        sig = re.sub(r"\s*```$", "", sig)
        lines.append(f"```{lang_fence}\n{sig.strip()}\n```\n")

    if concept.type_params:
        lines.append("## Type Parameters\n")
        for tp in concept.type_params:
            lines.append(f"- `{tp}`")
        lines.append("")

    if concept.inheritance:
        lines.append("## Inheritance\n")
        for base in concept.inheritance:
            lines.append(f"- `{base}`")
        lines.append("")

    if concept.decorators:
        lines.append("## Decorators\n")
        for d in concept.decorators:
            lines.append(f"- `{d}`")
        lines.append("")

    if concept.visibility:
        lines.append("## Visibility\n")
        for v in concept.visibility:
            lines.append(f"- `{v}`")
        lines.append("")

    if concept.fields:
        lines.append("## Fields\n")
        lines.append("| Name | Type | Visibility |")
        lines.append("|------|------|------------|")
        for f in concept.fields:
            lines.append(f"| `{f.get('name', '')}` | `{f.get('type', '')}` | `{f.get('visibility', '')}` |")
        lines.append("")

    if concept.docstring:
        lines.append("## Docstring\n")
        lines.append(f"{concept.docstring}\n")

    if concept.params:
        lines.append("## Parameters\n")
        lines.append("| Name | Type | Default |")
        lines.append("|------|------|---------|")
    for p in concept.params:
        name = p['name'].strip('`').strip()
        ann = (p['annotation'] or '—').strip('`').strip()
        default = (p['default'] or '—').strip('`').strip()
        lines.append(f"| `{name}` | `{ann}` | `{default}` |")
        lines.append("")

    if concept.returns:
        lines.append(f"## Returns\n`{concept.returns}`\n")

    if concept.design_pattern:
        lines.append(f"## Design Pattern\n{concept.design_pattern}\n")

    if concept.deprecation_notes:
        lines.append(f"## Deprecation\n{concept.deprecation_notes}\n")

    if concept.usage_example:
        lines.append(f"## Usage Example\n```\n{concept.usage_example}\n```\n")

    if concept.side_effects:
        lines.append(f"## Side Effects\n{concept.side_effects}\n")

    if concept.security:
        lines.append(
            "## Security \u26a0\ufe0f AI-estimated \u2014 verify manually, absence of a "
            f"flagged pattern is not proof of safety\n{concept.security}\n"
        )

    if concept.complexity:
        lines.append(f"## Complexity \u26a0\ufe0f AI-estimated \u2014 verify manually\n{concept.complexity}\n")

    if concept.methods:
        lines.append("## Methods\n")
        for m in concept.methods:
            lines.append(f"- `{m}`")
        lines.append("")

    if concept.source_lines and concept.source_lines[0]:
        start, end = concept.source_lines
        lines.append(f"## Source\nLines {start}–{end} in `{concept.resource}`\n")

    if concept.related:
        lines.append("## Related\n")
        for cid in concept.related:
            rel_concept = all_concepts.get(cid)
            if rel_concept:
                label = rel_concept.title
                # relative link: concept lives at concept_id + ".md" from bundle root
                lines.append(f"- [{label}](/{cid}.md)")
            else:
                # cid not found — may be stale; show as plain text
                label = cid.split("/")[-1]
                lines.append(f"- {label} *(unresolved)*")
        lines.append("")

    if concept.related_semantic:
        lines.append("## Related (AI-suggested)\n")
        for cid in concept.related_semantic:
            rel_concept = all_concepts.get(cid)
            label = rel_concept.title if rel_concept else cid.split("/")[-1]
            lines.append(f"- [{label}](/{cid}.md)")
        lines.append("")

    if concept.calls:
        lines.append("## Calls\n")
        for cid in concept.calls:
            rel_concept = all_concepts.get(cid)
            label = rel_concept.title if rel_concept else cid.split("/")[-1]
            lines.append(f"- [{label}](/{cid}.md)")
        lines.append("")

    if concept.called_by:
        lines.append("## Called By\n")
        for cid in concept.called_by:
            rel_concept = all_concepts.get(cid)
            label = rel_concept.title if rel_concept else cid.split("/")[-1]
            lines.append(f"- [{label}](/{cid}.md)")
        lines.append("")

    return "\n".join(lines)


def render_concept(concept: Concept, all_concepts: dict[str, Concept]) -> str:
    return _frontmatter(concept) + "\n" + _body(concept, all_concepts)


def render_dir_index(
    dir_path: str,
    subdirs: list[str],
    concepts: list["Concept"],
    bundle_name: str,
    all_map: dict[str, "Concept"],
) -> str:
    """Render index.md for a directory node in the resource tree."""
    title = dir_path.split("/")[-1] if dir_path else bundle_name
    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    fm = {
        "type": "Index",
        "title": title,
        "description": f"Knowledge index for {dir_path or bundle_name}",
        "resource": dir_path,
        "okf_version": "0.1" if not dir_path else None,
        "timestamp": ts,
    }
    # remove None values
    fm = {k: v for k, v in fm.items() if v is not None}

    lines = [
        "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True) + "---\n",
        f"# {title}\n",
    ]

    if subdirs:
        lines.append("## Subdirectories\n")
        for sd in sorted(subdirs):
            label = sd.split("/")[-1]
            lines.append(f"- [{label}]({label}/index.md)")
        lines.append("")

    if concepts:
        # group by type for readability
        by_type: dict[str, list] = {}
        for c in concepts:
            by_type.setdefault(c.type, []).append(c)

        def _plural(t: str) -> str:
            return "Dependencies" if t == "Dependency" else f"{t}s"

        for ctype in ("Module", "Class", "Function", "Method", "Constant", "Variable", "Dependency"):
            group = by_type.get(ctype, [])
            if not group:
                continue
            lines.append(f"## {_plural(ctype)}\n")
            for c in sorted(group, key=lambda x: x.title.lower()):
                filename = c.concept_id.split("/")[-1] + ".md"
                desc = f" — {c.description}" if c.description else ""
                lines.append(f"- [{c.title}]({filename}){desc}")
            lines.append("")

    return "\n".join(lines)


def render_root_index(bundle_name: str, top_dirs: list[str], total: int, ts: str, source_root: str = "") -> str:
    fm = {
        "type": "Index",
        "title": bundle_name,
        "description": f"OKF v0.1 bundle generated from the {bundle_name} codebase",
        "okf_version": "0.1",
        "timestamp": ts,
    }
    if source_root:
        fm["source_root"] = source_root
    lines = [
        "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True) + "---\n",
        f"# {bundle_name}\n",
        f"OKF v0.1 knowledge bundle — {total} concepts across {len(top_dirs)} top-level directories.\n",
        "## Top-level Directories\n",
    ]
    for d in sorted(top_dirs):
        lines.append(f"- [{d}]({d}/index.md)")
    lines.append("")
    return "\n".join(lines)


def render_log(entries: list[str]) -> str:
    fm = {
        "type": "Log",
        "title": "Change Log",
        "description": "Chronological history of bundle generation",
        "timestamp": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    lines = [
        "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True) + "---\n",
        "# Change Log\n",
    ]
    for e in entries:
        lines.append(f"- {e}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# SUMMARY.md generator
# ---------------------------------------------------------------------------

def render_summary(
    bundle_name: str,
    concepts: list[Concept],
    output_dir: Path,
    git: dict,
) -> str:
    """Generate a single SUMMARY.md — the top-level entry point for OpenCode.

    Groups concepts by top-level domain (first path segment of resource),
    then by module within each domain. Includes concept counts, descriptions,
    and direct links so an AI agent can navigate the whole bundle from one file.
    """
    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ── Separate dependencies from code concepts ──────────────────────────
    code_concepts = [c for c in concepts if c.type != "Dependency"]
    dep_concepts  = [c for c in concepts if c.type == "Dependency"]

    # ── Group by domain → module → concepts ──────────────────────────────
    # domain  = first path segment  (e.g. "StockAI")
    # module  = resource path without extension (e.g. "StockAI/RnD/python/connectors/economic_data")
    domains: dict[str, dict[str, list[Concept]]] = defaultdict(lambda: defaultdict(list))

    for c in code_concepts:
        parts = c.resource.replace("\\", "/").replace(os.sep, "/").split("/")
        domain = parts[0] if parts else "root"
        module = re.sub(r"\.[^/]+$", "", c.resource).replace(os.sep, "/")
        domains[domain][module].append(c)

    # ── Stats ─────────────────────────────────────────────────────────────
    total      = len(concepts)
    n_modules  = len({re.sub(r"\.[^/]+$", "", c.resource) for c in code_concepts})
    n_domains  = len(domains)
    by_type    = {}
    for c in concepts:
        by_type[c.type] = by_type.get(c.type, 0) + 1

    # ── Languages ─────────────────────────────────────────────────────────
    langs: dict[str, int] = {}
    for c in concepts:
        for tag in c.tags:
            if tag.startswith("lang:"):
                lang = tag[5:]
                langs[lang] = langs.get(lang, 0) + 1
                break

    # ── Frontmatter ───────────────────────────────────────────────────────
    fm: dict = {
        "type":        "Index",
        "title":       f"{bundle_name} — Knowledge Summary",
        "description": f"Top-level OKF summary: {total} concepts across {n_domains} domains and {n_modules} modules",
        "okf_version": "0.1",
        "timestamp":   ts,
    }
    if git.get("repo"):
        fm["git_repo"] = git["repo"]
    if git.get("branch"):
        fm["git_branch"] = git["branch"]

    lines = [
        "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True) + "---\n",
        f"# {bundle_name} — Knowledge Summary\n",
        f"> OKF v0.1 bundle | {total:,} concepts | {n_domains} domains | {n_modules} modules\n",
    ]

    # ── Quick stats table ─────────────────────────────────────────────────
    lines.append("## Stats\n")
    lines.append("| Type | Count |")
    lines.append("|------|-------|")
    for ctype, count in sorted(by_type.items(), key=lambda x: -x[1]):
        lines.append(f"| {ctype} | {count:,} |")
    if langs:
        lines.append("")
        lines.append("| Language | Concepts |")
        lines.append("|----------|----------|")
        for lang, count in sorted(langs.items(), key=lambda x: -x[1]):
            lines.append(f"| {lang} | {count:,} |")
    lines.append("")

    # ── Domain map ────────────────────────────────────────────────────────
    lines.append("## Domain Map\n")
    lines.append("Use these links to navigate the bundle or prime an AI agent with focused context.\n")

    for domain in sorted(domains.keys()):
        modules    = domains[domain]
        dom_total  = sum(len(v) for v in modules.values())
        dom_index  = f"{domain}/index.md"
        lines.append(f"### [{domain}]({dom_index}) — {dom_total:,} concepts\n")

        # show up to 8 modules per domain, sorted by concept count desc
        sorted_mods = sorted(modules.items(), key=lambda x: -len(x[1]))
        for mod_path, mod_concepts in sorted_mods[:8]:
            n          = len(mod_concepts)
            mod_index  = f"{mod_path.rstrip('/')}/index.md"  # not entirely accurate but navigable
            # pick the module concept for description
            mod_desc   = ""
            for mc in mod_concepts:
                if mc.type == "Module" and mc.description:
                    mod_desc = f" — {mc.description[:80]}"
                    break
            lines.append(f"- [{mod_path}]({mod_index}) ({n} concepts){mod_desc}")

        if len(sorted_mods) > 8:
            lines.append(f"- *…and {len(sorted_mods) - 8} more modules*")
        lines.append("")

    # ── Dependencies (compact ecosystem summary) ──────────────────────────
    if dep_concepts:
        lines.append("## Dependencies\n")
        lines.append("> Full list at [`_dependencies/index.md`](/_dependencies/index.md) or `okf lookup --type Dependency`\n")
        eco_count: dict[str, int] = {}
        for c in dep_concepts:
            eco = c.body_extra.get("ecosystem", "?")
            eco_count[eco] = eco_count.get(eco, 0) + 1
        lines.append("| Ecosystem | Packages |")
        lines.append("|----------|----------|")
        for eco, count in sorted(eco_count.items(), key=lambda x: -x[1]):
            lines.append(f"| {eco} | {count:,} |")
        lines.append("")

    # ── Key concepts (top 20 by description quality) ──────────────────────
    lines.append("## Key Concepts\n")
    lines.append("Highest-value concepts across all domains (Classes and Functions with rich descriptions).\n")

    key = [
        c for c in concepts
        if c.type in {"Class", "Function"} and len(c.description) > 40
    ]
    key_sorted = sorted(key, key=lambda c: -len(c.description))[:20]

    if key_sorted:
        lines.append("| Concept | Type | Module | Description |")
        lines.append("|---------|------|--------|-------------|")
        for c in key_sorted:
            link   = f"[{c.title}](/{c.concept_id}.md)"
            module = "/".join(c.resource.replace(os.sep, "/").split("/")[:3])
            desc   = c.description[:60] + ("…" if len(c.description) > 60 else "")
            lines.append(f"| {link} | {c.type} | `{module}` | {desc} |")
        lines.append("")

    # ── OpenCode usage hint ───────────────────────────────────────────────
    lines.append("## Usage with OpenCode\n")
    lines.append("```bash")
    lines.append("# Prime full context")
    lines.append("RUN cat ./okf_bundle/SUMMARY.md")
    lines.append("")
    lines.append("# Prime specific domain")
    if domains:
        lines.append(f"RUN cat ./okf_bundle/{sorted(domains.keys())[0]}/index.md")
    else:
        lines.append("RUN cat ./okf_bundle/<domain>/index.md")
    lines.append("")
    lines.append("# Find a concept")
    lines.append("RUN find ./okf_bundle -name '<ConceptName>.md' | xargs cat")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def write_summary(
    bundle_name: str,
    concepts: list[Concept],
    output_dir: Path,
    git: dict,
) -> Path:
    """Write SUMMARY.md to bundle root. Returns the path written."""
    content = render_summary(bundle_name, concepts, output_dir, git)
    out     = output_dir / "SUMMARY.md"
    out.write_text(content, encoding="utf-8")
    return out

# ---------------------------------------------------------------------------
# LLM enrichment (optional)
# ---------------------------------------------------------------------------

ENRICH_PROMPT = """\
You are enriching an OKF (Open Knowledge Format) knowledge bundle for a codebase.

Given this code concept, return a JSON object with four fields:

  "description"    - one clear sentence (max 20 words) summarising what it does,
                      specific enough to be useful to a developer or AI agent.
  "docstring"      - a full docstring in Google style:
                       - First line: one-sentence summary.
                       - Args section (if it has parameters).
                       - Returns section (if it returns something).
                       - Raises section (if relevant).
                     Omit sections that do not apply.
  "tags"           - 0-4 short semantic tags describing PURPOSE, not language/type
                      (e.g. "auth", "caching", "validation", "io-bound", "parsing").
                      Do not repeat the language, "function", "class", or module name
                      as a tag — those are already recorded elsewhere.
  "design_pattern" - a well-known design pattern name (e.g. "Factory", "Singleton",
                      "Observer", "Strategy", "Decorator") ONLY if the signature,
                      inheritance, or name clearly indicates one. Empty string if
                      none applies or you are not confident — do not force a label.

Rules:
- All fields must reference specific names or behaviour from THIS concept.
- Do NOT invent parameters or return types that are not in the signature.
- If the existing docstring is already detailed (>80 chars), improve it slightly
  rather than replacing it completely.
- Reply with ONLY the JSON object, no markdown fences, no preamble.

Concept type: {type}
Name: {title}
Existing docstring: {docstring}
Signature: {signature}
Parameters: {params}
Returns: {returns}
Inheritance: {inheritance}
"""


_MAX_BODY_LINES = 120  # cap so one large class doesn't blow the token budget

def _read_source_root(bundle_dir: Path) -> Path | None:
    """Read source_root from bundle's root index.md frontmatter."""
    try:
        raw = (bundle_dir / "index.md").read_text(encoding="utf-8")
        parts = raw.split("---", 2)
        if len(parts) >= 2:
            fm = yaml.safe_load(parts[1]) or {}
            src = fm.get("source_root")
            if src:
                return Path(str(src)).resolve()
    except Exception:
        pass
    return None


def _read_body(concept: Concept, source_dir: Path | None = None, bundle_dir: Path | None = None) -> str:
    """Best-effort read of the concept's source body using resource + source_lines.
    Returns '' if anything is missing/unreadable — callers must treat that as
    'no body available' and skip body-dependent enrichment rather than guessing."""
    if not concept.resource or not concept.source_lines:
        return ""
    start, end = concept.source_lines
    if not start or not end or end < start:
        return ""
    if source_dir is None and bundle_dir is not None:
        src = _read_source_root(bundle_dir)
        if src is None:
            return ""
        source_dir = src
    if source_dir is None:
        return ""
    try:
        path = (source_dir / concept.resource).resolve()
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        snippet = lines[start - 1:end]
        if len(snippet) > _MAX_BODY_LINES:
            snippet = snippet[:_MAX_BODY_LINES] + ["# ... truncated ..."]
        return "\n".join(snippet)
    except Exception as e:
        log.debug(f"Could not read body for {concept.title}: {e}")
        return ""


_DEPRECATED_RE = re.compile(r"@deprecated|\bdeprecated\b", re.IGNORECASE)

def _detect_deprecation(concept: Concept) -> str:
    """Deterministic scan of docstring + decorators for deprecation markers.
    Not LLM-based — comment/decorator text is either present or it isn't,
    so a regex is more reliable and cheaper than an inference call."""
    haystack = " ".join([concept.docstring or "", " ".join(concept.decorators or [])])
    if _DEPRECATED_RE.search(haystack):
        for line in (concept.docstring or "").splitlines():
            if _DEPRECATED_RE.search(line):
                return line.strip()
        return "Marked deprecated (see decorators)."
    return ""


def enrich_concept(concept: Concept, client, model: str) -> Concept:
    needs_desc = not concept.description or len(concept.description) <= 120
    needs_doc  = not concept.docstring or len(concept.docstring) <= 80

    # nothing to do
    if not needs_desc and not needs_doc:
        return concept

    # only enrich functions and classes — modules get description from first docstring line
    if concept.type not in {"Function", "Class", "Method"}:
        if needs_desc and concept.docstring:
            concept.description = concept.docstring.strip().splitlines()[0][:120]
        return concept

    # deterministic — no LLM call needed, do this regardless of needs_desc/needs_doc
    dep_note = _detect_deprecation(concept)
    if dep_note:
        concept.deprecation_notes = dep_note

    # build param summary for the prompt
    params_summary = ", ".join(
        p["name"] + (f": {p['annotation']}" if p.get("annotation") else "")
        for p in (concept.params or [])
    ) or "none"

    prompt = ENRICH_PROMPT.format(
        type=concept.type,
        title=concept.title,
        docstring=concept.docstring[:500] if concept.docstring else "none",
        signature=concept.signature or "none",
        params=params_summary,
        returns=concept.returns or "none",
        inheritance=", ".join(concept.inheritance) if concept.inheritance else "none",
    )

    raw = ""  # ensure always bound before try/except
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.1,
        )
        raw = (resp.choices[0].message.content or "").strip()

        # strip markdown fences if model wraps anyway
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw).strip()

        data = json.loads(raw)

        if needs_desc and data.get("description"):
            concept.description = data["description"].strip()

        if needs_doc and data.get("docstring"):
            concept.docstring = data["docstring"].strip()

        # tags are additive: keep the deterministic lang/type/module tags and
        # merge in LLM-suggested semantic tags, deduped, existing ones untouched
        llm_tags = data.get("tags") or []
        if isinstance(llm_tags, list):
            for t in llm_tags:
                t = str(t).strip().lower()
                if t and t not in concept.tags:
                    concept.tags.append(t)

        if data.get("design_pattern"):
            concept.design_pattern = str(data["design_pattern"]).strip()

    except json.JSONDecodeError:
        # fallback: treat whole response as description only
        if needs_desc and raw:
            concept.description = raw.splitlines()[0][:120]
        log.debug(f"JSON parse failed for {concept.title}, used fallback")
    except Exception as e:
        log.debug(f"Enrichment failed for {concept.title}: {e}")

    return concept


DEEP_ENRICH_PROMPT = """\
You are enriching an OKF (Open Knowledge Format) knowledge bundle for a codebase.

You are given the ACTUAL SOURCE BODY below, not just the signature. Only describe
behaviour you can see directly in this body — do not speculate about callers,
inputs from other files, or runtime conditions not visible here.

Return a JSON object with four fields:

  "usage_example" - a short (2-6 line) realistic code snippet showing how to call
                     this, using only the parameters/return type actually shown.
                     Empty string if the concept has no meaningful call pattern
                     (e.g. a plain data class with no methods).
  "side_effects"   - one sentence on what this mutates, reads/writes (files, env,
                      network, globals), or "Pure — no observable side effects."
                      if the body has none of that. Base this ONLY on the body
                      given; if uncertain, say what is uncertain rather than
                      asserting purity or impurity you can't confirm.
  "security"       - list ONLY concrete, visible risk patterns in this body:
                      unsanitized input reaching a query/shell/eval/HTML sink,
                      hardcoded secrets, missing auth checks that are visibly
                      absent, unsafe deserialization, etc. Quote the specific
                      line/construct you're flagging. If you see no such pattern,
                      say exactly: "No obvious risk pattern in this body." Do NOT
                      say a concept is "safe" or "secure" — absence of a visible
                      issue is not proof of safety, since you cannot see callers
                      or the full data flow.
  "complexity"     - Big-O time/space ONLY if a clear loop, recursion, or data
                      structure operation is visible in the body (e.g. nested
                      loops, recursive calls). Otherwise return exactly:
                      "Not estimable from this body alone." Do not guess based
                      on the function name or docstring.

Reply with ONLY the JSON object, no markdown fences, no preamble.

Concept type: {type}
Name: {title}
Signature: {signature}
Source body:
{body}
"""


def enrich_concept_deep(concept: Concept, client, model: str, source_dir: Path) -> Concept:
    """Second-pass enrichment that requires the actual source body.
    Skips silently (no call made) if the body can't be resolved, rather than
    falling back to signature-only guessing for fields that need real code.

    security/complexity are intentionally worded to avoid false-confidence
    claims (see DEEP_ENRICH_PROMPT) and the render layer adds a hardcoded
    "AI-estimated — verify manually" disclaimer regardless of what the model
    returns, so the caveat can't be silently dropped."""
    if concept.type not in {"Function", "Class", "Method"}:
        return concept
    if concept.usage_example and concept.side_effects and concept.security and concept.complexity:
        return concept  # already enriched

    body = _read_body(concept, source_dir)
    if not body:
        log.debug(f"No body available for {concept.title}, skipping deep enrichment")
        return concept

    prompt = DEEP_ENRICH_PROMPT.format(
        type=concept.type,
        title=concept.title,
        signature=concept.signature or "none",
        body=body,
    )

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.1,
        )
        raw = (resp.choices[0].message.content or "").strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw).strip()
        data = json.loads(raw)

        if data.get("usage_example"):
            concept.usage_example = str(data["usage_example"]).strip()
        if data.get("side_effects"):
            concept.side_effects = str(data["side_effects"]).strip()
        if data.get("security"):
            concept.security = str(data["security"]).strip()
        if data.get("complexity"):
            concept.complexity = str(data["complexity"]).strip()

    except json.JSONDecodeError:
        log.debug(f"Deep-enrich JSON parse failed for {concept.title}")
    except Exception as e:
        log.debug(f"Deep enrichment failed for {concept.title}: {e}")

    return concept


# ---------------------------------------------------------------------------
# Standalone security/complexity audit — runs against an EXISTING bundle
# (okf generate --security) without re-scanning or touching any other field.
# ---------------------------------------------------------------------------

SECURITY_PROMPT = """\
You are auditing one code concept for an OKF (Open Knowledge Format) knowledge
bundle. You are given the ACTUAL SOURCE BODY below — only describe patterns
visible in this body; do not speculate about callers or data you cannot see.

Return a JSON object with two fields:

  "security"   - concrete, visible risk patterns only: unsanitized input reaching
                  a query/shell/eval/HTML sink, hardcoded secrets, missing auth
                  checks that are visibly absent, unsafe deserialization, etc.
                  Quote the specific construct you're flagging. If you see none,
                  say exactly: "No obvious risk pattern in this body." Never say
                  a concept is "safe" or "secure" — absence of a visible issue is
                  not proof of safety, since you cannot see callers or full data flow.
  "complexity" - Big-O time/space ONLY if a clear loop, recursion, or data
                  structure operation is visible in the body. Otherwise return
                  exactly: "Not estimable from this body alone." Do not guess
                  from the function name or docstring alone.

Reply with ONLY the JSON object, no markdown fences, no preamble.

Concept type: {type}
Name: {title}
Signature: {signature}
Source body:
{body}
"""


def enrich_security(concept: Concept, client, model: str, source_dir: Path) -> Concept:
    """Lean, security/complexity-only enrichment."""
    if concept.type not in {"Function", "Class", "Method"}:
        return concept
    if concept.security and concept.complexity:
        return concept
    body = _read_body(concept, source_dir)
    if not body:
        log.debug(f"No body available for {concept.title}, skipping security audit")
        return concept
    prompt = SECURITY_PROMPT.format(
        type=concept.type, title=concept.title, signature=concept.signature or "none", body=body,
    )
    try:
        resp = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=300, temperature=0.1)
        raw = (resp.choices[0].message.content or "").strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw).strip()
        data = json.loads(raw)
        if data.get("security"):
            concept.security = str(data["security"]).strip()
        if data.get("complexity"):
            concept.complexity = str(data["complexity"]).strip()
    except json.JSONDecodeError:
        log.debug(f"Security-audit JSON parse failed for {concept.title}")
    except Exception as e:
        log.debug(f"Security audit failed for {concept.title}: {e}")
    return concept


_SOURCE_LINE_RE = re.compile(r"Lines (\d+)[-\u2013\u2014](\d+) in")


def _parse_source_line_range(source_section_text: str) -> tuple:
    """Recover (start, end) from the '## Source\\nLines N-M in `path`' section."""
    m = _SOURCE_LINE_RE.search(source_section_text or "")
    if not m:
        return ()
    return (int(m.group(1)), int(m.group(2)))


def _upsert_section(body: str, heading_prefix: str, new_heading: str, content: str,
                     insert_before: str = "## Source") -> str:
    """Surgically replace a single '## <heading_prefix>...' section, or insert
    a new one if absent — without touching any other section."""
    lines = body.splitlines()
    start = None
    end = len(lines)
    for i, line in enumerate(lines):
        if line.startswith(heading_prefix):
            start = i
            end = len(lines)
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("## "):
                    end = j
                    break
            break
    new_section = [new_heading, "", content, ""]
    if start is not None:
        lines[start:end] = new_section
    else:
        insert_at = len(lines)
        for i, line in enumerate(lines):
            if line.startswith(insert_before):
                insert_at = i
                break
        lines[insert_at:insert_at] = new_section + [""]
    return "\n".join(lines)


def _patch_security_complexity(path: Path, security: str, complexity: str) -> bool:
    """Write security/complexity into an existing concept .md file in place."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False
    body = parts[2]
    if security:
        body = _upsert_section(
            body, "## Security",
            "## Security \u26a0\ufe0f AI-estimated \u2014 verify manually, absence of a "
            "flagged pattern is not proof of safety",
            security,
        )
    if complexity:
        body = _upsert_section(
            body, "## Complexity",
            "## Complexity \u26a0\ufe0f AI-estimated \u2014 verify manually",
            complexity,
        )
    path.write_text("---" + parts[1] + "---" + body, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Semantic related-links (separate pass — needs the full concept catalog)
# ---------------------------------------------------------------------------

_MAX_CANDIDATES = 40


def _candidate_pool(concept: Concept, all_concepts: dict[str, Concept]) -> list[Concept]:
    """Cheap deterministic prefilter before the LLM re-ranks."""
    concept_dir = concept.resource.rsplit("/", 1)[0] if "/" in (concept.resource or "") else ""
    scored: list[tuple[int, Concept]] = []
    for other in all_concepts.values():
        if other.concept_id == concept.concept_id:
            continue
        if other.type not in {"Function", "Class", "Method"}:
            continue
        if other.concept_id in concept.related or other.concept_id in concept.calls or other.concept_id in concept.called_by:
            continue
        score = len(set(other.tags or []) & set(concept.tags or [])) * 2
        other_dir = other.resource.rsplit("/", 1)[0] if "/" in (other.resource or "") else ""
        if other_dir == concept_dir:
            score += 1
        if other.type == concept.type:
            score += 1
        if score > 0:
            scored.append((score, other))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:_MAX_CANDIDATES]]


RELATED_PROMPT = """\
You are finding semantically related code concepts for an OKF knowledge bundle.
Given the target concept and a list of CANDIDATES, pick UP TO {top_k} candidate
ids that are genuinely related in purpose or pattern. Do NOT pick candidates
just because they share a tag or directory if the purpose isn't actually related.

Rules:
- Only return ids that appear EXACTLY as given in the candidate list below.
- If nothing is truly related, return an empty list.
- Reply with ONLY a JSON object: {{"related_ids": ["id1", "id2"]}}, no preamble.

Target concept:
type: {type}
title: {title}
description: {description}

Candidates:
{candidates}
"""


def enrich_related_semantic(
    concept: Concept, all_concepts: dict[str, Concept], client, model: str, top_k: int = 5,
) -> Concept:
    """Adds LLM-suggested cross-links to concept.related_semantic."""
    if concept.type not in {"Function", "Class", "Method"}:
        return concept
    if concept.related_semantic:
        return concept
    candidates = _candidate_pool(concept, all_concepts)
    if not candidates:
        return concept
    candidate_ids = {c.concept_id for c in candidates}
    candidate_text = "\n".join(
        f"- {c.concept_id}: {c.title} \u2014 {c.description or 'no description'}"
        for c in candidates
    )
    prompt = RELATED_PROMPT.format(top_k=top_k, type=concept.type, title=concept.title, description=concept.description or "none", candidates=candidate_text)
    try:
        resp = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=200, temperature=0.1)
        raw = (resp.choices[0].message.content or "").strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw).strip()
        data = json.loads(raw)
        ids = data.get("related_ids") or []
        if isinstance(ids, list):
            concept.related_semantic = [i for i in ids if i in candidate_ids][:top_k]
    except json.JSONDecodeError:
        log.debug(f"Related-links JSON parse failed for {concept.title}")
    except Exception as e:
        log.debug(f"Semantic related linking failed for {concept.title}: {e}")
    return concept


# ---------------------------------------------------------------------------
# Client resolver — per-mode provider dispatch
# ---------------------------------------------------------------------------

def _resolve_client(cfg: dict, mode: str):
    """Create an LLM client for the given enrich mode.

    Resolves provider via config.resolve_provider(), then instantiates
    the appropriate SDK client. Returns (client, resolved_dict) or
    raises ImportError if the required SDK is missing.

    For anthropic provider -> anthropic.Anthropic client
    For all others        -> openai.OpenAI client (OpenAI-compatible)
    """
    from okf.config import resolve_provider
    r = resolve_provider(cfg, mode)
    api_key = r["api_key"]
    base_url = r["base_url"]

    if r["provider"] == "anthropic":
        try:
            from anthropic import Anthropic
        except ImportError:
            log.warning("anthropic package not installed. Install with: pip install anthropic")
            raise
        client = Anthropic(api_key=api_key)
    else:
        try:
            from openai import OpenAI
        except ImportError:
            log.warning("openai package not installed. Install with: pip install openai")
            raise
        if not api_key:
            api_key = "sk-unset"  # placeholder so client init doesn't crash
        client = OpenAI(api_key=api_key, base_url=base_url)

    return client, r


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def _walk_source_dirs(root: Path) -> set[str]:
    """All non-hidden, non-skipped directories under root (relative posix paths,
    '' for root itself). Used so directories with no parseable concepts —
    including genuinely empty ones — still appear in the bundle layout."""
    dirs = {""}
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        rel_parts = path.relative_to(root).parts
        if any(
            part.startswith(".") or
            part in SKIP_DIRS or
            any(part.endswith(sfx) for sfx in SKIP_DIR_SUFFIXES)
            for part in rel_parts
        ):
            continue
        dirs.add("/".join(rel_parts))
    return dirs


def scan_codebase(root: Path, exclude: list[str] | None = None) -> list[Concept]:
    git = _git_info(root)
    if git:
        log.info(f"Git: repo={git.get('repo','?')} branch={git.get('branch','?')}")

    if not root.exists() or not root.is_dir():
        log.warning(f"Source directory does not exist or is not a directory: {root}")
        return []

    exclude = exclude or []
    concepts = []
    all_paths = sorted(root.rglob("*"))
    log.info(f"Scanning {len(all_paths)} paths...")

    pbar = tqdm(all_paths, desc="Scanning", unit="files", leave=False, disable=len(all_paths) < 500)
    for path in pbar:
        rel = path.relative_to(root)
        # per-run exclude patterns (e.g. --exclude tests, --exclude docs)
        if any(part in exclude for part in rel.parts):
            continue
        # skip hidden / vendor dirs (only check relative to root, not absolute prefix)
        if any(
            part.startswith(".") or
            part in SKIP_DIRS or
            any(part.endswith(sfx) for sfx in SKIP_DIR_SUFFIXES)
            for part in rel.parts
        ):
            continue
        if not path.is_file():
            continue
        if manifest_scanner.is_manifest_file(path):
            try:
                raw_deps = manifest_scanner.scan_manifest(path, root)
                for d in raw_deps:
                    # Merge standardised tags with ecosystem-specific tags from the scanner
                    base = _make_tags(language="manifest", resource=d["resource"],
                                      concept_type=d["type"], git=git)
                    existing = set(d.get("tags", []))
                    merged = list(dict.fromkeys(base + [t for t in existing if not t.startswith(("lang:", "type:", "module:", "domain:", "git:"))]))
                    c = Concept(
                        type=d["type"], title=d["title"],
                        description=d["description"], resource=d["resource"],
                        tags=merged,
                        timestamp=d["timestamp"], concept_id=d["concept_id"],
                        body_extra=d.get("body_extra", {}),
                    )
                    concepts.append(c)
                log.debug(f"Parsed manifest {path}: {len(raw_deps)} deps")
            except Exception as e:
                log.warning(f"Failed to parse manifest {path}: {e}")
            continue
        parser = get_parser(path.suffix.lower())
        if parser is None:
            continue
        try:
            file_concepts = parser.parse_file(path, root)
            for c in file_concepts:
                c.tags = _make_tags(
                    language=parser.LANGUAGE,
                    resource=c.resource,
                    concept_type=c.type,
                    git=git,
                )
            concepts.extend(file_concepts)
            log.debug(f"Parsed {path}: {len(file_concepts)} concepts")
        except Exception as e:
            log.warning(f"Failed to parse {path}: {e}")

    if not concepts:
        log.warning(f"No recognized source files found under {root} — bundle will be empty.")
        return concepts

    from okf.linker import link_all
    stats = link_all(concepts)
    log.info(stats.summary_line())

    return concepts


# ---------------------------------------------------------------------------
# Writer  (domain/resource-path layout)
# ---------------------------------------------------------------------------

def _concept_output_path(concept: Concept, output_dir: Path) -> Path:
    """Map concept_id to output .md path, mirroring the source tree."""
    return output_dir.joinpath(*concept.concept_id.split("/")).with_suffix(".md")


def write_bundle(
    concepts: list[Concept],
    output_dir: Path,
    bundle_name: str,
    log_entries: list[str],
    source_dirs: set[str] | None = None,
    source_root: str = "",
):
    output_dir.mkdir(parents=True, exist_ok=True)

    concepts = _dedup_concept_ids(concepts)
    all_map: dict[str, Concept] = {c.concept_id: c for c in concepts}

    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ── 1. Write every concept file (skip already-enriched ones) ────────────
    from okf.config import load as load_config, _get
    _cfg = load_config()
    enrich_enabled = _get(_cfg, "llm.enabled", False)
    for c in concepts:
        out_path = _concept_output_path(c, output_dir)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # If enrichment is enabled and file already exists with rich content,
        # skip overwriting — the enrichment pass already wrote the best version
        if enrich_enabled and out_path.exists():
            try:
                existing = out_path.read_text(encoding="utf-8", errors="replace")
                fm_parts = existing.split("---", 2)
                if len(fm_parts) >= 2:
                    fm = yaml.safe_load(fm_parts[1]) or {}
                    if len(fm.get("description", "")) > 60:
                        continue  # keep enriched version
            except Exception:
                pass
        out_path.write_text(render_concept(c, all_map), encoding="utf-8")

    # ── 2. Build directory tree from all concept paths ────────────────────
    # dir_path (relative to output_dir) → {"subdirs": set, "concepts": list}
    dir_tree: dict[str, dict] = {}

    def _ensure_dir(rel: str):
        if rel not in dir_tree:
            dir_tree[rel] = {"subdirs": set(), "concepts": []}

    def _register_ancestors(rel_dir: str):
        parts = rel_dir.split("/") if rel_dir else []
        for i in range(len(parts)):
            parent = "/".join(parts[:i]) if i > 0 else ""
            child  = "/".join(parts[:i+1])
            _ensure_dir(parent)
            _ensure_dir(child)
            dir_tree[parent]["subdirs"].add(child)

    for c in concepts:
        out_path = _concept_output_path(c, output_dir)
        rel_dir = str(out_path.parent.relative_to(output_dir)).replace(os.sep, "/")
        if rel_dir == ".":
            rel_dir = ""
        _ensure_dir(rel_dir)
        dir_tree[rel_dir]["concepts"].append(c)
        _register_ancestors(rel_dir)

    # ── 2b. Register directories with no concepts at all (empty folders, or
    #        folders containing only files in unsupported formats) so they
    #        still show up in the navigation instead of disappearing ───────
    for rel_dir in (source_dirs or set()):
        rel_dir = rel_dir.replace(os.sep, "/")
        _ensure_dir(rel_dir)
        _register_ancestors(rel_dir)

    # ── 3. Write index.md at every directory level ────────────────────────
    for rel_dir, node in dir_tree.items():
        dir_abs = output_dir / rel_dir if rel_dir else output_dir
        dir_abs.mkdir(parents=True, exist_ok=True)
        index_content = render_dir_index(
            dir_path=rel_dir,
            subdirs=list(node["subdirs"]),
            concepts=node["concepts"],
            bundle_name=bundle_name,
            all_map=all_map,
        )
        (dir_abs / "index.md").write_text(index_content, encoding="utf-8")

    # ── 4. Root index ─────────────────────────────────────────────────────
    top_dirs = sorted(dir_tree.get("", {}).get("subdirs", set()))
    (output_dir / "index.md").write_text(
        render_root_index(bundle_name, top_dirs, len(concepts), ts, source_root=source_root),
        encoding="utf-8",
    )

    # ── 5. Log ────────────────────────────────────────────────────────────
    (output_dir / "log.md").write_text(render_log(log_entries), encoding="utf-8")

    # return summary grouped by type (for printing)
    by_type: dict[str, list] = {}
    for c in concepts:
        by_type.setdefault(c.type, []).append(c)
    return by_type


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def setup_logging():
    level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def enrich_bundle(
    bundle_dir: Path,
    mode: str = "base",
    source_dir: Path | None = None,
    force: bool = False,
    file_filter: str | None = None,
    concept_filter: str | None = None,
):
    """Run an enrich pass against an EXISTING bundle without re-scanning.

    Reads source_root from bundle index.md frontmatter (stored at generate time),
    or uses the provided source_dir. Supports modes: base, deep, security, full.
    Default is 'base' (safe, no source code sent to LLM).

    Args:
        file_filter: If set, only enrich concepts from this source file path.
        concept_filter: If set, only enrich the concept with this concept_id.
    """
    if not bundle_dir.exists():
        log.error(f"Bundle directory not found: {bundle_dir}")
        return

    src = source_dir or _read_source_root(bundle_dir)
    if not src:
        log.error("No source directory available. Either pass --src or generate the bundle first.")
        return

    from okf.config import load as load_config
    _cfg = load_config()

    from okf.pairs import load_bundle as _load_md
    raw = _load_md(bundle_dir)

    # Apply filters
    if file_filter:
        raw = [r2 for r2 in raw if file_filter in r2.get("resource", "")]
        log.info(f"Filtered by file '{file_filter}': {len(raw)} concepts")
    if concept_filter:
        raw = [r2 for r2 in raw if concept_filter in r2.get("concept_id", "")]
        log.info(f"Filtered by concept '{concept_filter}': {len(raw)} concepts")
    if not raw:
        log.info("No concepts match the filter.")
        return

    if mode == "base":
        resolve_mode = "description"
    elif mode in ("deep", "full"):
        resolve_mode = "deep"
    else:
        resolve_mode = "security"
    try:
        client, r = _resolve_client(_cfg, resolve_mode)
    except ImportError:
        return
    log.info(f"Enrich (mode={mode}): {r['provider']}/{r['model']} @ {r['base_url']}")

    if mode == "base":
        log.info(f"Base enrich for {len(raw)} concepts...")
        all_map = {}
        concepts = []
        for r2 in raw:
            s = r2.get("sections", {})
            c = Concept(
                type=r2.get("type", ""),
                title=r2.get("title", ""),
                description=r2.get("description", ""),
                resource=r2.get("resource", ""),
                tags=r2.get("tags", []),
                signature=s.get("signature", ""),
                docstring=s.get("docstring", ""),
                params=[dict(zip(["name", "annotation", "default"], [x.strip().strip("`") for x in p.split("|")[1:4]])) for p in s.get("parameters", "").splitlines() if "|" in p and "Name" not in p and "---" not in p] or r2.get("params", []),
                returns=s.get("returns", "").strip("`").strip(),
                source_lines=_parse_source_line_range(s.get("source", "")),
                concept_id=r2.get("concept_id", ""),
            )
            concepts.append(c)
            all_map[c.concept_id] = c

        done_seen = errors = 0
        with ThreadPoolExecutor(max_workers=r["max_workers"]) as pool:
            futures = {pool.submit(_enrich_one_base, c, client, r["model"], bundle_dir, all_map): c for c in concepts}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Enriching"):
                try:
                    future.result()
                    done_seen += 1
                except Exception as e:
                    errors += 1
                    log.debug(f"Enrich error: {e}")
        log.info(f"Enrich complete: {done_seen} done, {errors} errors")

    elif mode == "security":
        targets = []
        for r2 in raw:
            if r2.get("type") not in {"Function", "Class", "Method"}:
                continue
            sections = r2.get("sections", {})
            source_lines = _parse_source_line_range(sections.get("source", ""))
            if not source_lines:
                continue
            if not force and sections.get("security") and sections.get("complexity"):
                continue
            c = Concept(type=r2.get("type", ""), title=r2.get("title", ""), resource=r2.get("resource", ""), signature=sections.get("signature", ""), source_lines=source_lines)
            targets.append((c, Path(r2["source_file"])))
        log.info(f"To audit: {len(targets)} concepts")
        if not targets:
            log.info("Nothing to do — all concepts already audited (use --force to re-run).")
            return
        done_seen = skipped = errors = 0
        with ThreadPoolExecutor(max_workers=r["max_workers"]) as pool:
            futures = {}
            for c, path in targets:
                futures[pool.submit(_audit_one, c, client, r["model"], src, path)] = (c, path)
            for future in tqdm(as_completed(futures), total=len(futures), desc="Security audit"):
                try:
                    result = future.result()
                    if result == "done":
                        done_seen += 1
                    else:
                        skipped += 1
                except Exception as e:
                    errors += 1
                    log.debug(f"Security audit error: {e}")
        log.info(f"Security audit complete: {done_seen} patched, {skipped} skipped, {errors} errors")

    elif mode in ("deep", "full"):
        log.info(f"Deep enrich for {len(raw)} concepts...")
        all_map = {}
        concepts = []
        for r2 in raw:
            s = r2.get("sections", {})
            c = Concept(
                type=r2.get("type", ""),
                title=r2.get("title", ""),
                description=r2.get("description", ""),
                resource=r2.get("resource", ""),
                tags=r2.get("tags", []),
                signature=s.get("signature", ""),
                docstring=s.get("docstring", ""),
                params=[dict(zip(["name", "annotation", "default"], p.split("|")[1:4])) for p in s.get("parameters", "").splitlines() if "|" in p and "Name" not in p and "---" not in p] or r2.get("params", []),
                returns=s.get("returns", "").strip("`").strip(),
                methods=[m.strip("`") for m in s.get("methods", "").splitlines() if m.strip().startswith("- `")],
                source_lines=_parse_source_line_range(s.get("source", "")),
                concept_id=r2.get("concept_id", ""),
                related=r2.get("related", []),
            )
            concepts.append(c)
            all_map[c.concept_id] = c

        def _deep_and_write(c):
            enriched = enrich_concept(c, client, r["model"])
            enriched = enrich_concept_deep(enriched, client, r["model"], src)
            p = _concept_output_path(enriched, bundle_dir)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(render_concept(enriched, all_map), encoding="utf-8")
            return enriched

        done_seen = errors = 0
        with ThreadPoolExecutor(max_workers=r["max_workers"]) as pool:
            futures = {pool.submit(_deep_and_write, c): c for c in concepts}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Enriching"):
                try:
                    future.result()
                    done_seen += 1
                except Exception as e:
                    errors += 1
                    log.debug(f"Enrich error: {e}")
        log.info(f"Enrich complete: {done_seen} done, {errors} errors")


def _audit_one(c: Concept, client, model: str, source_dir: Path, path: Path) -> str:
    """Helper for enrich_bundle security mode."""
    enrich_security(c, client, model, source_dir)
    if c.security or c.complexity:
        if _patch_security_complexity(path, c.security, c.complexity):
            return "done"
    return "skipped"


def _enrich_one_base(c: Concept, client, model: str, bundle_dir: Path, all_map: dict) -> None:
    """Enrich a single concept with base mode and write it back."""
    enriched = enrich_concept(c, client, model)
    p = _concept_output_path(enriched, bundle_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render_concept(enriched, all_map), encoding="utf-8")


def main():
    setup_logging()

    # --summarize mode: regenerate SUMMARY.md from existing bundle (no re-scan)
    if len(sys.argv) >= 2 and sys.argv[1] == "--summarize":
        bundle_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path("okf_bundle").resolve()
        if not bundle_dir.exists():
            log.error(f"Bundle directory not found: {bundle_dir}")
            sys.exit(1)
        log.info(f"Regenerating SUMMARY.md from existing bundle: {bundle_dir}")
        # load concepts from existing bundle by parsing all .md files
        from okf.pairs import load_bundle as _load_md
        raw = _load_md(bundle_dir)
        # reconstruct minimal Concept objects for summary
        regen_concepts = []
        for r in raw:
            c = Concept(
                type=r.get("type",""),
                title=r.get("title",""),
                description=r.get("description",""),
                resource=r.get("resource",""),
                tags=r.get("tags",[]),
                concept_id=r.get("concept_id",""),
            )
            regen_concepts.append(c)
        out = write_summary(bundle_dir.name, regen_concepts, bundle_dir, {})
        log.info(f"SUMMARY.md written -> {out}")
        return

    # --security mode: audit an EXISTING bundle for security/complexity only.
    if len(sys.argv) >= 2 and sys.argv[1] == "--security":
        if len(sys.argv) < 3:
            print("Usage: okf generate --security <source_dir> [bundle_dir] [--force]")
            sys.exit(1)
        force = "--force" in sys.argv
        _argv = [a for a in sys.argv if a != "--force"]
        source_dir = Path(_argv[2]).resolve()
        bundle_dir = Path(_argv[3]).resolve() if len(_argv) > 3 else Path("okf_bundle").resolve()
        if not source_dir.exists():
            log.error(f"Source directory not found: {source_dir}")
            sys.exit(1)
        if not bundle_dir.exists():
            log.error(f"Bundle directory not found: {bundle_dir}")
            sys.exit(1)
        from okf.config import load as load_config
        _cfg = load_config()
        try:
            client, r = _resolve_client(_cfg, "security")
        except ImportError:
            sys.exit(1)
        log.info(f"Security audit: {r['provider']}/{r['model']} @ {r['base_url']}")
        from okf.pairs import load_bundle as _load_md
        raw = _load_md(bundle_dir)
        targets = []
        for r2 in raw:
            if r2.get("type") not in {"Function", "Class", "Method"}:
                continue
            sections = r2.get("sections", {})
            source_lines = _parse_source_line_range(sections.get("source", ""))
            if not source_lines:
                continue
            if not force and sections.get("security") and sections.get("complexity"):
                continue
            c = Concept(type=r2.get("type", ""), title=r2.get("title", ""), resource=r2.get("resource", ""), signature=sections.get("signature", ""), source_lines=source_lines)
            targets.append((c, Path(r2["source_file"])))
        log.info(f"To audit: {len(targets)} concepts")
        if not targets:
            log.info("Nothing to do — all concepts already audited (use --force to re-run).")
            return
        done = skipped = errors = 0
        def _audit_and_patch(item):
            c, path = item
            enrich_security(c, client, r["model"], source_dir)
            if c.security or c.complexity:
                if _patch_security_complexity(path, c.security, c.complexity):
                    return "done"
            return "skipped"
        with ThreadPoolExecutor(max_workers=r["max_workers"]) as pool:
            futures = {pool.submit(_audit_and_patch, t): t for t in targets}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Security audit"):
                try:
                    result = future.result()
                    if result == "done":
                        done += 1
                    else:
                        skipped += 1
                except Exception as e:
                    errors += 1
                    log.debug(f"Security audit error: {e}")
        log.info(f"Security audit complete: {done} patched, {skipped} skipped, {errors} errors")
        return

    # Determine source_dir: positional arg or auto-detect
    _has_pos_arg = len(sys.argv) >= 2 and not sys.argv[1].startswith("-")
    if _has_pos_arg:
        source_dir = Path(sys.argv[1]).resolve()
        output_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path("okf_bundle").resolve()
    else:
        from okf.root_detector import detect_root
        source_dir = detect_root()
        output_dir = Path("okf_bundle").resolve()
        log.info(f"Auto-detected project root: {source_dir}")

    # Save --enrich flag + optional mode before removing from argv
    _has_enrich_flag = "--enrich" in sys.argv
    _enrich_mode = "base"
    if _has_enrich_flag:
        idx = sys.argv.index("--enrich")
        del sys.argv[idx]
        if idx < len(sys.argv) and not sys.argv[idx].startswith("-"):
            _enrich_mode = sys.argv.pop(idx)
        if _enrich_mode not in {"base", "deep", "security", "full"}:
            print(f"Unknown enrich mode: {_enrich_mode!r}. Use: base, deep, security, full")
            sys.exit(1)

    exclude = []
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == "--exclude" and i + 1 < len(sys.argv):
            exclude.append(sys.argv[i + 1])
            i += 2
        else:
            i += 1

    if not source_dir.exists():
        log.error(f"Source directory not found: {source_dir}")
        sys.exit(1)

    bundle_name = source_dir.name
    log.info(f"Scanning: {source_dir}")
    log.info(f"Output:   {output_dir}")
    if exclude:
        log.info(f"Excluding: {', '.join(exclude)}")

    # --- Scan ---
    concepts = scan_codebase(source_dir, exclude=exclude)
    log.info(f"Found {len(concepts)} concepts")

    if not concepts:
        log.warning(
            "No concepts found — the source directory is empty or has no "
            "recognized source files. Writing an empty bundle anyway."
        )

    # --- Optional LLM enrichment (resumable) ---
    _do_enrich = {"base": False, "deep": False, "security": False, "semantic": False}
    if _enrich_mode == "full":
        _do_enrich = {"base": True, "deep": True, "security": True, "semantic": True}
    elif _enrich_mode == "deep":
        _do_enrich = {"base": True, "deep": True, "security": True, "semantic": False}
    elif _enrich_mode == "security":
        _do_enrich = {"base": False, "deep": False, "security": True, "semantic": False}
    elif _enrich_mode == "base":
        _do_enrich = {"base": True, "deep": False, "security": False, "semantic": False}

    from okf.config import load as load_config, _get
    _cfg = load_config()
    config_enabled = _get(_cfg, "llm.enabled", False)
    if config_enabled and not any(_do_enrich.values()):
        _do_enrich["base"] = True
    enrich = any(_do_enrich.values()) or _has_enrich_flag
    if enrich and not any(_do_enrich.values()):
        _do_enrich["base"] = True
    client = None

    # Resolve clients per mode
    if enrich:
        try:
            client, r = _resolve_client(_cfg, "description")
            model = r["model"]
            base_url = r["base_url"]
            max_workers = r["max_workers"]
            log.info(f"LLM enrichment enabled: {r['provider']}/{model} @ {base_url}")
        except ImportError:
            log.warning("Skipping LLM enrichment.")

    if client:
        # Resolve deep enrichment client (may use a different provider)
        deep_client = None
        deep_model = None
        if _do_enrich["deep"] or _do_enrich["security"]:
            try:
                deep_client, deep_r = _resolve_client(_cfg, "deep")
                deep_model = deep_r["model"]
                log.info(f"Deep enrichment enabled: {deep_r['provider']}/{deep_model} @ {deep_r['base_url']}")
            except ImportError:
                log.warning("Deep enrichment disabled.")

        # Prepare output dirs and lookup so we can write each file immediately
        output_dir.mkdir(parents=True, exist_ok=True)
        concepts = _dedup_concept_ids(concepts)
        all_map_enrich: dict[str, Concept] = {c.concept_id: c for c in concepts}

        def _concept_path(c: Concept) -> Path:
            return _concept_output_path(c, output_dir)

        def _is_already_enriched(c: Concept) -> bool:
            """Return True if the on-disk .md already has rich description + docstring."""
            p = _concept_path(c)
            if not p.exists():
                return False
            try:
                raw = p.read_text(encoding="utf-8", errors="replace")
                parts = raw.split("---", 2)
                if len(parts) < 3:
                    return False
                fm = yaml.safe_load(parts[1]) or {}
                desc = fm.get("description", "")
                has_doc = "## Docstring" in parts[2] and len(parts[2]) > 200
                return len(desc) > 120 and has_doc
            except Exception:
                return False

        def _enrich_and_write(c: Concept) -> Concept:
            enriched = enrich_concept(c, client, model)
            if deep_client:
                enriched = enrich_concept_deep(enriched, deep_client, deep_model, source_dir)
            path = _concept_path(enriched)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(render_concept(enriched, all_map_enrich), encoding="utf-8")
            return enriched

        to_enrich   = [c for c in concepts if c.type in {"Function", "Class", "Method"} and not _is_already_enriched(c)]
        skipped_ok  = sum(1 for c in concepts if c.type in {"Function", "Class", "Method"} and _is_already_enriched(c))
        log.info(f"To enrich: {len(to_enrich)}  |  already done (skipped): {skipped_ok}")

        done = errors = 0
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(_enrich_and_write, c): c for c in to_enrich}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Enriching"):
                try:
                    future.result()
                    done += 1
                except Exception as e:
                    errors += 1
                    log.debug(f"Enrichment error: {e}")

        log.info(f"Enrichment complete: {done} enriched, {errors} errors, {skipped_ok} skipped")

        # --- Optional third pass: semantic related-links ---
        if _do_enrich["semantic"] and client:
            code_concepts = {cid: c for cid, c in all_map_enrich.items() if c.type in {"Function", "Class", "Method"}}
            def _relate_and_write(c: Concept) -> Concept:
                enrich_related_semantic(c, code_concepts, client, model)
                path = _concept_path(c)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(render_concept(c, all_map_enrich), encoding="utf-8")
                return c
            to_relate = [c for c in code_concepts.values() if not c.related_semantic]
            log.info(f"Building semantic related-links for {len(to_relate)} concepts...")
            rel_done = rel_errors = 0
            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {pool.submit(_relate_and_write, c): c for c in to_relate}
                for future in tqdm(as_completed(futures), total=len(futures), desc="Linking related"):
                    try:
                        future.result()
                        rel_done += 1
                    except Exception as e:
                        rel_errors += 1
                        log.debug(f"Related-linking error: {e}")
            log.info(f"Semantic related-links complete: {rel_done} linked, {rel_errors} errors")

    # --- Write bundle ---
    log_entries = [
        f"{datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} — Bundle generated from `{source_dir}`",
        f"  Source files scanned: {len(set(c.resource for c in concepts))}",
        f"  Total concepts: {len(concepts)}",
        f"  LLM enrichment: {'enabled' if enrich else 'disabled'}",
    ]

    by_type = write_bundle(
        concepts, output_dir, bundle_name, log_entries,
        source_dirs=_walk_source_dirs(source_dir),
        source_root=str(source_dir.resolve()),
    )

    # --- Write SUMMARY.md ---
    git = _git_info(source_dir)
    summary_path = write_summary(bundle_name, concepts, output_dir, git)
    log.info(f"SUMMARY.md written -> {summary_path}")

    # --- Summary ---
    print(f"\n{'='*55}")
    print(f"  Bundle: {bundle_name}")
    print(f"  Output: {output_dir}")
    print(f"  {'Type':<15} {'Concepts':>8}")
    print(f"  {'-'*24}")
    for ctype, items in sorted(by_type.items()):
        print(f"  {ctype:<15} {len(items):>8}")
    print(f"  {'─'*24}")
    print(f"  {'TOTAL':<15} {len(concepts):>8}")
    print(f"{'='*55}\n")
    log.info(f"OKF bundle written → {output_dir}")


if __name__ == "__main__":
    main()
