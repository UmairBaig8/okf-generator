"""OKF Lookup — pinpoint exact concepts from an OKF bundle.

Designed to be called by OpenCode (or any AI agent) via RUN directive
to inject precise concept context before touching code.

Search modes:
  by name      exact or fuzzy match on concept title
  by file      all concepts extracted from a source file
  by tag       filter by OKF tag (e.g. lang:python, type:Class)
  by type      filter by concept type (Function, Class, Module)

Output modes:
  full         complete concept file (default for single result)
  compact      one-line per concept: type | title | file | description
  json         machine-readable JSON array

Usage:
  # Exact / fuzzy name search
  python okf_lookup.py WorldBankConnector
  python okf_lookup.py world bank          # fuzzy, space-separated tokens

  # All concepts from a source file
  python okf_lookup.py --file StockAI/RnD/python/connectors/economic_data.py

  # Filter by type
  python okf_lookup.py --type Class connector

  # Filter by tag
  python okf_lookup.py --tag lang:python --tag type:Function fetch

  # Change bundle dir (default: ./okf_bundle)
  python okf_lookup.py --bundle ./Knowlege/okf_bundle WorldBankConnector

  # Compact listing (good for /lookup commands)
  python okf_lookup.py --compact connector

  # JSON output (for programmatic use)
  python okf_lookup.py --json WorldBankConnector

  # Limit results
  python okf_lookup.py --limit 5 fetch
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Bundle loader (self-contained, no dependency on okf_to_pairs)
# ---------------------------------------------------------------------------

def _parse_md(path: Path, bundle_dir: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    if not text.startswith("---"):
        return None

    parts = text.split("---", 2)
    if len(parts) < 3:
        return None

    try:
        fm = yaml.safe_load(parts[1]) or {}
    except Exception:
        return None

    ctype = fm.get("type", "")
    if not ctype or ctype in {"Index", "Log"}:
        return None

    body = parts[2].strip()

    # parse sections
    sections: dict[str, str] = {}
    cur_key, cur_lines = None, []
    for line in body.splitlines():
        if line.startswith("## "):
            if cur_key:
                sections[cur_key] = "\n".join(cur_lines).strip()
            cur_key = line[3:].strip().lower()
            cur_lines = []
        elif cur_key is not None:
            cur_lines.append(line)
    if cur_key:
        sections[cur_key] = "\n".join(cur_lines).strip()

    rel = path.relative_to(bundle_dir)
    concept_id = str(rel.with_suffix("")).replace(os.sep, "/")

    return {
        "type":        ctype,
        "title":       fm.get("title", path.stem),
        "description": fm.get("description", ""),
        "resource":    fm.get("resource", ""),
        "tags":        fm.get("tags", []),
        "timestamp":   fm.get("timestamp", ""),
        "concept_id":  concept_id,
        "sections":    sections,
        "raw":         text,          # full file content for --full output
        "_path":       str(path),
    }


def load_bundle(bundle_dir: Path) -> list[dict]:
    reserved = {"index.md", "log.md", "SUMMARY.md"}
    concepts = []
    for md in sorted(bundle_dir.rglob("*.md")):
        if md.name in reserved:
            continue
        c = _parse_md(md, bundle_dir)
        if c:
            concepts.append(c)
    return concepts


# ---------------------------------------------------------------------------
# Scoring / search
# ---------------------------------------------------------------------------

def _score(concept: dict, tokens: list[str]) -> float:
    """Return a relevance score 0–1. Higher = better match."""
    if not tokens:
        return 1.0

    title       = concept["title"].lower()
    description = concept["description"].lower()
    resource    = concept["resource"].lower()
    concept_id  = concept["concept_id"].lower()
    tags        = " ".join(concept["tags"]).lower()

    score = 0.0
    for tok in tokens:
        t = tok.lower()
        if t == title:
            score += 1.0   # exact title match
        elif title.startswith(t):
            score += 0.8   # prefix match
        elif t in title:
            score += 0.6   # substring in title
        elif t in concept_id:
            score += 0.4   # in path
        elif t in resource:
            score += 0.35  # in source file
        elif t in description:
            score += 0.3   # in description
        elif t in tags:
            score += 0.2   # in tags
        # fuzzy: count matching chars / token length
        else:
            matches = sum(1 for ch in t if ch in title)
            ratio   = matches / max(len(t), 1)
            if ratio > 0.7:
                score += ratio * 0.15

    return score / len(tokens)


def search(
    concepts:  list[dict],
    tokens:    list[str],
    file_filter: str  = "",
    type_filter: str  = "",
    tag_filters: list[str] = [],
    limit:     int    = 10,
    min_score: float  = 0.1,
) -> list[dict]:

    results = []
    for c in concepts:
        # hard filters
        if file_filter and file_filter.lower() not in c["resource"].lower():
            continue
        if type_filter and c["type"].lower() != type_filter.lower():
            continue
        if tag_filters:
            ctags = [t.lower() for t in c["tags"]]
            if not all(f.lower() in ctags for f in tag_filters):
                continue

        score = _score(c, tokens)
        if score >= min_score or file_filter:   # file_filter shows all matches
            results.append((score, c))

    results.sort(key=lambda x: -x[0])
    return [c for _, c in results[:limit]]


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

DIVIDER = "─" * 60


def fmt_full(concept: dict) -> str:
    """Full concept content — exactly what's in the .md file."""
    return concept["raw"]


