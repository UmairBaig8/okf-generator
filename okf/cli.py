"""okf — unified CLI for the OKF toolkit.

Commands:
  okf generate   <source_dir> [output_dir]   Generate OKF bundle from codebase
  okf update     [--force] [--enrich] [--watch] [--debounce MS] [--exclude PAT]
                                                Incremental bundle update (fast, re-scans only changed files)
  okf domains   [list|validate <file>]   List domain rules or validate a rule file
  okf enrich     [--lsp] [--llm] [--full] [--mode base|deep|security] [--bundle <dir>] [--src <path>]
                                                Enrich an existing bundle with LSP (4 servers) and/or LLM
  okf lsp        [status|resolve|map]         Inspect available language servers (4 verified: pyright, gopls, rust-analyzer, typescript)
  okf lookup     <query> [options]            Look up a concept in a bundle
  okf ask        <question>                  AI-powered Q&A about your codebase (requires LLM)
  okf diff       <old> <new>                  Diff two bundles (added/removed/changed)
  okf pairs      <bundle_dir> [output_file]  Convert bundle to training pairs
  okf summarize  <bundle_dir>                Regenerate SUMMARY.md only
  okf install    [agent]                     Install agent integration (claude, opencode, copilot, cursor, windsurf, cline, all)
  okf init                                   Interactive bundle setup wizard
  okf visualize  <bundle> [output.html]       Generate interactive HTML graph of a bundle
  okf serve      [dir] [--port] [--open]     Serve bundle + auto-open viz
  okf dashboard  <bundle> [--port] [--open]   Live bundle browser (FastAPI + interactive graph)
  okf mcp        <bundle> [--port] [--install] MCP server for AI agents. --install registers in opencode.json / claude_desktop_config.json
  okf plugin     [list|install|uninstall]     Manage parser plugins

Run `okf <command> --help` for per-command options.
"""

import shutil
import sys
from pathlib import Path


SKILL_SOURCE = Path(__file__).resolve().parent.parent / "SKILL.md"


def _find_skill() -> Path:
    if SKILL_SOURCE.exists():
        return SKILL_SOURCE
    alt = Path(__file__).resolve().parent / "SKILL.md"
    if alt.exists():
        return alt
    from okf import __version__
    print(f"SKILL.md not found — reinstall okf-generator (v{__version__}+)", file=sys.stderr)
    sys.exit(1)


def _install_agent(agent: str):
    root = Path.cwd()

    def _maybe_overwrite(target: Path, desc: str) -> bool:
        if target.exists():
            resp = input(f"  {desc} already exists at {target}. Overwrite? [y/N] ").strip().lower()
            if resp != "y":
                print(f"  Skipped {desc}.")
                return False
        return True

    if agent == "claude":
        target = Path.home() / ".config" / "opencode" / "skills" / "okf-generator" / "SKILL.md"
        if not _maybe_overwrite(target, "Claude Code skill"):
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(_find_skill(), target)
        print(f"Claude Code skill → {target}")
        print("  Restart Claude Code for it to take effect.")

    elif agent == "opencode":
        target = root / ".opencode" / "commands" / "lookup.md"
        if not _maybe_overwrite(target, "OpenCode command"):
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("RUN okf lookup --bundle ./okf_bundle $NAME\n")
        print(f"OpenCode command → {target}")
        print("  Use: /lookup NAME=<ConceptName>")
        print("  Tip: also run 'okf mcp --install' to set up MCP tools (preferred over shell commands)")

    elif agent == "copilot":
        target = root / ".github" / "copilot-instructions.md"
        if not _maybe_overwrite(target, "Copilot instructions"):
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_copilot_default())
        print(f"Copilot instructions → {target}")
        print("  Copilot loads this file automatically.")

    elif agent == "cursor":
        target = root / ".cursorrules"
        if not _maybe_overwrite(target, "Cursor rules"):
            return
        target.write_text(_agent_rules("Cursor"))
        print(f"Cursor rules → {target}")
        print("  Tip: also run 'okf mcp --install' to set up MCP tools (preferred over shell commands)")

    elif agent == "windsurf":
        target = root / ".windsurfrules"
        if not _maybe_overwrite(target, "Windsurf rules"):
            return
        target.write_text(_agent_rules("Windsurf"))
        print(f"Windsurf rules → {target}")
        print("  Tip: also run 'okf mcp --install' to set up MCP tools (preferred over shell commands)")

    elif agent == "cline":
        target = root / ".clinerules"
        if not _maybe_overwrite(target, "Cline rules"):
            return
        target.write_text(_agent_rules("Cline"))
        print(f"Cline rules → {target}")
        print("  Tip: also run 'okf mcp --install' to set up MCP tools (preferred over shell commands)")

    elif agent == "mcp":
        _install_mcp()
        return

    elif agent == "all":
        for a in ("claude", "opencode", "copilot", "cursor", "windsurf", "cline"):
            _install_agent(a)
        _install_agent("mcp")
        return

    else:
        print(f"Unknown agent: {agent!r}", file=sys.stderr)
        print("Available: claude, opencode, copilot, cursor, windsurf, cline, mcp, all", file=sys.stderr)
        print("Note: OpenAI Codex reads AGENTS.md — use 'okf install opencode' to set it up.", file=sys.stderr)
        sys.exit(1)


