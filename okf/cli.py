"""okf — unified CLI for the OKF toolkit.

Commands:
  okf generate   <source_dir> [output_dir]   Generate OKF bundle from codebase
  okf lookup     <query> [options]            Look up a concept in a bundle
  okf diff       <old> <new>                  Diff two bundles (added/removed/changed)
  okf pairs      <bundle_dir> [output_file]  Convert bundle to training pairs
  okf summarize  <bundle_dir>                Regenerate SUMMARY.md only
  okf install    [agent]                     Install agent integration (claude, opencode, copilot, cursor, windsurf, cline, all)
  okf visualize  <bundle> [output.html]       Generate interactive HTML graph of a bundle

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

    if agent == "claude":
        target = Path.home() / ".config" / "opencode" / "skills" / "okf-generator" / "SKILL.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(_find_skill(), target)
        print(f"Claude Code skill → {target}")
        print("  Restart Claude Code for it to take effect.")

    elif agent == "opencode":
        target = root / ".opencode" / "commands" / "lookup.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("RUN okf lookup --bundle ./okf_bundle $NAME\n")
        print(f"OpenCode command → {target}")
        print("  Use: /lookup NAME=<ConceptName>")

    elif agent == "copilot":
        target = root / ".github" / "copilot-instructions.md"
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
        target.write_text(_agent_rules("Cursor"))
        print(f"Cursor rules → {target}")

    elif agent == "windsurf":
        target = root / ".windsurfrules"
        target.write_text(_agent_rules("Windsurf"))
        print(f"Windsurf rules → {target}")

    elif agent == "cline":
        target = root / ".clinerules"
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


def main():
    if len(sys.argv) >= 2 and sys.argv[1] in {"-v", "--version"}:
        from okf import __version__
        print(f"okf-generator v{__version__}")
        sys.exit(0)

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
        print("  install         Set up agent integration (claude, opencode, copilot, cursor, windsurf, cline)")
        sys.exit(0)

    cmd, rest = sys.argv[1], sys.argv[2:]
    sys.argv = [f"okf {cmd}"] + rest

    if cmd == "install":
        _install_main()

    elif cmd in ("install-skill",):  # backwards compat
        _install_agent("claude")

    elif cmd == "generate":
        if rest and rest[0] == "--summarize":
            sys.argv = ["okf generate", "--summarize"] + rest[1:]
        from okf.generator import main as _main
        _main()

    elif cmd == "summarize":
        sys.argv = ["okf generate", "--summarize"] + rest
        from okf.generator import main as _main
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

    else:
        print(f"Unknown command: {cmd!r}", file=sys.stderr)
        print("Run `okf --help` for available commands.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