def fmt_detail(concept: dict) -> str:
    """Rich single-concept view — most useful for OpenCode context."""
    lines = [
        DIVIDER,
        f"  {concept['type'].upper()}: {concept['title']}",
        DIVIDER,
    ]

    if concept["description"]:
        lines.append(f"  Description : {concept['description']}")

    if concept["resource"]:
        src = concept["sections"].get("source", "")
        lineno = ""
        if src:
            m = re.search(r"Lines (\d+)", src)
            if m:
                lineno = f"  line {m.group(1)}"
        lines.append(f"  Source      : {concept['resource']}{lineno}")

    lines.append(f"  Concept ID  : {concept['concept_id']}")

    if concept["tags"]:
        lines.append(f"  Tags        : {', '.join(concept['tags'])}")

    # Signature
    sig = concept["sections"].get("signature", "")
    if sig:
        sig_clean = re.sub(r"```\w*\n?", "", sig).strip()
        lines.append(f"\n  Signature:\n    {sig_clean}")

    # Docstring
    doc = concept["sections"].get("docstring", "")
    if doc:
        doc_lines = doc.strip().splitlines()
        lines.append("\n  Docstring:")
        for dl in doc_lines[:8]:
            lines.append(f"    {dl}")
        if len(doc_lines) > 8:
            lines.append(f"    ... ({len(doc_lines)-8} more lines)")

    # Parameters
    params = concept["sections"].get("parameters", "")
    if params:
        lines.append("\n  Parameters:")
        for row in params.splitlines():
            if "|" in row and "---" not in row and "Name" not in row:
                cols = [c.strip().strip("`") for c in row.split("|") if c.strip()]
                if len(cols) >= 2:
                    lines.append(f"    {cols[0]}: {cols[1]}" + (f" = {cols[2]}" if len(cols) > 2 and cols[2] != "-" else ""))

    # Returns
    ret = concept["sections"].get("returns", "")
    if ret:
        lines.append(f"\n  Returns: {ret.replace('`','').strip()}")

    # Methods (for classes)
    methods = concept["sections"].get("methods", "")
    if methods:
        mnames = re.findall(r"`(\w+)`", methods)
        if mnames:
            lines.append(f"\n  Methods: {', '.join(mnames)}")

    # Related
    related = concept["sections"].get("related", "")
    if related:
        rnames = re.findall(r"\[([^\]]+)\]", related)
        if rnames:
            lines.append(f"\n  Related: {', '.join(rnames)}")

    lines.append(DIVIDER)
    return "\n".join(lines)


