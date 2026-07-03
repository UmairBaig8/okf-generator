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


def clr(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def ask(prompt: str, default: str = "") -> str:
    """Ask with a colored prompt and optional default."""
    label = f"{clr('?', CYAN)} {prompt}"
    if default:
        label += f" {clr(f'[{default}]', YELLOW)}"
    try:
        return input(f"{label} ").strip() or default
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)


def confirm(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    val = ask(f"{prompt} {clr(f'({hint})', YELLOW)}", "y" if default else "n")
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
        print(f"  {clr('Languages:', CYAN)} {'  '.join(f'{clr(n, BOLD)}×{clr(str(v), GREEN)}' for n, v in sorted(langs.items()))}")
    if manifests:
        print(f"  {clr('Manifests:', CYAN)} {clr(str(manifests), GREEN)} files")
    print(f"  {clr('Total files:', CYAN)} {clr(str(total), GREEN)}")


# ── Main ─────────────────────────────────────────────────────────────────


HELP_TEXT = f"""
  {clr('Available commands:', BOLD)}
    {clr('/g', CYAN)}            Generate/regenerate the bundle
    {clr('/lookup <name>', CYAN)}  Look up a concept
    {clr('/deps', CYAN)}         List dependencies
    {clr('/viz', CYAN)}          Generate HTML visualization
    {clr('/serve', CYAN)}        Start local HTTP server
    {clr('/install [agent]', CYAN)}  Install agent integration
    {clr('/info', CYAN)}         Show bundle info
    {clr('/help', CYAN)}         Show this help
    {clr('/quit', CYAN)}         Exit
"""


def repl_loop(bundle_path: Path):
    from okf.lookup import load_bundle, search, fmt_detail

    print(f"\n  {clr('Interactive mode — type /help for commands', CYAN)}\n")
    while True:
        try:
            cmd = input(f"{clr('okf>', PURPLE)} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not cmd:
            continue

        parts = cmd.split(maxsplit=1)
        verb = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if verb in ("/quit", "/exit", "/q"):
            break

        elif verb == "/help":
            print(HELP_TEXT)

        elif verb == "/info":
            concepts = load_bundle(bundle_path)
            types: dict[str, int] = {}
            for c in concepts:
                types[c["type"]] = types.get(c["type"], 0) + 1
            print(f"  {clr('Bundle:', BOLD)} {bundle_path.name}")
            for t, n in sorted(types.items()):
                print(f"    {t:<15} {n:>8}")
            print(f"    {'─'*24}")
            print(f"    {'TOTAL':<15} {sum(types.values()):>8}")

        elif verb == "/g":
            print(f"  {clr('Regenerating bundle...', CYAN)}")
            from okf.generator import scan_codebase, write_bundle, write_summary, _walk_source_dirs, _git_info
            from okf.linker import link_all

            src_path = bundle_path.parent / bundle_path.name.replace("_bundle", "") if bundle_path.name.endswith("_bundle") else bundle_path.parent
            concepts = scan_codebase(src_path)
            stats = link_all(concepts)
            print(f"  {clr(stats.summary_line(), YELLOW)}")
            log_entries = [f"Regenerated via okf init from {src_path}", f"  Total concepts: {len(concepts)}"]
            write_bundle(concepts, bundle_path, bundle_path.name, log_entries, source_dirs=_walk_source_dirs(src_path))
            git = _git_info(src_path) or {}
            write_summary(bundle_path.name, concepts, bundle_path, git)
            print(f"  {clr('Bundle regenerated.', GREEN)}")

        elif verb == "/lookup":
            if not arg:
                print(f"  {clr('Usage: /lookup <name>', YELLOW)}")
                continue
            concepts = load_bundle(bundle_path)
            results = search(concepts, tokens=arg.split(), limit=5)
            if results:
                for r in results:
                    print(f"\n{fmt_detail(r)}")
            else:
                print(f"  {clr('No concept found.', YELLOW)}")

        elif verb == "/deps":
            concepts = load_bundle(bundle_path)
            deps = [c for c in concepts if c["type"] == "Dependency"]
            if arg:
                deps = [c for c in deps if arg in c.get("resource", "")]
            print(f"  {clr(f'{len(deps)} dependencies:', BOLD)}")
            for d in deps:
                print(f"    {clr(d['title'], GREEN)}  {d.get('resource', '')}")

        elif verb == "/viz":
            print(f"  {clr('Generating visualization...', CYAN)}")
            from okf.visualize import visualize as _viz_fn
            viz_path = bundle_path / "viz.html"
            html, n_nodes, n_edges = _viz_fn(bundle_path)
            viz_path.write_text(html, encoding="utf-8")
            print(f"  {clr('Viz written →', GREEN)} {viz_path}")

        elif verb == "/serve":
            from okf.serve import main as serve_main
            serve_main()

        elif verb == "/install":
            targets = arg.split() if arg else ("claude", "opencode", "copilot", "cursor", "windsurf", "cline")
            from okf.cli import _install_agent
            for agent in targets:
                _install_agent(agent)

        else:
            print(f"  Unknown: {cmd}. Type {clr('/help', CYAN)} for commands.")


def main():
    parser = argparse.ArgumentParser(description="Interactive OKF bundle setup wizard.")
    parser.add_argument("--quick", action="store_true", help="Skip prompts, use defaults")
    parser.add_argument("--enrich", action="store_true", help="Enable LLM enrichment")
    parser.add_argument("dir", nargs="?", default=None, help="Source directory (optional)")
    args = parser.parse_args()

    print()
    print_banner()
    print(f"  {clr('okf init', BOLD)} — interactive bundle setup\n")
    if args.quick:
        print(f"  {clr('Quick mode', YELLOW)} — using defaults\n")

    # ── Source directory ──────────────────────────────────────────────────
    default_dir = args.dir or "."
    src = default_dir if args.quick or args.dir else ask("Source directory to scan?", default_dir)
    src_path = Path(src).resolve()
    while not src_path.exists():
        print(f"  {clr('Directory not found.', YELLOW)} Try again.")
        src = ask("Source directory to scan?", ".")
        src_path = Path(src).resolve()

    langs, manifests, total = detect_languages(src_path)
    print(f"\n  {clr('Detected in', CYAN)} {clr(str(src_path), BOLD)}{clr(':', CYAN)}")
    print_summary(langs, manifests, total)

    out_name = src_path.name

    # ── Output directory ──────────────────────────────────────────────────
    bundle_dir = src_path.parent / f"{out_name}_bundle" if src_path.name not in (".", "..") else src_path / "okf_bundle"
    bundle_str = str(bundle_dir)
    if not args.quick and not args.dir:
        bundle_str = ask("Output directory?", str(bundle_dir))
    bundle_path = Path(bundle_str).resolve()

    # ── Config ────────────────────────────────────────────────────────────
    cfg = {}
    cfg["bundle_dir"] = str(bundle_path)

    if args.enrich:
        cfg["llm"] = {"enabled": True}
    elif args.quick:
        cfg["llm"] = {"enabled": False}
    else:
        print(f"\n  {clr('Configuration', BOLD)}")
        if confirm("Enable LLM enrichment? (improves descriptions)", default=False):
            provider = ask("LLM provider (openai-compatible, anthropic, openai)?", "openai-compatible")
            base_url = ask("API base URL?", "http://localhost:8080/v1" if provider == "openai-compatible" else "https://api.anthropic.com/v1")
            model = ask("Model name?", "local-model")
            api_key = ask("API key (leave blank if not needed)?", "")
            cfg["llm"] = {
                "enabled": True,
                "provider": provider,
                "base_url": base_url,
                "model": model,
                "api_key": api_key,
                "max_workers": 2,
            }
        else:
            cfg["llm"] = {"enabled": False}

    # Write .okfconfig
    from okf.config import dump
    dotfile = Path.cwd() / ".okfconfig"
    dump(cfg, dotfile)
    print(f"  {clr('Config written →', GREEN)} {dotfile}")

    print(f"  {clr('Generating bundle...', CYAN)}")
    from okf.generator import scan_codebase, write_bundle, write_summary, _walk_source_dirs
    from okf.linker import link_all

    concepts = scan_codebase(src_path)
    stats = link_all(concepts)
    print(f"  {clr(stats.summary_line(), YELLOW)}")

    log_entries = [
        f"Generated via okf init from {src_path}",
        f"  Source files scanned: {len(set(c.resource for c in concepts))}",
        f"  Total concepts: {len(concepts)}",
    ]
    by_type = write_bundle(
        concepts, bundle_path, bundle_path.name, log_entries,
        source_dirs=_walk_source_dirs(src_path),
    )
    try:
        from okf.generator import _git_info
        git_info = _git_info(src_path) or {}
    except Exception:
        git_info = {}
    write_summary(bundle_path.name, concepts, bundle_path, git_info)

    print(f"\n  {clr('Bundle written →', GREEN)} {bundle_path}")
    for ctype, items in sorted(by_type.items()):
        print(f"    {ctype:<15} {len(items):>8}")
    print(f"    {'─'*24}")
    print(f"    {'TOTAL':<15} {len(concepts):>8}")

    # ── REPL loop ─────────────────────────────────────────────────────────
    if not args.quick:
        repl_loop(bundle_path)

    print(f"\n  {clr('Done.', GREEN)}\n")
