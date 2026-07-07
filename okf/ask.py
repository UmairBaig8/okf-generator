"""okf ask — LLM-powered Q&A over your knowledge bundle.

Asks a natural language question about your codebase. The bundle is searched
for relevant concepts, then sent as context to the configured LLM for an answer.

Without a question, enters interactive chat mode.

Requires an LLM provider configured in .okfconfig (llm.api_key, llm.base_url).

Usage:
  okf ask "how does the payment service work"
  okf ask "what dependencies does this project use" --bundle ./my_bundle
  okf ask                          # interactive chat mode
"""

import sys
from pathlib import Path

from okf.lookup import search

STOP_WORDS = {
    "how", "does", "do", "is", "are", "was", "were", "the", "a", "an",
    "in", "on", "at", "to", "for", "of", "with", "by", "and", "or",
    "it", "its", "what", "where", "when", "why", "which", "who", "that",
    "this", "these", "those", "i", "you", "we", "they", "he", "she",
    "me", "my", "your", "all", "can", "will", "would", "could", "should",
    "has", "have", "had", "been", "being", "am", "are", "was", "were",
    "get", "got", "find", "show", "list", "tell", "describe", "explain",
}


def _search_context(concepts, query_parts, llm_client=None, llm_model=None):
    """Search bundle and build context string from top results.
    
    Uses LLM to extract search terms if available, otherwise falls back to stop word filtering.
    Returns (context_string, results, term_usage_dict).
    """
    query = " ".join(query_parts)
    term_usage = {}
    
    # Try LLM-based term extraction first
    tokens = None
    if llm_client and llm_model:
        try:
            term_prompt = f"""Extract 2-5 key search terms from this question about a codebase.
Return ONLY a JSON object with a "terms" key containing an array of strings.
No preamble, no markdown, no reasoning. Just the JSON.
Example: {{"terms": ["payment", "service", "api"]}}
Question: {query}"""
            resp = llm_client.chat.completions.create(
                model=llm_model, messages=[{"role": "user", "content": term_prompt}],
                max_tokens=500, temperature=0.1,
            )
            import json, re
            raw = (resp.choices[0].message.content or "").strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw).strip()
            data = json.loads(raw)
            terms = data.get("terms", [])
            if terms:
                tokens = [t for t in terms if isinstance(t, str) and t.strip()]
            u = resp.usage
            if u:
                term_usage = {
                    "prompt": u.prompt_tokens,
                    "completion": u.completion_tokens,
                    "total": u.total_tokens,
                    "reasoning": (u.completion_tokens_details.reasoning_tokens or 0) if u.completion_tokens_details else 0,
                }
        except Exception:
            pass
    
    # Fallback: stop word filtering
    if not tokens:
        tokens = [t for t in query_parts if t.lower() not in STOP_WORDS]
        if not tokens:
            tokens = query_parts[-3:]
    
    results = search(concepts, tokens=tokens, limit=8)
    context_parts = []
    for c in results:
        sig = c.get("sections", {}).get("signature", "")
        desc = c.get("description", "")
        related = c.get("sections", {}).get("related", "")[:200]
        entry = f"--- {c['type']}: {c['title']} ---\nFile: {c.get('resource', '')}\nDescription: {desc}\nSignature: {sig}\nRelated: {related}"
        context_parts.append(entry)
    return "\n\n".join(context_parts), results, term_usage


def _ask_llm(client, model, question, context, messages, max_tokens=2000):
    """Send question + context to LLM. Returns (answer, usage_dict)."""
    system = f"""You are a codebase expert. Answer based on the context below.
If the context doesn't contain enough information, say so.

Context from the knowledge bundle:
{context}"""
    msgs = [{"role": "system", "content": system}]
    for role, text in messages:
        msgs.append({"role": role, "content": text})
    msgs.append({"role": "user", "content": question})

    resp = client.chat.completions.create(
        model=model, messages=msgs, max_tokens=max_tokens, temperature=0.1,
    )
    answer = (resp.choices[0].message.content or "").strip()
    u = resp.usage
    usage = {
        "prompt": u.prompt_tokens if u else 0,
        "completion": u.completion_tokens if u else 0,
        "total": u.total_tokens if u else 0,
        "reasoning": (u.completion_tokens_details.reasoning_tokens or 0) if u and u.completion_tokens_details else 0,
    }
    return answer, usage


def main():
    if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    bundle_dir = Path("okf_bundle").resolve()
    query_parts = []
    skip_next = False
    for i, a in enumerate(sys.argv[1:], 1):
        if skip_next:
            skip_next = False
            continue
        if a == "--bundle" and i + 1 < len(sys.argv):
            bundle_dir = Path(sys.argv[i + 1]).resolve()
            skip_next = True
        elif not a.startswith("-"):
            query_parts.append(a)

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

    if not api_key:
        print("No LLM configured. Set llm.api_key in .okfconfig.", file=sys.stderr)
        print("Without an LLM, use okf lookup instead for static search.", file=sys.stderr)
        sys.exit(1)

    from okf.lookup import load_bundle, search
    concepts = load_bundle(bundle_dir)

    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)

    def _fmt_usage(u):
        parts = [f"{u['total']} total"]
        if u.get("reasoning"):
            parts.append(f"{u['reasoning']} reasoning")
        return " · ".join(parts)

    # ── Interactive chat mode ──
    if not query_parts:
        print("OKF Ask — interactive chat. Type your questions or /exit.\n")
        history = []
        total_usage = {"prompt": 0, "completion": 0, "total": 0, "reasoning": 0}
        while True:
            try:
                q = input(">>> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not q:
                continue
            if q.lower() in ("/exit", "/quit", "exit", "quit"):
                break
            context, results, term_u = _search_context(concepts, q.split(), client, model)
            for k in total_usage:
                total_usage[k] += term_u.get(k, 0)
            if not context:
                print("  No relevant concepts found. Try different keywords.\n")
                continue
            answer, ans_u = _ask_llm(client, model, q, context, history, max_tokens)
            for k in total_usage:
                total_usage[k] += ans_u.get(k, 0)
            history.append(("user", q))
            history.append(("assistant", answer))
            print(f"\n  {answer}\n")
            print("Sources:")
            for i, c in enumerate(results[:5], 1):
                desc = c.get("description", "")[:60]
                print(f"  [{i}] {c['type']}: {c['title']} — {c.get('resource', '')}")
            print(f"  Tokens: {_fmt_usage(ans_u)}")
            print()
        if total_usage["total"]:
            print(f"  Session total: {_fmt_usage(total_usage)}")
        return

    # ── Single question mode ──
    context, results, term_u = _search_context(concepts, query_parts, client, model)
    if not context:
        print(f"No relevant concepts found for: {' '.join(query_parts)}")
        print("Try different keywords or check the bundle is up to date.")
        sys.exit(1)

    answer, ans_u = _ask_llm(client, model, " ".join(query_parts), context, [], max_tokens)
    total_u = {k: term_u.get(k, 0) + ans_u.get(k, 0) for k in ("prompt", "completion", "total", "reasoning")}
    print(f"\n  Q: {' '.join(query_parts)}\n")
    print(answer)
    print(f"\nSources:")
    for i, c in enumerate(results[:10], 1):
        desc = c.get("description", "")[:80]
        desc_str = f" — {desc}" if desc else ""
        print(f"  [{i}] {c['type']}: {c['title']}{desc_str}")
        print(f"      {c.get('resource', '')}")
    print(f"\n  Tokens: {_fmt_usage(total_u)}")
    print(f"  Run okf lookup <Name> for full detail.")
