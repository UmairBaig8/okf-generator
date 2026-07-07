"""okf — unified CLI for the OKF toolkit.

Commands:
  okf generate   <source_dir> [output_dir]   Generate OKF bundle from codebase
  okf generate --enrich [base|deep|security|full]  Enrich with mode selection
  okf enrich     [--bundle <bundle_dir>] [--mode base|deep|security|full] [--src <path>]
                                               Enrich an EXISTING bundle (default: ./okf_bundle)
  okf lookup     <query> [options]            Look up a concept in a bundle
  okf diff       <old> <new>                  Diff two bundles (added/removed/changed)
  okf pairs      <bundle_dir> [output_file]  Convert bundle to training pairs
  okf summarize  <bundle_dir>                Regenerate SUMMARY.md only
  okf install    [agent]                     Install agent integration (claude, opencode, copilot, cursor, windsurf, cline, all)
  okf init                                   Interactive bundle setup wizard
  okf visualize  <bundle> [output.html]       Generate interactive HTML graph of a bundle
  okf serve      [dir] [--port] [--open]     Serve bundle + auto-open viz
  okf dashboard  <bundle> [--port] [--open]   Live bundle browser (FastAPI + interactive graph)
  okf mcp        <bundle> [--port]            MCP server for AI agents (Claude, Cursor, etc.)

Run `okf <command> --help` for per-command options.
"""

import shutil
import sys
from pathlib import Path


SKILL_SOURCE = Path(__file__).resolve().parent.parent / "SKILL.md"
AGENTS_MD_SOURCE = Path(__file__).resolve().parent.parent / "AGENTS.md"
COPILOT_SOURCE = Path(__file__).resolve().parent.parent / ".github" / "copilot-instructions.md"


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

    elif agent == "copilot":
        target = root / ".github" / "copilot-instructions.md"
        if not _maybe_overwrite(target, "Copilot instructions"):
            return
        if COPILOT_SOURCE.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(COPILOT_SOURCE, target)
        else:
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

    elif agent == "windsurf":
        target = root / ".windsurfrules"
        if not _maybe_overwrite(target, "Windsurf rules"):
            return
        target.write_text(_agent_rules("Windsurf"))
        print(f"Windsurf rules → {target}")

    elif agent == "cline":
        target = root / ".clinerules"
        if not _maybe_overwrite(target, "Cline rules"):
            return
        target.write_text(_agent_rules("Cline"))
        print(f"Cline rules → {target}")

    elif agent == "all":
        for a in ("claude", "opencode", "copilot", "cursor", "windsurf", "cline"):
            _install_agent(a)
        return

    else:
        print(f"Unknown agent: {agent!r}", file=sys.stderr)
        print("Available: claude, opencode, copilot, cursor, windsurf, cline, all", file=sys.stderr)
        sys.exit(1)


def _copilot_default() -> str:
    return """# OKF Knowledge Bundle — Copilot Instructions

This project uses okf-generator to produce an OKF v0.1 knowledge bundle at ./okf_bundle/.
Before editing any source file, run:

  okf lookup --bundle ./okf_bundle <ConceptName>

For dependencies: okf lookup --bundle ./okf_bundle --type Dependency
For JSON output:  okf lookup --bundle ./okf_bundle --json <Name>
"""


def _agent_rules(name: str) -> str:
    return f"""# {name} Rules — OKF Knowledge Bundle

This project is indexed as an OKF v0.1 bundle at ./okf_bundle/.
Every function, class, module, and dependency has a structured markdown file.

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

Agents:
  claude      Install Claude Code skill (SKILL.md → ~/.config/opencode/skills/)
  opencode    Add /lookup command (.opencode/commands/lookup.md)
  copilot     Add GitHub Copilot instructions (.github/copilot-instructions.md)
  cursor      Add Cursor rules (.cursorrules)
  windsurf    Add Windsurf rules (.windsurfrules)
  cline       Add Cline rules (.clinerules)
  all         Install for all agents above

Run without arguments to see this help.
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
        print("  lookup          Look up concepts in a bundle")
        print("  diff            Compare two bundles (added/removed/changed)")
        print("  pairs           Convert bundle to JSONL training pairs")
        print("  summarize       Regenerate SUMMARY.md from existing bundle")
        print("  dashboard       Launch live bundle browser (FastAPI + interactive graph)")
        print("  init            Interactive bundle setup wizard")
        print("  install         Set up agent integration (claude, opencode, copilot, cursor, windsurf, cline)")
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

    elif cmd == "summarize":
        sys.argv = ["okf generate", "--summarize"] + rest
        from okf.generator import main as _main
        _main()

    elif cmd == "enrich":
        from pathlib import Path
        from okf.generator import enrich_bundle
        # --bundle flag takes precedence, otherwise positional arg, otherwise ./okf_bundle
        if rest and not rest[0].startswith("--"):
            bundle_dir = Path(rest[0]).resolve()
            rest_args = list(rest[1:])
        else:
            bundle_dir = Path("okf_bundle").resolve()
            rest_args = list(rest)
        mode = "security"
        source_dir = None
        for i, a in enumerate(rest_args):
            if a == "--bundle" and i + 1 < len(rest_args):
                bundle_dir = Path(rest_args[i + 1]).resolve()
            elif a == "--mode" and i + 1 < len(rest_args):
                mode = rest_args[i + 1]
            elif a == "--src" and i + 1 < len(rest_args):
                source_dir = Path(rest_args[i + 1]).resolve()
            elif a == "--force":
                pass  # passed through
        if mode not in {"base", "deep", "security", "full"}:
            print(f"Unknown mode: {mode!r}. Use: base, deep, security, full")
            sys.exit(1)
        enrich_bundle(bundle_dir, mode=mode, source_dir=source_dir, force="--force" in rest_args or "--force" in rest)
        sys.exit(0)

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

    else:
        print(f"Unknown command: {cmd!r}", file=sys.stderr)
        print("Run `okf --help` for available commands.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