def fmt_compact(concept: dict) -> str:
    """Single line — good for listing multiple results."""
    desc = concept["description"][:60] + ("…" if len(concept["description"]) > 60 else "")
    return (
        f"[{concept['type']:<8}] {concept['title']:<30} "
        f"{concept['resource']:<40} {desc}"
    )


def fmt_json(concepts: list[dict]) -> str:
    out = []
    for c in concepts:
        out.append({
            "type":        c["type"],
            "title":       c["title"],
            "description": c["description"],
            "resource":    c["resource"],
            "concept_id":  c["concept_id"],
            "tags":        c["tags"],
            "signature":   c["sections"].get("signature", "").replace("```python", "").replace("```", "").strip(),
            "docstring":   c["sections"].get("docstring", ""),
            "methods":     re.findall(r"`(\w+)`", c["sections"].get("methods", "")),
            "returns":     c["sections"].get("returns", "").replace("`", "").strip(),
        })
    return json.dumps(out, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Look up OKF concepts — pinpoint exact code knowledge for AI agents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("query",       nargs="*",           help="Search tokens (name or keywords)")
    p.add_argument("--bundle",    default="./okf_bundle", help="Path to OKF bundle dir (default: ./okf_bundle)")
    p.add_argument("--file",      default="",          help="Filter by source file path (e.g. src/connectors/economic_data.py)")
    p.add_argument("--type",      default="",          help="Filter by concept type: Function | Class | Module")
    p.add_argument("--tag",       action="append", default=[], dest="tags", help="Filter by tag (repeatable): --tag lang:python --tag type:Class")
    p.add_argument("--limit",     type=int, default=10, help="Max results (default: 10)")
    p.add_argument("--compact",   action="store_true", help="One-line output per result")
    p.add_argument("--json",      action="store_true", help="JSON output")
    p.add_argument("--full",      action="store_true", help="Show raw .md file content")
    p.add_argument("--min-score", type=float, default=0.1, help="Minimum relevance score 0-1 (default: 0.1)")
    return p


def main():
    parser = build_parser()
    args   = parser.parse_args()

    bundle_dir = Path(args.bundle).resolve()
    if not bundle_dir.exists():
        # try common locations relative to cwd
        for candidate in ["./okf_bundle", "./Knowlege/okf_bundle", "./knowledge/okf_bundle"]:
            p = Path(candidate).resolve()
            if p.exists():
                bundle_dir = p
                break
        else:
            print(f"ERROR: OKF bundle not found at {args.bundle}", file=sys.stderr)
            print("Set --bundle path/to/okf_bundle", file=sys.stderr)
            sys.exit(1)

    # Load
    concepts = load_bundle(bundle_dir)
    if not concepts:
        print(f"ERROR: No concepts found in {bundle_dir}", file=sys.stderr)
        sys.exit(1)

    # Search
    tokens  = args.query or []
    results = search(
        concepts,
        tokens     = tokens,
        file_filter= args.file,
        type_filter= args.type,
        tag_filters= args.tags,
        limit      = args.limit,
        min_score  = args.min_score,
    )

    if not results:
        print("No concepts found", file=sys.stderr)
        if tokens:
            print(f"Query: {' '.join(tokens)}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.json:
        print(fmt_json(results))
        return

    if args.compact or len(results) > 3:
        # compact list for multiple results
        print(f"\nFound {len(results)} concept(s) in {bundle_dir.name}:\n")
        for c in results:
            print(fmt_compact(c))
        print()
        if len(results) == 1:
            print(fmt_detail(results[0]))
        else:
            print("Tip: run with exact name for full detail, e.g.:")
            print(f"  python okf_lookup.py --bundle {args.bundle} \"{results[0]['title']}\"")
        return

    # 1-3 results: show full detail for each
    for i, c in enumerate(results):
        if args.full:
            print(fmt_full(c))
        else:
            print(fmt_detail(c))
        if i < len(results) - 1:
            print()


if __name__ == "__main__":
    main()
