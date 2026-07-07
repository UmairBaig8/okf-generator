"""Convert an OKF bundle directly into training pairs (build_pairs.py format).

Reads every concept .md file from an OKF bundle and generates multiple
training pair types — richer than extract.py because OKF carries signatures,
cross-links, method lists, param tables, and LLM-enriched descriptions.

Pair types generated per concept:

  codegen      "Write a class/function that does X"  →  signature + docstring
  qa           categorized Q&A (purpose/params/return/edge)
  doc          code context  →  generate the docstring/description
  summarize    module/class  →  one-paragraph summary
  crosslink    "What does X relate to?"  →  linked concepts

Output: JSONL in the same format as build_pairs.py (drop-in replacement).

Config via env vars:
  SYNTH_API_KEY      API key
  SYNTH_BASE_URL     API base URL (default: http://localhost:8080/v1)
  SYNTH_MODEL        model name
  SKIP_SYNTH=1       skip API, static pairs only
  QA_PER_CONCEPT     Q&A pairs per concept (default: 3)
  MAX_WORKERS        parallel workers (default: 3)
  PAIR_TYPES         comma-separated subset, e.g. "codegen,qa,doc"
                     default: all types
  LOG_LEVEL          default: INFO

Usage:
  python okf_to_pairs.py <okf_bundle_dir> [output_file]

  okf_bundle_dir   path to the OKF bundle (output of okf_generator.py)
  output_file      where to write JSONL (default: ./okf_pairs.jsonl)
"""

import json
import logging
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml
from tqdm import tqdm

log = logging.getLogger("okf_pairs")

# ---------------------------------------------------------------------------
# OKF concept reader
# ---------------------------------------------------------------------------

def parse_okf_file(path: Path) -> dict | None:
    """Parse a single OKF .md file into a dict. Returns None if invalid."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        log.debug(f"Cannot read {path}: {e}")
        return None

    # Must start with ---
    if not text.startswith("---"):
        return None

    # Split frontmatter from body
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None

    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        log.debug(f"YAML error in {path}: {e}")
        return None

    # OKF conformance: type is required
    if not fm.get("type"):
        return None

    body = parts[2].strip()

    # Parse body sections into structured dict
    sections = _parse_body_sections(body)

    return {
        "type": fm.get("type", ""),
        "title": fm.get("title", path.stem),
        "description": fm.get("description", ""),
        "resource": fm.get("resource", ""),
        "tags": fm.get("tags", []),
        "timestamp": fm.get("timestamp", ""),
        "body": body,
        "sections": sections,
        # concept_id = path relative to bundle_dir, without .md extension
        # resolved later in load_bundle where we have bundle_dir context
        "concept_id": "",  # set by load_bundle
        "source_file": str(path),
    }


def _parse_body_sections(body: str) -> dict:
    """Extract named sections from markdown body."""
    sections = {}
    current_section = None
    current_lines = []

    for line in body.splitlines():
        if line.startswith("## "):
            if current_section:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = line[3:].strip().lower()
            current_lines = []
        else:
            if current_section is not None:
                current_lines.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections


def load_bundle(bundle_dir: Path) -> list[dict]:
    """Load all concept files from an OKF bundle."""
    concepts = []
    skipped = 0
    reserved = {"index.md", "log.md"}

    for md_file in sorted(bundle_dir.rglob("*.md")):
        if md_file.name in reserved:
            continue
        concept = parse_okf_file(md_file)
        if concept is None:
            skipped += 1
            continue
        # skip Index/Log types
        if concept["type"] in {"Index", "Log"}:
            continue
        # set concept_id from path relative to bundle_dir (no .md extension)
        rel = md_file.relative_to(bundle_dir)
        concept["concept_id"] = str(rel.with_suffix("")).replace(os.sep, "/")
        concepts.append(concept)

    if skipped:
        log.warning(f"Skipped {skipped} non-conformant or reserved files")
    return concepts


def build_cross_link_map(concepts: list[dict], bundle_dir: Path) -> dict[str, dict]:
    """Build concept_id → concept lookup for cross-link resolution."""
    return {c["concept_id"]: c for c in concepts}


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

CODEGEN_SYNTH_PROMPT = """\
Given this code concept, write ONE instruction that asks someone to implement it.