def _install_mcp():
    """Run okf mcp --install with auto-detected bundle dir."""
    bundle = Path("okf_bundle").resolve()
    from okf.mcp_server import _install_mcp_config
    _install_mcp_config(bundle)


def _copilot_default() -> str:
    return """# OKF Knowledge Bundle — Copilot Instructions

This project uses okf-generator to produce an OKF v0.2 knowledge bundle at ./okf_bundle/.
Every function, class, module, and dependency has a structured markdown card.

## MCP Tools (preferred)

If an MCP server is running, use lookup/get_concept/find_callers etc. via MCP.
Otherwise, use the shell commands below.

## CRITICAL RULE: Never grep source files first

BEFORE reading or editing any source file, ALWAYS run:
  okf lookup --bundle ./okf_bundle <ConceptName>

This returns signature, parameters, docstring, dependencies, callers,
and callees in milliseconds — faster and more accurate than reading source.

## Common lookups

  okf lookup --bundle ./okf_bundle --type Function <Name>
  okf lookup --bundle ./okf_bundle --type Class <Name>
  okf lookup --bundle ./okf_bundle --type Dependency
  okf lookup --bundle ./okf_bundle --tag lang:python
  okf lookup --bundle ./okf_bundle --tag ecosystem:npm
  okf lookup --bundle ./okf_bundle --json <Name>
  okf diff ./okf_bundle.bak ./okf_bundle --compact
"""


def _agent_rules(name: str) -> str:
    return f"""# {name} Rules — OKF Knowledge Bundle

This project is indexed as an OKF v0.2 bundle at ./okf_bundle/.
Every function, class, module, and dependency has a structured markdown card.

## MCP Tools (preferred)

If this agent supports MCP, the OKF MCP server exposes 11 tools:
  lookup, get_concept, find_callers, find_callees, list_by_file,
  list_dependencies, bundle_info, list_by_type, search_by_tag,
  get_related, get_manifest_source

Use these instead of shell commands when available.

## CRITICAL RULE: Never grep source files first

BEFORE reading or editing any source file, ALWAYS run:
  okf lookup --bundle ./okf_bundle <ConceptName>

This returns signature, parameters, docstring, dependencies, callers,
and callees in milliseconds — faster and more accurate than reading source.

## Common lookups

  okf lookup --bundle ./okf_bundle --type Function <Name>
  okf lookup --bundle ./okf_bundle --type Class <Name>
  okf lookup --bundle ./okf_bundle --type Dependency
  okf lookup --bundle ./okf_bundle --tag lang:python
  okf lookup --bundle ./okf_bundle --tag ecosystem:npm
  okf lookup --bundle ./okf_bundle --json <Name>
  okf diff ./okf_bundle.bak ./okf_bundle --compact
"""


HELP = """Usage: okf install [agent]

Install okf-generator integration for an AI coding agent.

Skill installation (instructions/rules for the AI):
  claude      Install Claude Code skill (SKILL.md → ~/.config/opencode/skills/)
  opencode    Add /lookup command (.opencode/commands/lookup.md)
  copilot     Add GitHub Copilot instructions (.github/copilot-instructions.md)
  cursor      Add Cursor rules (.cursorrules)
  windsurf    Add Windsurf rules (.windsurfrules)
  cline       Add Cline rules (.clinerules)

  Note: OpenAI Codex (CLI + VS Code) reads AGENTS.md — use `okf install opencode`
  to set it up. Codex is covered automatically via the same AGENTS.md convention.

MCP server registration (preferred — gives agent direct tools):
  mcp         Register OKF MCP server in OpenCode + Claude configs
  all         Install skills for all agents + register MCP

Tip: MCP tools (lookup, find_callers, etc.) are preferred over RUN commands.
Run 'okf mcp --install' for the same effect as 'okf install mcp'.
"""


