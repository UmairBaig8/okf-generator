"""okf init — interactive wizard for OKF bundle setup.

Guides you through:
  1. Picking a source directory (auto-detects languages + manifests)
  2. Generating the bundle
  3. Looking up a concept
  4. Visualizing the bundle
  5. Installing AI agent integration
  6. Serving the bundle

Usage:
  okf init                  Interactive wizard
  okf init --quick          Skip prompts, use defaults
"""

import argparse
import sys
from pathlib import Path

from okf.cli import print_banner


# ── Helpers ──────────────────────────────────────────────────────────────

PURPLE = "\033[35m"
CYAN = "\033[36m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"


def c(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def ask(prompt: str, default: str = "") -> str:
    """Ask with a colored prompt and optional default."""
    label = f"{c('?', CYAN)} {prompt}"
    if default:
        label += f" {c(f'[{default}]', YELLOW)}"
    try:
        return input(f"{label} ").strip() or default
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)


def confirm(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    val = ask(f"{prompt} {c(f'({hint})', YELLOW)}", "y" if default else "n")
    return val.lower().startswith("y")


def detect_languages(root: Path) -> dict[str, int]:
    """Count files by language in a directory."""
    exts = {
        ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
        ".go": "Go", ".java": "Java", ".rs": "Rust", ".rb": "Ruby",
        ".c": "C", ".h": "C", ".cpp": "C++", ".cxx": "C++", ".hpp": "C++", ".cs": "C#",
        ".sql": "SQL",
    }
    manifest_files = {
        "requirements.txt", "pyproject.toml", "package.json", "Cargo.toml", "Cargo.lock",
        "go.mod", "go.sum", "composer.json", "pom.xml", "Gemfile", "build.gradle",
        "Package.swift", "project.clj", "mix.exs", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
    }
    langs: dict[str, int] = {}
    manifests = 0
    total = 0
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext in exts:
            lang = exts[ext]
            langs[lang] = langs.get(lang, 0) + 1
        if path.name in manifest_files:
            manifests += 1
        total += 1
    return langs, manifests, total


def print_summary(langs: dict[str, int], manifests: int, total: int):
    if langs:
        print(f"  {c('Languages:', CYAN)} {'  '.join(f'{c(n, BOLD)}×{c(str(v), GREEN)}' for n, v in sorted(langs.items()))}")
    if manifests:
        print(f"  {c('Manifests:', CYAN)} {c(str(manifests), GREEN)} files")
    print(f"  {c('Total files:', CYAN)} {c(str(total), GREEN)}")


# ── Main ─────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Interactive OKF bundle setup wizard.")
    parser.add_argument("--quick", action="store_true", help="Skip prompts, use defaults")
    parser.add_argument("--llm", action="store_true", help="Enable LLM-assisted Q&A mode")
    args = parser.parse_args()

    print()
    print_banner()
    print(f"  {c('okf init', BOLD)} — interactive bundle setup wizard\n")
    if args.quick:
        print(f"  {c('Quick mode', YELLOW)} — using defaults\n")
    if args.llm:
        print(f"  {c('LLM mode enabled', CYAN)} — you can ask questions about your codebase\n")

    # ── Step 1: Source directory ──────────────────────────────────────────
    default_dir = "."
    src = ask("Source directory to scan?", default_dir) if not args.quick else default_dir
    src_path = Path(src).resolve()
    while not src_path.exists():
        print(f"  {c('Directory not found.', YELLOW)} Try again.")
        src = ask("Source directory to scan?", default_dir)
        src_path = Path(src).resolve()

    langs, manifests, total = detect_languages(src_path)
    print(f"\n  {c('Detected in', CYAN)} {c(str(src_path), BOLD)}{c(':', CYAN)}")
    print_summary(langs, manifests, total)

    out_name = src_path.name

    # ── Step 2: Generate bundle ───────────────────────────────────────────
    if args.quick or confirm("\nGenerate OKF bundle?", True):
        bundle_dir = src_path.parent / f"{out_name}_bundle" if src_path.name != "." else src_path / "okf_bundle"
        bundle_str = ask("Output directory?", str(bundle_dir)) if not args.quick else str(bundle_dir)
        bundle_path = Path(bundle_str).resolve()

        print(f"  {c('Generating bundle...', CYAN)}")
        from okf.generator import scan_codebase, write_bundle, write_summary, _walk_source_dirs
        from okf.linker import link_all

        concepts = scan_codebase(src_path)
        stats = link_all(concepts)
        print(f"  {c(stats.summary_line(), YELLOW)}")

        log_entries = [
            f"Generated via okf init from {src_path}",
            f"  Source files scanned: {len(set(c.resource for c in concepts))}",
            f"  Total concepts: {len(concepts)}",
        ]
        by_type = write_bundle(
            concepts, bundle_path, bundle_path.name, log_entries,
            source_dirs=_walk_source_dirs(src_path),
        )
        git_info = {}
        try:
            from okf.generator import _git_info
            git_info = _git_info(src_path) or {}
        except Exception:
            pass
        write_summary(bundle_path.name, concepts, bundle_path, git_info)

        print(f"\n  {c('Bundle written →', GREEN)} {bundle_path}")
        for ctype, items in sorted(by_type.items()):
            print(f"    {ctype:<15} {len(items):>8}")
        print(f"    {'─'*24}")
        print(f"    {'TOTAL':<15} {len(concepts):>8}")

        # ── Step 3: Look up a concept ─────────────────────────────────────
        if not args.quick:
            print()
            if confirm("Look up a concept?", False):
                while True:
                    query = ask("Concept name (or empty to skip)?")
                    if not query:
                        break
                    from okf.lookup import load_bundle, search, fmt_detail
                    loaded = load_bundle(bundle_path)
                    results = search(loaded, tokens=[query], limit=5)
                    if results:
                        for r in results:
                            print(f"\n  {fmt_detail(r)}")
                    else:
                        print(f"  {c('No concept found.', YELLOW)}")

        # ── Step 4: Visualize ─────────────────────────────────────────────
        if not args.quick:
            print()
            if confirm("Generate interactive visualization?", True):
                from okf.visualize import visualize as _viz_fn
                viz_path = bundle_path / "viz.html"
                html, n_nodes, n_edges = _viz_fn(bundle_path)
                viz_path.write_text(html, encoding="utf-8")
                print(f"  {c('Viz written →', GREEN)} {viz_path}")
                print(f"  {n_nodes} concepts, {n_edges} edges")

        # ── Step 5: Install for agents ────────────────────────────────────
        if not args.quick:
            print()
            if confirm("Install agent integrations?", False):
                from okf.cli import _install_agent
                for agent in ("claude", "opencode", "copilot", "cursor", "windsurf", "cline"):
                    _install_agent(agent)

        # ── Step 6: Serve ─────────────────────────────────────────────────
        if not args.quick:
            print()
            if confirm("Start local server to browse bundle?", True):
                from okf.serve import main as serve_main
                serve_main()

    print(f"\n  {c('Done.', GREEN)} {c('Run okf --help to explore more commands.', CYAN)}\n")