Rules:
- Do NOT mention the exact function/class name.
- Focus on behavior, inputs, outputs.
- Imperative voice ("Write a function that...").
- Max 25 words.
- Return ONLY the instruction, nothing else.

Type: {type}
Title: {title}
Description: {description}
Signature: {signature}
"""

QA_PROMPT = """\
Generate exactly {n} question-answer pairs about this code concept.
Cover these categories (one each): purpose, params, return, edge

Rules:
- Questions must reference specific names, values, or logic from THIS concept.
- Answers must mention at least one identifier (variable, param, class name).
- Answers: 1-2 sentences max.
- Format: JSON array of {{"question": "...", "answer": "...", "category": "..."}}
- Reply with ONLY the JSON array.

Type: {type}
Title: {title}
Description: {description}
Signature: {signature}
Methods: {methods}
Params: {params}
Returns: {returns}
"""

DOC_PROMPT = """\
Given this code concept's signature and context, write a concise docstring.

Rules:
- First line: one-sentence summary of what it does.
- If it has params, add an Args section.
- If it returns something, add a Returns section.
- Be specific, not generic.
- Return ONLY the docstring text (no quotes, no markdown).

Type: {type}
Title: {title}
Signature: {signature}
Params: {params}
Returns: {returns}
Description hint: {description}
"""

SUMMARIZE_PROMPT = """\
Write a one-paragraph summary (3-5 sentences) of this code concept for a developer.

Be specific: mention key methods, what it connects to, and what problem it solves.
Return ONLY the paragraph, nothing else.

