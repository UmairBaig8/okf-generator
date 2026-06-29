"""okf — unified CLI for the OKF toolkit.

Commands:
  okf generate   <source_dir> [output_dir]   Generate OKF bundle from codebase
  okf lookup     <query> [options]            Look up a concept in a bundle
  okf pairs      <bundle_dir> [output_file]  Convert bundle to training pairs
  okf summarize  <bundle_dir>                Regenerate SUMMARY.md only
  okf install-skill                         Install Claude Code skill

Run `okf <command> --help` for per-command options.
"""

import shutil
import sys
from pathlib import Path


SKILL_SOURCE = Path(__file__).resolve().parent.parent / "SKILL.md"


def _install_skill():
    target_dir  = Path.home() / ".config" / "opencode" / "skills" / "okf-generator"
    target_file = target_dir / "SKILL.md"

    if not SKILL_SOURCE.exists():
        # running from PyPI wheel — SKILL.md bundled inside package dir
        alt = Path(__file__).resolve().parent / "SKILL.md"
        if alt.exists():
            src = alt
        else:
            print("SKILL.md not found — reinstall okf-generator (v0.1.6+)", file=sys.stderr)
            sys.exit(1)
    else:
        src = SKILL_SOURCE

    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, target_file)
    print(f"Installed Claude Code skill → {target_file}")
    print("Restart Claude Code for it to take effect.")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print(__doc__)
        print("Usage: okf <command> [args]")
        print("")
        print("Commands:")
        print("  generate        Generate OKF bundle from a codebase")
        print("  lookup          Look up concepts in a bundle")
        print("  pairs           Convert bundle to JSONL training pairs")
        print("  summarize       Regenerate SUMMARY.md from existing bundle")
        print("  install-skill   Install Claude Code skill")
        sys.exit(0)

    cmd, rest = sys.argv[1], sys.argv[2:]
    sys.argv = [f"okf {cmd}"] + rest   # rewrite argv for sub-parsers

    if cmd == "install-skill":
        _install_skill()

    elif cmd == "generate":
        # Handle --summarize flag routed here too
        if rest and rest[0] == "--summarize":
            sys.argv = ["okf generate", "--summarize"] + rest[1:]
        from okf.generator import main as _main
        _main()

    elif cmd == "summarize":
        # Sugar: `okf summarize <bundle>` → generator --summarize <bundle>
        sys.argv = ["okf generate", "--summarize"] + rest
        from okf.generator import main as _main
        _main()

    elif cmd == "lookup":
        from okf.lookup import main as _main
        _main()

    elif cmd == "pairs":
        from okf.pairs import main as _main
        _main()

    else:
        print(f"Unknown command: {cmd!r}", file=sys.stderr)
        print("Run `okf --help` for available commands.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
