"""okf agent — interactive REPL over your knowledge bundle.

Multi-turn chat with persistent sessions, slash commands for
concept lookup/source/calls, and session export.

Usage:
  okf agent                    # interactive REPL
  okf agent --bundle ./path    # custom bundle path
"""

import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SESSION_DIR = Path.home() / ".okf" / "sessions"

# ── Session persistence ──────────────────────────────────────────────────


def _session_path(session_id: str = "") -> Path:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    if session_id:
        return SESSION_DIR / f"{session_id}.json"
    # generate new id
    return SESSION_DIR / f"ses_{uuid.uuid4().hex[:12]}.json"


def _load_session(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_session(session: dict):
    session["updated"] = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path = _session_path(session.get("id", ""))
    path.write_text(json.dumps(session, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def _list_sessions() -> list[dict]:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    sessions = []
    for p in sorted(SESSION_DIR.glob("ses_*.json"), key=os.path.getmtime, reverse=True)[:20]:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            sessions.append({
                "id": data.get("id", p.stem),
                "created": data.get("created", ""),
                "updated": data.get("updated", ""),
                "messages": len(data.get("messages", [])),
                "path": str(p),
            })
        except Exception:
            pass
    return sessions


# ── Slash command handlers ───────────────────────────────────────────────


def _resolve_name(args: list[str], recent: list[dict]) -> str:
    """Get concept name from args or last recent concept."""
    if args:
        return " ".join(args)
    if recent:
        return recent[-1].get("title", "")
    return ""


def _do_lookup(name: str, concepts: list[dict]) -> str:
    from okf.lookup import search, fmt_full
    results = search(concepts, tokens=name.split(), limit=5)
    if not results:
        return f"  No concept found for: {name}"
    # exact match first
    exacts = [c for c in results if c["title"].lower() == name.lower()]
    targets = exacts or results[:1]
    return "\n".join(fmt_full(c) for c in targets)


def _do_source(name: str, concepts: list[dict], bundle_dir: Path) -> str:
    from okf.lookup import search
    results = search(concepts, tokens=name.split(), limit=5)
    if not results:
        return f"  No concept found for: {name}"
    exacts = [c for c in results if c["title"].lower() == name.lower()]
    c = (exacts or results)[0]
    resource = c.get("resource", "")
    src_lines = c.get("sections", {}).get("source", "")
    if not src_lines:
        return f"  No source section for {c['title']}"
    # try to read actual source
    if resource:
        src_path = bundle_dir / resource
        if not src_path.exists():
            src_path = bundle_dir.parent / resource
        if src_path.exists():
            try:
                lines = src_path.read_text(encoding="utf-8", errors="replace").splitlines()
                ln = src_lines
                m = re.search(r"Lines (\d+)", ln)
                if m:
                    start, end = int(m.group(1)), 0
                    m2 = re.search(r"–(\d+)", ln)
                    if m2:
                        end = int(m2.group(1))
                    snippet = lines[max(0, start - 1):end] if end else lines[start - 1:start + 20]
                    return f"  Source: {resource}\n\n" + "\n".join(snippet)
            except Exception:
                pass
    # fallback: show the source section text
    return f"  Source: {resource}\n\n{src_lines}"


def _do_related(name: str, concepts: list[dict]) -> str:
    from okf.lookup import search
    results = search(concepts, tokens=name.split(), limit=5)
    if not results:
        return f"  No concept found for: {name}"
    exacts = [c for c in results if c["title"].lower() == name.lower()]
    c = (exacts or results)[0]
    rel = c.get("sections", {}).get("relationships", "") or c.get("sections", {}).get("related", "")
    if not rel:
        return f"  No relationships for {c['title']}"
    return f"  Relationships for {c['title']}:\n\n{rel}"


def _do_calls(name: str, concepts: list[dict]) -> str:
    from okf.lookup import search
    results = search(concepts, tokens=name.split(), limit=5)
    if not results:
        return f"  No concept found for: {name}"
    exacts = [c for c in results if c["title"].lower() == name.lower()]
    c = (exacts or results)[0]
    rel = c.get("sections", {}).get("relationships", "") or ""
    calls = [line for line in rel.splitlines() if "| calls" in line.lower() or "| calls |" in line]
    if not calls:
        return f"  {c['title']} does not call any other concepts"
    lines = [f"  Calls from {c['title']}:"]
    for cl in calls:
        m = re.search(r"\[([^\]]+)\]", cl)
        lines.append(f"    → {m.group(1) if m else cl}")
    return "\n".join(lines)


def _do_called_by(name: str, concepts: list[dict]) -> str:
    from okf.lookup import search
    results = search(concepts, tokens=name.split(), limit=5)
    if not results:
        return f"  No concept found for: {name}"
    exacts = [c for c in results if c["title"].lower() == name.lower()]
    c = (exacts or results)[0]
    rel = c.get("sections", {}).get("relationships", "") or ""
    calls = [line for line in rel.splitlines() if "| called_by" in line.lower()]
    if not calls:
        return f"  No concepts call {c['title']}"
    lines = [f"  Called by {c['title']}:"]
    for cl in calls:
        m = re.search(r"\[([^\]]+)\]", cl)
        lines.append(f"    ← {m.group(1) if m else cl}")
    return "\n".join(lines)


# ── Main REPL ────────────────────────────────────────────────────────────


def main():
    bundle_dir = Path("okf_bundle").resolve()
    resume_session = ""
    args = sys.argv[1:]

    for i, a in enumerate(args):
        if a == "--bundle" and i + 1 < len(args):
            bundle_dir = Path(args[i + 1]).resolve()
        elif a == "--resume" and i + 1 < len(args):
            resume_session = args[i + 1]
        elif a in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)

    if not bundle_dir.exists():
        print(f"Bundle not found: {bundle_dir}", file=sys.stderr)
        print("Generate one first: okf generate", file=sys.stderr)
        sys.exit(1)

    from okf.config import load as load_config, _get
    cfg = load_config()
    api_key = _get(cfg, "llm.api_key", "")
    base_url = _get(cfg, "llm.base_url", "http://localhost:8080/v1")
    model = _get(cfg, "llm.model", "local-model")
    max_tokens = int(_get(cfg, "llm.max_tokens", 2000))

    from okf.lookup import load_bundle
    concepts = load_bundle(bundle_dir)

    client = None
    if api_key:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)

    # ── Session state ──
    session = {
        "id": uuid.uuid4().hex[:12],
        "created": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated": "",
        "bundle_path": str(bundle_dir),
        "messages": [],
        "recent_concepts": [],
    }

    if resume_session:
        loaded = _load_session(_session_path(resume_session))
        if loaded:
            session = loaded
            print(f"  Resumed session {resume_session} ({len(session.get('messages', []))//2} exchanges)")
        else:
            print(f"  Session {resume_session} not found", file=sys.stderr)

    def _update_recent(results: list[dict]):
        seen = {c.get("concept_id", "") for c in session["recent_concepts"]}
        for c in results:
            cid = c.get("concept_id", "")
            if cid and cid not in seen:
                session["recent_concepts"].append({"title": c["title"], "concept_id": cid, "type": c["type"]})
                seen.add(cid)
        session["recent_concepts"] = session["recent_concepts"][-10:]

    def _fmt_usage(u: dict) -> str:
        parts = [f"{u.get('total', 0)} total"]
        if u.get("reasoning"):
            parts.append(f"{u.get('reasoning')} reasoning")
        return " · ".join(parts)

    # ── Slash command dispatch ──
    def _handle_slash(cmd: str, rest: list[str]) -> tuple[str, bool]:
        nonlocal session
        if cmd in ("exit", "quit"):
            return "", True
        if cmd == "help":
            return (
                "  Commands:\n"
                "    /lookup <name>      — full detail card\n"
                "    /source <name>      — show source code\n"
                "    /calls [name]       — show what this calls\n"
                "    /called-by [name]   — show what calls this\n"
                "    /related [name]     — show relationships\n"
                "    /save [name]        — save session (default: auto-save)\n"
                "    /export [json|md]   — export session to file\n"
                "    /sessions           — list saved sessions\n"
                "    /resume <id>        — resume a saved session\n"
                "    /history            — show conversation\n"
                "    /clear              — clear conversation context\n"
                "    /help               — this message\n"
                "    /exit               — quit"
            ), False
        if cmd == "save":
            name = " ".join(rest) if rest else ""
            p = _save_session(session)
            return f"  Session saved: {p.name}", False
        if cmd == "export":
            fmt = rest[0].lower() if rest else "md"
            export_path = SESSION_DIR / f"{session['id']}.{fmt}"
            if fmt == "json":
                export_path.write_text(json.dumps(session, indent=2, ensure_ascii=False), encoding="utf-8")
            else:
                lines = [f"# OKF Agent Session: {session['id']}\n"]
                lines.append(f"Date: {session['created']}\n")
                for role, text in session.get("messages", []):
                    prefix = "**Q:**" if role == "user" else "**A:**"
                    lines.append(f"\n{prefix}\n\n{text}\n")
                export_path.write_text("\n".join(lines), encoding="utf-8")
            return f"  Exported: {export_path}", False
        if cmd == "sessions":
            sessions = _list_sessions()
            if not sessions:
                return "  No saved sessions.", False
            rows = ["  Saved sessions:"]
            for s in sessions[:10]:
                rows.append(f"    {s['id']:14s} {s.get('updated','')[:19]:20s} {s['messages']//2} exchanges")
            return "\n".join(rows), False
        if cmd == "resume":
            if not rest:
                return "  Usage: /resume <session_id>", False
            sid = rest[0]
            loaded = _load_session(_session_path(sid))
            if not loaded:
                return f"  Session {sid} not found.", False
            session = loaded
            return f"  Resumed session {sid} ({len(session.get('messages', []))//2} exchanges)", False
        if cmd == "history":
            msgs = session.get("messages", [])
            if not msgs:
                return "  No conversation history.", False
            lines = ["  Conversation:"]
            for role, text in msgs[-10:]:
                preview = text[:100].replace("\n", " ")
                prefix = "  Q:" if role == "user" else "  A:"
                lines.append(f"{prefix} {preview}")
                lines.append("  ---")
            return "\n".join(lines), False
        if cmd == "clear":
            session["messages"] = []
            return "  Conversation cleared.", False

        # concept-aware commands
        name = _resolve_name(rest, session.get("recent_concepts", []))
        if not name:
            return "  Usage: /{cmd} <name> (or mention a concept first)".format(cmd=cmd), False

        if cmd == "lookup":
            return _do_lookup(name, concepts), False
        if cmd == "source":
            return _do_source(name, concepts, bundle_dir), False
        if cmd == "related":
            return _do_related(name, concepts), False
        if cmd == "calls":
            return _do_calls(name, concepts), False
        if cmd == "called-by":
            return _do_called_by(name, concepts), False

        return f"  Unknown command: /{cmd}. Try /help", False

    # ── REPL loop ──
    print("OKF Agent — interactive REPL. Type /help for commands, /exit to quit.\n")

    if session.get("messages"):
        print(f"  ({len(session['messages'])//2} previous messages in session)\n")

    total_usage = {"prompt": 0, "completion": 0, "total": 0, "reasoning": 0}
    auto_save = True

    while True:
        try:
            line = input("❯ ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue

        # ── Slash command ──
        if line.startswith("/"):
            parts = line[1:].split()
            cmd = parts[0].lower()
            rest = parts[1:]
            output, should_exit = _handle_slash(cmd, rest)
            if should_exit:
                break
            if output:
                print(output)
            continue

        # ── LLM question ──
        if not client:
            print("  No LLM configured. Set llm.api_key in .okfconfig.")
            print("  Use /lookup, /source, /related for static queries.\n")
            continue

        from okf.ask import _search_context, _ask_llm

        context, results, term_u = _search_context(concepts, line.split(), client, model)
        for k in total_usage:
            total_usage[k] += term_u.get(k, 0)

        if not context:
            print("  No relevant concepts found. Try different keywords or /lookup.\n")
            continue

        answer, ans_u = _ask_llm(client, model, line, context, session.get("messages", []), max_tokens)
        for k in total_usage:
            total_usage[k] += ans_u.get(k, 0)

        session.setdefault("messages", []).append(("user", line))
        session["messages"].append(("assistant", answer))
        _update_recent(results)

        print(f"\n  {answer}\n")
        print("  Sources:")
        for i, c in enumerate(results[:5], 1):
            print(f"    [{i}] {c['type']}: {c['title']} — {c.get('resource', '')}")
        print(f"  Tokens: {_fmt_usage(ans_u)}")
        print()

        if auto_save and len(session.get("messages", [])) % 4 == 0:
            _save_session(session)

    # ── Cleanup ──
    if auto_save and session.get("messages"):
        p = _save_session(session)
        print(f"\n  Session saved: {p.name}")
    if total_usage.get("total", 0):
        print(f"  Session total tokens: {_fmt_usage(total_usage)}")


if __name__ == "__main__":
    main()
