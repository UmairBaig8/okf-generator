"""
okf/enrich/_llm_prompts.py

Prompt templates for LLM-based enrichment modes (base, deep, security, related).
Extracted from generator.py so they live alongside LSP in the enrich package.

WARNING: The {body} and {candidates} template variables are populated from
arbitrary third-party source code.  Do NOT add user-controlled text into
the instruction portion of these prompts — the "system" role is not used
here so the model treats the full message as user input, making prompt-injection
theoretically possible.  The JSON-only output constraint limits the blast radius
to structured fields, and the security/complexity fields carry a built-in
"not proof of safety" caveat.  See AGENTS.md for known limitations.
"""

# Shared security/complexity field spec used by both DEEP_ENRICH_PROMPT and
# SECURITY_PROMPT so they can't drift apart.
_SECURITY_FIELD_SPEC = """\
  "security"       - list ONLY concrete, visible risk patterns in this body:
                      unsanitized input reaching a query/shell/eval/HTML sink,
                      hardcoded secrets, missing auth checks that are visibly
                      absent, unsafe deserialization, etc. Quote the specific
                      line/construct you're flagging. If you see no such pattern,
                      say exactly: "No obvious risk pattern in this body." Do NOT
                      say a concept is "safe" or "secure" — absence of a visible
                      issue is not proof of safety, since you cannot see callers
                      or the full data flow.
  "complexity"     - Big-O time/space ONLY if a clear loop, recursion, or data
                      structure operation is visible in the body (e.g. nested
                      loops, recursive calls). Otherwise return exactly:
                      "Not estimable from this body alone." Do not guess based
                      on the function name or docstring."""

ENRICH_PROMPT = """\
You are enriching an OKF (Open Knowledge Format) knowledge bundle for a codebase.

Given this code concept, return a JSON object with four fields:

  "description"    - one clear sentence (max 20 words) summarising what it does,
                      specific enough to be useful to a developer or AI agent.
  "docstring"      - a full docstring in Google style:
                       - First line: one-sentence summary.
                       - Args section (if it has parameters).
                       - Returns section (if it returns something).
                       - Raises section (if relevant).
                     Omit sections that do not apply.
  "tags"           - 0-4 short semantic tags describing PURPOSE, not language/type
                     (e.g. "auth", "caching", "validation", "io-bound", "parsing").
                     Do not repeat the language, "function", "class", or module name
                     as a tag — those are already recorded elsewhere.
  "design_pattern" - a well-known design pattern name (e.g. "Factory", "Singleton",
                     "Observer", "Strategy", "Decorator") ONLY if the signature,
                     inheritance, or name clearly indicates one. Empty string if
                     none applies or you are not confident — do not force a label.

Rules:
- All fields must reference specific names or behaviour from THIS concept.
- Do NOT invent parameters or return types that are not in the signature.
- If the existing docstring is already detailed (>80 chars), improve it slightly
  rather than replacing it completely.
- Reply with ONLY the JSON object, no markdown fences, no preamble.

Concept type: {type}
Name: {title}
Existing docstring: {docstring}
Signature: {signature}
Parameters: {params}
Returns: {returns}
Inheritance: {inheritance}
"""

# NOTE: {body} is pre-truncated at _MAX_BODY_LINES (= 120 lines) in the
# calling code so that oversized functions don't inflate token cost or
# risk mid-function truncation by the model.
DEEP_ENRICH_PROMPT = """\
You are enriching an OKF (Open Knowledge Format) knowledge bundle for a codebase.

You are given the ACTUAL SOURCE BODY below, not just the signature. Only describe
behaviour you can see directly in this body — do not speculate about callers,
inputs from other files, or runtime conditions not visible here.

Return a JSON object with four fields:

  "usage_example" - a short (2-6 line) realistic code snippet showing how to call
                     this, using only the parameters/return type actually shown.
                     Empty string if the concept has no meaningful call pattern
                     (e.g. a plain data class with no methods).
  "side_effects"   - one sentence on what this mutates, reads/writes (files, env,
                      network, globals), or "Pure — no observable side effects."
                      if the body has none of that. Base this ONLY on the body
                      given; if uncertain, say what is uncertain rather than
                      asserting purity or impurity you can't confirm.

""" + _SECURITY_FIELD_SPEC + """

Reply with ONLY the JSON object, no markdown fences, no preamble.

Concept type: {type}
Name: {title}
Signature: {signature}
Source body:
{body}
"""

SECURITY_PROMPT = """\
You are auditing one code concept for an OKF (Open Knowledge Format) knowledge
bundle. You are given the ACTUAL SOURCE BODY below — only describe patterns
visible in this body; do not speculate about callers or data you cannot see.

Return a JSON object with two fields:

""" + _SECURITY_FIELD_SPEC + """

Reply with ONLY the JSON object, no markdown fences, no preamble.

Type: {type}
Title: {title}
Signature: {signature}
Source body:
{body}
"""

RELATED_PROMPT = """\
You are finding semantically related code concepts for an OKF knowledge bundle.
Given the target concept and a list of CANDIDATES, pick UP TO {top_k} candidate
ids that are genuinely related in purpose or pattern. Do NOT pick candidates
just because they share a tag or directory if the purpose isn't actually related.

Rules:
- Only return ids that appear EXACTLY as given in the candidate list below.
- If nothing is truly related, return an empty list.
- Reply with ONLY a JSON object: {{"related_ids": ["id1", "id2"]}}, no preamble.

Target concept:
type: {type}
title: {title}
description: {description}

Candidates:
{candidates}
"""