Type: {type}
Title: {title}
Description: {description}
Methods: {methods}
Related: {related}
Body excerpt:
{body_excerpt}
"""


# ---------------------------------------------------------------------------
# Pair builders
# ---------------------------------------------------------------------------

def _system(lang: str, role: str) -> str:
    return f"You are an expert {lang} {role}. Be precise and concise."


def _lang(concept: dict) -> str:
    tags = concept.get("tags") or []
    for t in tags:
        stripped = t.removeprefix("lang:")
        if stripped in {"python", "javascript", "typescript", "go", "java", "rust"}:
            return stripped
    return "python"


def _sig(concept: dict) -> str:
    return re.sub(r"```\w*\n?", "", concept["sections"].get("signature", "")).strip()


def _methods(concept: dict) -> str:
    m = concept["sections"].get("methods", "")
    # extract method names from markdown list
    names = re.findall(r"`(\w+)`", m)
    return ", ".join(names) if names else "none"


def _params(concept: dict) -> str:
    p = concept["sections"].get("parameters", "")
    if not p:
        return "none"
    # extract from markdown table
    rows = [line for line in p.splitlines() if line.startswith("|") and "---" not in line and "Name" not in line]
    params = []
    for row in rows:
        cols = [c.strip().strip("`") for c in row.split("|") if c.strip()]
        if cols:
            params.append(cols[0])
    return ", ".join(params) if params else "none"


def _returns(concept: dict) -> str:
    r = concept["sections"].get("returns", "")
    return r.replace("`", "").strip() or "none"


def _related(concept: dict) -> str:
    r = concept["sections"].get("related", "")
    names = re.findall(r"\[([^\]]+)\]", r)
    return ", ".join(names) if names else "none"


def make_static_codegen(concept: dict) -> dict | None:
    """Static codegen pair from description + signature (no LLM needed)."""
    desc = concept.get("description", "").strip()
    sig = _sig(concept)
    if not desc or not sig:
        return None

    instruction = f"Write a {concept['type'].lower()} that: {desc}"
    answer = sig
    doc = concept["sections"].get("docstring", "")
    if doc:
        answer += f'\n    """{doc}"""'

    lang = _lang(concept)
    return {
        "type": "codegen",
        "pair_source": "okf_static",
        "language": lang,
        "source": concept.get("resource", ""),
        "symbol": concept.get("title", ""),
        "okf_concept_id": concept.get("concept_id", ""),
        "messages": [
            {"role": "system", "content": _system(lang, "programmer. Generate clean, correct code.")},
            {"role": "user", "content": instruction},
            {"role": "assistant", "content": answer},
        ],
    }


def make_static_summarize(concept: dict) -> dict | None:
    """Static summarize pair for modules/classes."""
    if concept["type"] not in {"Module", "Class"}:
        return None
    desc = concept.get("description", "").strip()
    methods = _methods(concept)
    if not desc:
        return None

    question = f"Give me a summary of the `{concept['title']}` {concept['type'].lower()}."
    answer_parts = [desc]
    if methods != "none":
        answer_parts.append(f"It provides the following methods: {methods}.")
    related = _related(concept)
    if related != "none":
        answer_parts.append(f"Related concepts: {related}.")

    lang = _lang(concept)
    return {
        "type": "summarize",
        "pair_source": "okf_static",
        "language": lang,
        "source": concept.get("resource", ""),
        "symbol": concept.get("title", ""),
        "okf_concept_id": concept.get("concept_id", ""),
        "messages": [
            {"role": "system", "content": _system(lang, "code analyst.")},
            {"role": "user", "content": question},
            {"role": "assistant", "content": " ".join(answer_parts)},
        ],
    }


def make_static_crosslink(concept: dict, link_map: dict) -> dict | None:
    """Static cross-link pair — what does X relate to and why."""
    related_text = concept["sections"].get("related", "")
    names = re.findall(r"\[([^\]]+)\]", related_text)
    if not names:
        return None

    question = f"What concepts are related to `{concept['title']}` and why?"
    answer_parts = [f"`{concept['title']}` is related to:"]
    for name in names[:5]:
        answer_parts.append(f"- `{name}`")
    answer = "\n".join(answer_parts)

    lang = _lang(concept)
    return {
        "type": "crosslink",
        "pair_source": "okf_static",
        "language": lang,
        "source": concept.get("resource", ""),
        "symbol": concept.get("title", ""),
        "okf_concept_id": concept.get("concept_id", ""),
        "messages": [
            {"role": "system", "content": _system(lang, "code analyst.")},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ],
    }


# ---------------------------------------------------------------------------
# LLM-based pair generators
# ---------------------------------------------------------------------------

def extract_json_array(raw: str) -> list:
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())
    try:
        result = json.loads(raw)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass
    return []


def call_with_retry(fn, max_retries=3, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            if attempt == max_retries - 1:
                log.debug(f"API call failed after {max_retries} retries: {e}")
                return None
            time.sleep(base_delay * (2 ** attempt))
    return None


def llm_codegen(concept: dict, client, model: str) -> dict | None:
    prompt = CODEGEN_SYNTH_PROMPT.format(
        type=concept["type"],
        title=concept["title"],
        description=concept.get("description", ""),
        signature=_sig(concept),
    )
    def _call():
        return client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150, temperature=0.1,
        )
    resp = call_with_retry(_call)
    if not resp:
        return None
    instruction = (resp.choices[0].message.content or "").strip()
    if not instruction:
        return None

    sig = _sig(concept)
    doc = concept["sections"].get("docstring", "")
    answer = sig + (f'\n    """{doc}"""' if doc else "")
    lang = _lang(concept)
    return {
        "type": "codegen",
        "pair_source": "okf_llm",
        "language": lang,
        "source": concept.get("resource", ""),
        "symbol": concept["title"],
        "okf_concept_id": concept.get("concept_id", ""),
        "messages": [
            {"role": "system", "content": _system(lang, "programmer. Generate clean, correct code.")},
            {"role": "user", "content": instruction},
            {"role": "assistant", "content": answer},
        ],
    }


def llm_qa(concept: dict, client, model: str, n: int = 3) -> list[dict]:
    prompt = QA_PROMPT.format(
        n=n,
        type=concept["type"],
        title=concept["title"],
        description=concept.get("description", ""),
        signature=_sig(concept),
        methods=_methods(concept),
        params=_params(concept),
        returns=_returns(concept),
    )
    def _call():
        return client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800, temperature=0.2,
        )
    resp = call_with_retry(_call)
    if not resp:
        return []

    raw_pairs = extract_json_array(resp.choices[0].message.content or "")
    lang = _lang(concept)
    result = []
    for p in raw_pairs:
        q = p.get("question", "").strip()
        a = p.get("answer", "").strip()
        cat = p.get("category", "").strip()
        if not q or not a:
            continue
        result.append({
            "type": "qa",
            "pair_source": "okf_llm",
            "language": lang,
            "source": concept.get("resource", ""),
            "symbol": concept["title"],
            "category": cat,
            "okf_concept_id": concept.get("concept_id", ""),
            "messages": [
                {"role": "system", "content": _system(lang, "code analyst.")},
                {"role": "user", "content": q},
                {"role": "assistant", "content": a},
            ],
        })
    return result


def llm_doc(concept: dict, client, model: str) -> dict | None:
    sig = _sig(concept)
    if not sig:
        return None
    prompt = DOC_PROMPT.format(
        type=concept["type"],
        title=concept["title"],
        signature=sig,
        params=_params(concept),
        returns=_returns(concept),
        description=concept.get("description", ""),
    )
    def _call():
        return client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300, temperature=0.15,
        )
    resp = call_with_retry(_call)
    if not resp:
        return None
    docstring = resp.choices[0].message.content.strip()
    if not docstring:
        return None

    lang = _lang(concept)
    question = f"Write a docstring for `{concept['title']}`.\n\n```\n{sig}\n```"
    return {
        "type": "doc",
        "pair_source": "okf_llm",
        "language": lang,
        "source": concept.get("resource", ""),
        "symbol": concept["title"],
        "okf_concept_id": concept.get("concept_id", ""),
        "messages": [
            {"role": "system", "content": _system(lang, "documentation writer.")},
            {"role": "user", "content": question},
            {"role": "assistant", "content": docstring},
        ],
    }


def llm_summarize(concept: dict, client, model: str) -> dict | None:
    if concept["type"] not in {"Module", "Class"}:
        return None
    body_excerpt = concept.get("body", "")[:600]
    prompt = SUMMARIZE_PROMPT.format(
        type=concept["type"],
        title=concept["title"],
        description=concept.get("description", ""),
        methods=_methods(concept),
        related=_related(concept),
        body_excerpt=body_excerpt,
    )
    def _call():
        return client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300, temperature=0.2,
        )
    resp = call_with_retry(_call)
    if not resp:
        return None
    summary = resp.choices[0].message.content.strip()
    if not summary:
        return None

    lang = _lang(concept)
    question = f"Summarize the `{concept['title']}` {concept['type'].lower()} for a developer."
    return {
        "type": "summarize",
        "pair_source": "okf_llm",
        "language": lang,
        "source": concept.get("resource", ""),
        "symbol": concept["title"],
        "okf_concept_id": concept.get("concept_id", ""),
        "messages": [
            {"role": "system", "content": _system(lang, "code analyst.")},
            {"role": "user", "content": question},
            {"role": "assistant", "content": summary},
        ],
    }


# ---------------------------------------------------------------------------
# Per-concept processor
# ---------------------------------------------------------------------------

def process_concept(
    concept: dict,
    client,
    model: str,
    link_map: dict,
    qa_per_concept: int,
    pair_types: set[str],
) -> list[dict]:
    pairs = []

    # --- Static pairs (no LLM) ---
    if "codegen" in pair_types:
        p = make_static_codegen(concept)
        if p:
            pairs.append(p)

    if "summarize" in pair_types:
        p = make_static_summarize(concept)
        if p:
            pairs.append(p)

    if "crosslink" in pair_types:
        p = make_static_crosslink(concept, link_map)
        if p:
            pairs.append(p)

    # --- LLM pairs ---
    if client:
        if "codegen" in pair_types:
            p = llm_codegen(concept, client, model)
            if p:
                pairs.append(p)

        if "qa" in pair_types:
            pairs.extend(llm_qa(concept, client, model, n=qa_per_concept))

        if "doc" in pair_types and concept["type"] in {"Function", "Class"}:
            p = llm_doc(concept, client, model)
            if p:
                pairs.append(p)

        if "summarize" in pair_types and concept["type"] in {"Module", "Class"}:
            p = llm_summarize(concept, client, model)
            if p:
                pairs.append(p)

    return pairs


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


def main():
    setup_logging()

    if len(sys.argv) < 2 or (len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help")):
        print(__doc__)
        sys.exit(0)

    # --bundle flag overrides positional, otherwise default ./okf_bundle
    bundle_dir = Path("okf_bundle").resolve()
    out_file = Path("okf_pairs.jsonl").resolve()
    skip_next = False
    for i, a in enumerate(sys.argv[1:], 1):
        if skip_next:
            skip_next = False
            continue
        if a == "--bundle" and i + 1 < len(sys.argv):
            bundle_dir = Path(sys.argv[i + 1]).resolve()
            skip_next = True
        elif not a.startswith("-"):
            # First non-flag positional = bundle_dir, second = output
            if str(bundle_dir) == str(Path("okf_bundle").resolve()):
                bundle_dir = Path(a).resolve()
            else:
                out_file = Path(a).resolve()

    if not bundle_dir.exists():
        log.error(f"Bundle directory not found: {bundle_dir}")
        sys.exit(1)

    # --- Config (from .okfconfig) ---
    from okf.config import load as load_config, _get
    _pcfg = load_config()
    skip_synth  = "--skip-synth" in sys.argv or "-s" in sys.argv
    api_key     = _get(_pcfg, "llm.api_key", "")
    base_url    = _get(_pcfg, "llm.base_url", "http://localhost:8080/v1")
    model       = _get(_pcfg, "llm.model", "local-model")
    qa_n        = int(_get(_pcfg, "pairs.qa_per_concept", 3))
    max_workers = int(_get(_pcfg, "pairs.max_workers", 3))
    types_env   = _get(_pcfg, "pairs.pair_types", "codegen,qa,doc,summarize,crosslink")
    pair_types  = set(t.strip() for t in types_env.split(","))

    log.info(f"Bundle:     {bundle_dir}")
    log.info(f"Output:     {out_file}")
    log.info(f"Pair types: {', '.join(sorted(pair_types))}")

    # --- Load bundle ---
    log.info("Loading OKF bundle...")
    concepts = load_bundle(bundle_dir)
    log.info(f"Loaded {len(concepts)} concepts")

    if not concepts:
        log.error("No concepts found. Is this a valid OKF bundle?")
        sys.exit(1)

    link_map = build_cross_link_map(concepts, bundle_dir)

    # --- LLM client ---
    client = None
    if not skip_synth:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=base_url)
            log.info(f"LLM: {model} @ {base_url}")
            log.info(f"QA/concept: {qa_n} | workers: {max_workers}")
        except ImportError:
            log.warning("openai not installed — static pairs only")

    # --- Process ---
    stats = {"total": 0, "errors": 0}
    type_counts: dict[str, int] = {}

    out_file.parent.mkdir(parents=True, exist_ok=True)

    with open(out_file, "w", encoding="utf-8") as f:
        if client and max_workers > 1:
            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {
                    pool.submit(
                        process_concept, c, client, model, link_map, qa_n, pair_types
                    ): c for c in concepts
                }
                for future in tqdm(as_completed(futures), total=len(futures), desc="Converting"):
                    try:
                        pairs = future.result()
                        for p in pairs:
                            f.write(json.dumps(p, ensure_ascii=False) + "\n")
                            f.flush()
                            type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1
                            stats["total"] += 1
                    except Exception as e:
                        log.debug(f"Error: {e}")
                        stats["errors"] += 1
        else:
            for concept in tqdm(concepts, desc="Converting"):
                try:
                    pairs = process_concept(concept, client, model, link_map, qa_n, pair_types)
                    for p in pairs:
                        f.write(json.dumps(p, ensure_ascii=False) + "\n")
                        f.flush()
                        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1
                        stats["total"] += 1
                except Exception as e:
                    log.debug(f"Error: {e}")
                    stats["errors"] += 1

    # --- Summary ---
    print(f"\n{'='*50}")
    print(f"  Concepts processed: {len(concepts)}")
    print(f"  {'Pair type':<15} {'Count':>8}")
    print(f"  {'-'*24}")
    for t, count in sorted(type_counts.items()):
        print(f"  {t:<15} {count:>8}")
    print(f"  {'─'*24}")
    print(f"  {'TOTAL':<15} {stats['total']:>8}")
    if stats["errors"]:
        print(f"  Errors: {stats['errors']}")
    print(f"{'='*50}")
    log.info(f"Saved → {out_file}")


if __name__ == "__main__":
    main()