def _install_main():
    args = sys.argv[1:]  # okf install [agent] [agent] ...
    if not args or args[0] in {"-h", "--help"}:
        print(HELP)
        sys.exit(0)

    for agent in args:
        _install_agent(agent)


BANNER = r"""┌─────────────────────────────────────────────────────┐
│  ██████╗ ██╗  ██╗███████╗                           │
│ ██╔═══██╗██║ ██╔╝██╔════╝  [ O.K.F. ]               │
│ ██║   ██║█████╔╝ █████╗    Open Knowledge Format    │
│ ██║   ██║██╔═██╗ ██╔══╝    Generator                │
│ ╚██████╔╝██║  ██╗██║       v{version}                  │
│  ╚═════╝ ╚═╝  ╚═╝╚═╝       ► Index any codebase     │
└─────────────────────────────────────────────────────┘"""

PURPLE = "\033[35m"
RESET = "\033[0m"


def print_banner():
    from okf import __version__
    for line in BANNER.splitlines():
        print(f"{PURPLE}{line.replace('{version}', __version__)}{RESET}")


def main():
    if len(sys.argv) >= 2 and sys.argv[1] in {"-v", "--version"}:
        from okf import __version__
        print(f"okf-generator v{__version__}")
        sys.exit(0)

    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print_banner()

    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print(__doc__)
        print("Usage: okf <command> [args]")
        print("")
        print("Commands:")
        print("  generate        Generate OKF bundle from a codebase")
        print("  update          Incremental bundle update (re-scans only changed files)")
        print("  enrich          Enrich existing bundle via LSP, LLM, or both")
        print("  lsp             Inspect available language servers")
        print("  lookup          Look up concepts in a bundle")
        print("  ask             AI-powered Q&A about your codebase (requires LLM)")
        print("  diff            Compare two bundles (added/removed/changed)")
        print("  pairs           Convert bundle to JSONL training pairs")
        print("  summarize       Regenerate SUMMARY.md from existing bundle")
        print("  domains         [list|validate <file>]  List or validate domain rules")
        print("  migrate         Convert OKF bundle between schema versions")
        print("  visualize       Generate interactive HTML graph of a bundle")
        print("  serve           Serve bundle as static HTML via local server")
        print("  dashboard       Launch live bundle browser (FastAPI + interactive graph)")
        print("  config          View or set OKF configuration")
        print("  init            Interactive bundle setup wizard")
        print("  install         Set up agent integration (claude, opencode, copilot, cursor, windsurf, cline, mcp)")
        print("  mcp             Start MCP server (stdio or HTTP). Use --install to register in client configs")
        print("  plugin          Manage parser plugins (list, install, uninstall)")
        print("  agent           Interactive REPL with persistent sessions, slash commands")
        sys.exit(0)

    cmd, rest = sys.argv[1], sys.argv[2:]
    sys.argv = [f"okf {cmd}"] + rest

    if cmd == "init":
        from okf.init import main as _main
        _main()

    elif cmd == "install":
        _install_main()

    elif cmd in ("install-skill",):  # backwards compat
        _install_agent("claude")

    elif cmd == "generate":
        if rest and rest[0] == "--summarize":
            sys.argv = ["okf generate", "--summarize"] + rest[1:]
        elif rest and rest[0] == "--security":
            sys.argv = ["okf generate", "--security"] + rest[1:]
        from okf.generator import main as _main
        _main()

    elif cmd == "update":
        source_dir = None
        bundle_dir = Path("okf_bundle").resolve()
        force = False
        enable_enrich = False
        watch = False
        debounce_ms = 500
        exclude = set()

        i = 0
        while i < len(rest):
            a = rest[i]
            if a == "--force":
                force = True
                i += 1
            elif a == "--enrich":
                enable_enrich = True
                i += 1
            elif a == "--watch":
                watch = True
                i += 1
            elif a == "--debounce" and i + 1 < len(rest):
                debounce_ms = int(rest[i + 1])
                i += 2
            elif a == "--exclude" and i + 1 < len(rest):
                exclude.add(rest[i + 1])
                i += 2
            elif not a.startswith("--") and source_dir is None:
                source_dir = Path(a).resolve()
                i += 1
            elif not a.startswith("--") and bundle_dir == Path("okf_bundle").resolve():
                bundle_dir = Path(a).resolve()
                i += 1
            else:
                print(f"Unknown flag: {a!r}")
                sys.exit(1)

        if source_dir is None or not source_dir.exists():
            print("Error: specify a valid source directory")
            sys.exit(1)

        if watch:
            try:
                from okf.watcher import watch_and_update
                print(f"Watching {source_dir} for changes...")
                watch_and_update(source_dir, bundle_dir, debounce_ms, exclude, enable_enrich)
            except ImportError:
                print("Watch mode requires 'watchdog' package. Install: pip install watchdog")
                sys.exit(1)
        else:
            from okf.update import update_bundle
            dirty = update_bundle(source_dir, bundle_dir, exclude, force, enable_enrich)
            if dirty > 0:
                print(f"  Updated {dirty} concept(s)")
            else:
                print("  No changes")

    elif cmd == "summarize":
        sys.argv = ["okf generate", "--summarize"] + rest
        from okf.generator import main as _main
        _main()

    elif cmd == "enrich":
        from okf.pairs import load_bundle
        from okf.enrich import run_enrich

        if rest and not rest[0].startswith("--"):
            bundle_dir = Path(rest[0]).resolve()
            rest_args = list(rest[1:])
        else:
            bundle_dir = Path("okf_bundle").resolve()
            rest_args = list(rest)

        source_dir = None
        file_filter = None
        concept_filter = None
        enable_lsp = False
        enable_llm = False
        llm_mode = "base"

        i = 0
        while i < len(rest_args):
            a = rest_args[i]
            if a == "--bundle" and i + 1 < len(rest_args):
                bundle_dir = Path(rest_args[i + 1]).resolve()
                i += 2
            elif a == "--src" and i + 1 < len(rest_args):
                source_dir = Path(rest_args[i + 1]).resolve()
                i += 2
            elif a == "--file" and i + 1 < len(rest_args):
                file_filter = rest_args[i + 1]
                i += 2
            elif a == "--concept" and i + 1 < len(rest_args):
                concept_filter = rest_args[i + 1]
                i += 2
            elif a == "--lsp":
                enable_lsp = True
                i += 1
            elif a == "--llm":
                enable_llm = True
                i += 1
            elif a == "--full":
                enable_lsp = True
                enable_llm = True
                llm_mode = "deep"
                i += 1
            elif a == "--mode" and i + 1 < len(rest_args):
                llm_mode = rest_args[i + 1]
                if llm_mode not in {"base", "deep", "security"}:
                    print(f"Unknown LLM mode: {llm_mode!r}. Use: base, deep, security")
                    sys.exit(1)
                i += 2
            elif a == "--force":
                i += 1
            else:
                print(f"Unknown flag: {a!r}")
                sys.exit(1)

        if not enable_lsp and not enable_llm:
            print("Error: specify --lsp, --llm, or --full")
            print()
            print("  okf enrich --lsp                LSP enrichment only")
            print("  okf enrich --llm                LLM enrichment (mode=base)")
            print("  okf enrich --llm --mode deep    LLM deep enrichment")
            print("  okf enrich --lsp --llm          LSP + LLM base")
            print("  okf enrich --full               LSP + LLM deep (shortcut)")
            sys.exit(1)

        if not bundle_dir.exists():
            print(f"Bundle directory not found: {bundle_dir}")
            sys.exit(1)

        raw = load_bundle(bundle_dir)

        if file_filter:
            raw = [r for r in raw if file_filter in r.get("resource", "")]
        if concept_filter:
            raw = [r for r in raw if concept_filter in r.get("concept_id", "")]

        if source_dir is None:
            from okf.generator import _read_source_root
            source_dir = _read_source_root(bundle_dir)

        if not source_dir:
            print("No source directory. Pass --src or generate the bundle first.")
            sys.exit(1)

        # Quick sanity: check if source_dir actually contains source files
        # referenced by the bundle (sample up to 3)
        _sample_paths = []
        for r2 in raw[:3]:
            res = r2.get("resource", "")
            if res:
                _sample_paths.append(str((source_dir / res).resolve()))
        if _sample_paths and not any(Path(p).exists() for p in _sample_paths):
            print(f"Warning: --src points to {source_dir} but none of the bundle's")
            print(f"  source files were found there (e.g. {_sample_paths[0]}).")
            print("  Enrichment will skip all concepts due to missing files.")
            print("  The correct source root is where the original code lives.")

        print(f"  Bundle: {bundle_dir}")
        print(f"  Source: {source_dir}")
        print(f"  Concepts: {len(raw)}")

        results = run_enrich(
            bundle_dir, raw, source_dir,
            enable_lsp=enable_lsp,
            enable_llm=enable_llm,
            llm_mode=llm_mode,
        )
        for name, result in results:
            status = "partial" if result.is_partial else "complete"
            print(f"  {name}: {result.enriched_count}/{result.total_count} enriched ({status})")
            if result.warnings:
                _warn_count = len(result.warnings)
                if _warn_count <= 10:
                    for w in result.warnings:
                        print(f"    {w}")
                else:
                    print(f"    ({_warn_count} warnings — use --verbose to show all)")
                    for w in result.warnings[:5]:
                        print(f"    {w}")
                    print(f"    ... and {_warn_count - 5} more")

        sys.exit(0)

    elif cmd == "lsp":
        from okf.lsp import main as _lsp_main
        _lsp_main()

    elif cmd == "config":
        from okf.config import load, dump, CONFIG_FILES, _get
        if rest and rest[0] in ("-h", "--help"):
            print("""Usage: okf config [key=value ...]

View or set OKF configuration.

Without arguments: show current config (merged from env + file).
With key=value pairs: write to project .okfconfig file.

Common settings:
  llm.api_key       API key for LLM enrichment (or OKF_API_KEY env)
  llm.base_url      API base URL — works with llama.cpp, Ollama, vLLM, etc.
  llm.model         Model name
  llm.max_workers   Parallel enrichment workers (default: 2)

Any key is allowed — .okfconfig is extensible for future settings.

Examples:
  okf config                                   # view current config
  okf config llm.base_url=http://localhost:8080/v1
  okf config llm.api_key=sk-xxx
""")
            sys.exit(0)

        if rest:
            pairs = dict(kv.split("=", 1) for kv in rest if "=" in kv)
            existing = load()
            for k, v in pairs.items():
                from okf.config import _set
                _set(existing, k, v)
            proj_file = CONFIG_FILES[0]
            dump(existing, proj_file)
            print(f"Written {proj_file}")
        else:
            cfg = load()
            for k in ("llm.base_url", "llm.model", "llm.api_key", "llm.max_workers"):
                v = _get(cfg, k, "")
                if "api_key" in k and v:
                    v = v[:8] + "..." if len(v) > 8 else "***"
                print(f"  {k:20s} {v}")
    elif cmd == "agent":
        from okf.agent import main as _main
        _main()

    elif cmd in ("ask", "query"):
        from okf.ask import main as _main
        _main()

    elif cmd == "lookup":
        from okf.lookup import main as _main
        _main()

    elif cmd == "pairs":
        from okf.pairs import main as _main
        _main()

    elif cmd == "diff":
        from okf.diff import main as _main
        _main()

    elif cmd == "visualize":
        from okf.visualize import main as _main
        _main()

    elif cmd == "serve":
        from okf.serve import main as _main
        _main()

    elif cmd == "dashboard":
        from okf.dashboard import main as _main
        _main()

    elif cmd == "mcp":
        from okf.mcp_server import main as _main
        _main()

    elif cmd == "domains":
        if rest and rest[0] == "validate":
            if len(rest) < 2:
                print("Usage: okf domains validate <rule-file>")
                sys.exit(1)
            from okf.domains.engine import validate_rule_file
            errors = validate_rule_file(Path(rest[1]))
            if not errors:
                print(f"✅ {rest[1]} — valid")
            else:
                print(f"❌ {rest[1]} — {len(errors)} error(s):\n")
                for e in errors:
                    print(f"   • {e}")
                sys.exit(1)
        elif rest and rest[0] in ("-h", "--help", "help"):
            print("Usage: okf domains [list|validate <file>]")
            print()
            print("  okf domains              List available domain rule sets")
            print("  okf domains validate     Validate a rule file for correctness")
        else:
            from okf.domains.engine import list_domains
            domains = list_domains()
            if not domains:
                print("No domain rule sets found.")
                print("  Check: okf/domains/rules/ (built-in) or .okf/domains/ (project)")
                return
            print(f"\n  Available domains ({len(domains)}):\n")
            for d in domains:
                print(f"    {d['domain']:25s} [{d['source']}]  {d['path']}")
            print()
            print("  Use: okf generate --domains <domain>")
            print("  Use: okf domains validate <rule-file>")
            print()

    elif cmd == "migrate":
        from okf.migrate import main as _main
        _main()

    elif cmd == "plugin":
        from okf.plugin import cli as _main
        _main()

    else:
        print(f"Unknown command: {cmd!r}", file=sys.stderr)
        print("Run `okf --help` for available commands.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
