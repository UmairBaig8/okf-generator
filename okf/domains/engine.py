"""Domain classification engine — re-classifies YAML concepts using
data-driven rule files. Users provide rules as YAML/JSON files; the engine
matches concepts against rules and applies type/field/link transformations.

Usage:
    from okf.domains.engine import classify, load_rules
    rules = load_rules(domain_names=["crossplane"], user_files=[".okf/domains/mine.yaml"])
    concepts = classify(concepts, rules)
"""

import fnmatch
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

from okf.parsers.base import Concept

log = logging.getLogger("okf_gen")

# ── Built-in rules directory ────────────────────────────────────────────────

_BUILTIN_RULES_DIR = Path(__file__).resolve().parent / "rules"


def _discover_builtin() -> list[tuple[str, Path]]:
    """Scan okf/domains/rules/*.{yaml,yml,json} and return (domain_key, path) pairs."""
    results = []
    if not _BUILTIN_RULES_DIR.exists():
        return results
    for f in sorted(_BUILTIN_RULES_DIR.iterdir()):
        if f.suffix in (".yaml", ".yml", ".json") and f.is_file():
            data = _load_file(f)
            if isinstance(data, dict) and "domain" in data:
                results.append((data["domain"], f))
    return results


def _discover_project_local() -> list[tuple[str, Path]]:
    """Scan .okf/domains/*.{yaml,yml,json} for project-specific overrides."""
    results = []
    project_rules = Path.cwd() / ".okf" / "domains"
    if project_rules.exists():
        for f in sorted(project_rules.iterdir()):
            if f.suffix in (".yaml", ".yml", ".json") and f.is_file():
                data = _load_file(f)
                if isinstance(data, dict) and "domain" in data:
                    results.append((data["domain"], f))
    return results


def _load_file(path: Path) -> Any:
    try:
        if path.suffix in (".yaml", ".yml"):
            import yaml as _yaml
            return _yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
        else:
            import json as _json
            return _json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        log.warning(f"Failed to load rule file {path}: {e}")
        return {}


def _load_rules_from_path(path: Path) -> list[dict]:
    """Load a single rule file and return its rules list."""
    data = _load_file(path)
    if not isinstance(data, dict):
        log.warning(f"Rule file {path} is not a mapping, skipping")
        return []
    rules = data.get("rules", [])
    domain = data.get("domain", "unknown")
    for r in rules:
        r.setdefault("_domain", domain)
        r.setdefault("_source", str(path))
    return rules


def load_rules(
    domain_names: list[str] | None = None,
    user_files: list[Path] | None = None,
) -> list[dict]:
    """Load and merge rules from three sources (in order):

    1. Built-in: okf/domains/rules/*.{yaml,yml,json}
    2. Project-local: .okf/domains/*.{yaml,yml,json}
    3. CLI ―user_files: explicit --domain-rules paths

    If *domain_names* is given, only rules whose ``domain`` key matches
    (case-sensitive) are included.  User rules with the same ``domain`` key
    override built-in rules for that domain; user rules with a new domain key
    are additive.

    Returns a flat list of rule dicts, each decorated with ``_domain`` and
    ``_source``.
    """
    domain_names = domain_names or []
    domain_set = set(domain_names)

    # 1. Built-in
    builtin_rules: list[dict] = []
    for domain_key, path in _discover_builtin():
        if domain_set and domain_key not in domain_set:
            continue
        builtin_rules.extend(_load_rules_from_path(path))

    # 2. Project-local overrides
    project_rules: list[dict] = []
    for domain_key, path in _discover_project_local():
        if domain_set and domain_key not in domain_set:
            continue
        project_rules.extend(_load_rules_from_path(path))

    # 3. CLI user files
    cli_rules: list[dict] = []
    for path in (user_files or []):
        p = Path(path)
        if p.exists():
            cli_rules.extend(_load_rules_from_path(p))

    # Merge: project rules with same domain override built-in
    project_domains = {r["_domain"] for r in project_rules}
    merged = [r for r in builtin_rules if r["_domain"] not in project_domains]
    merged.extend(project_rules)
    merged.extend(cli_rules)

    log.debug(f"Domain rules loaded: {len(merged)} rules from {len(domain_set or ['all'])} domain(s)")
    return merged


# ── Matcher ─────────────────────────────────────────────────────────────────

def _matches_conditions(doc: dict, match: dict) -> bool:
    """Check if a parsed YAML doc matches all conditions in *match*.

    Supported operators:
      - Exact string: ``{"kind": "Composition"}``
      - Glob: ``{"apiVersion": {"$glob": "apiextensions.crossplane.io/*"}}``
      - Regex: ``{"kind": {"$regex": "^X.*"}}``
      - Catch-all: ``{"default": true}``
      - require_keys: ``{"require_keys": ["apiVersion", "kind"]}``
      - has_key: ``{"has_key": "spec.resources"}`` (presence check)
    """
    if match.get("default"):
        require_keys = match.get("require_keys", [])
        if require_keys:
            for k in require_keys:
                if k not in doc:
                    return False
        return True

    for key, pattern in match.items():
        if key in ("default", "require_keys"):
            continue
        if key == "has_key":
            # Presence check — doc must have this key at any depth
            keys = pattern if isinstance(pattern, list) else [pattern]
            for required_key in keys:
                if _deep_get(doc, required_key) is None:
                    return False
            continue

        actual = _deep_get(doc, key)
        if actual is None:
            return False
        if isinstance(pattern, dict):
            if "$glob" in pattern:
                if not fnmatch.fnmatch(str(actual), str(pattern["$glob"])):
                    return False
            elif "$regex" in pattern:
                import re
                if not re.search(str(pattern["$regex"]), str(actual)):
                    return False
            else:
                if actual != pattern:
                    return False
        else:
            if str(actual) != str(pattern):
                return False

    return True


def _deep_get(doc: Any, dotted: str) -> Any:
    """Resolve ``spec.compositeTypeRef.apiVersion`` against a nested dict.

    Supports:
      - ``.`` nesting: ``spec.group``
      - ``[N]`` index: ``spec.versions[0].name``
      - ``[*]`` wildcard: ``spec.versions[*].name``
    """
    if not isinstance(doc, dict) and not isinstance(doc, list):
        return None

    # Split on first dot, but handle bracket notation before it
    parts = dotted.split(".", 1)
    first = parts[0]

    # Check if this segment has bracket notation
    bracket_start = first.find("[")
    key = first[:bracket_start] if bracket_start >= 0 else first

    if isinstance(doc, list):
        # We're in a list — index directly
        try:
            idx = int(key)
            item = doc[idx] if idx < len(doc) else doc[0]
        except (ValueError, IndexError):
            return None
        rest_part = dotted.split(".", 1)[1] if "." in dotted else ""
        if not rest_part:
            return item
        return _deep_get(item, rest_part)

    # dict path
    if key:
        val = doc.get(key)
    else:
        val = doc

    if bracket_start >= 0:
        # Extract the index spec
        bracket_end = first.find("]")
        index_spec = first[bracket_start + 1:bracket_end]
        rest_from_first = first[bracket_end + 1:]  # anything after ]

        if index_spec == "*":
            if isinstance(val, list) and val:
                val = val[0]
            else:
                return None
        else:
            try:
                idx = int(index_spec)
                if isinstance(val, list) and idx < len(val):
                    val = val[idx]
                else:
                    return None
            except (ValueError, IndexError, TypeError):
                return None

        # If there was content after bracket (like .name), append to rest
        if rest_from_first.startswith("."):
            rest_from_first = rest_from_first[1:]
        if rest_from_first:
            rest = f"{rest_from_first}.{parts[1]}" if len(parts) > 1 else rest_from_first
        else:
            rest = parts[1] if len(parts) > 1 else ""
    else:
        rest = parts[1] if len(parts) > 1 else ""

    if not rest:
        return val
    return _deep_get(val, rest)


def _extract_field(doc: dict, path: str) -> Any:
    """Extract a dot-path value from a dict.  Supports ``[*]`` wildcard."""
    return _deep_get(doc, path)


# ── Classifier ─────────────────────────────────────────────────────────────

def classify(concepts: list[Concept], rules: list[dict]) -> list[Concept]:
    """Run domain classification rules against concept list.

    Each concept with ``body_extra.yaml_doc`` is matched against rules
    in order (first-match-wins).  Matched rules may:
      - Change concept type
      - Add tags
      - Extract YAML fields into concept fields
      - Register link targets for the linker pass

    After reclassification, a linker pass resolves cross-concept references.

    Audit: logs a summary of rule matches so users can verify their rules
    are being applied as expected.
    """
    # Build index by concept_id for linker
    by_id = {c.concept_id: c for c in concepts}

    # Track links to resolve in a second pass
    pending_links: list[tuple[Concept, dict, list]] = []  # (concept, link_config, extracted_values)

    # Audit counters
    audit: dict[str, int] = {}  # rule name → match count
    unmatched_concepts: list[str] = []
    matched_concepts: list[str] = []

    for c in concepts:
        yaml_doc = c.body_extra.get("yaml_doc") if c.body_extra else None
        if not isinstance(yaml_doc, dict):
            continue

        matched = False
        for rule in rules:
            match_block = rule.get("match", {})
            if not _matches_conditions(yaml_doc, match_block):
                continue

            rule_name = rule.get("name", rule.get("type", "unnamed"))
            audit[rule_name] = audit.get(rule_name, 0) + 1
            matched_concepts.append(c.concept_id)
            matched = True

            # Apply type override
            new_type = rule.get("type")
            if new_type:
                c.type = new_type

            # Apply tags
            for tag in rule.get("add_tags", []):
                if tag not in c.tags:
                    c.tags.append(tag)

            # Extract fields
            for ext in rule.get("extract", []):
                if isinstance(ext, dict):
                    from_path = ext.get("from", "")
                    to_field = ext.get("to", "")
                    val = _extract_field(yaml_doc, from_path)
                    if val is not None:
                        if to_field == "signature":
                            c.signature = str(val) if not c.signature else c.signature
                        elif to_field == "returns":
                            c.returns = str(val)
                        elif to_field == "fields":
                            if isinstance(val, dict):
                                c.fields = [{"name": k, "type": str(v.get("type", "")), "visibility": ""}
                                            for k, v in val.items()]
                            elif isinstance(val, str):
                                if val not in [f["name"] for f in c.fields]:
                                    c.fields.append({"name": val, "type": "string", "visibility": ""})
                            elif isinstance(val, list):
                                for item in val:
                                    if isinstance(item, str) and item not in [f["name"] for f in c.fields]:
                                        c.fields.append({"name": item, "type": "string", "visibility": ""})
                        elif to_field == "description" and not c.description:
                            c.description = str(val)

            # Collect links for second pass
            for link_conf in rule.get("links", []):
                field = link_conf.get("field", "")
                val = _extract_field(yaml_doc, field)
                if val is not None:
                    pending_links.append((c, link_conf, val))

            # First-match-wins
            break

        if not matched:
            unmatched_concepts.append(c.concept_id)

    # Log audit summary
    _log_audit(audit, matched_concepts, unmatched_concepts, rules)

    # ── Linker pass ──────────────────────────────────────────────────────
    # Build hash index for link targets
    # index: (attr_path, value) → [concept]
    link_idx: dict[tuple[str, str], list[Concept]] = defaultdict(list)
    for c in concepts:
        for match_on in ["name", "apiVersion", "kind"]:
            if match_on == "name":
                link_idx[("name", c.title.lower())].append(c)
            elif match_on == "kind":
                link_idx[("kind", c.title)].append(c)
            elif match_on == "apiVersion":
                link_idx[("apiVersion", c.signature.split("/")[0] if c.signature else "")].append(c)
        # Index by tag:domain too
        for t in c.tags:
            if t.startswith("domain:"):
                link_idx[("domain", t.split(":", 1)[1])].append(c)

    for src_concept, link_conf, field_val in pending_links:
        match_on = link_conf.get("match_on", ["name"])

        if isinstance(field_val, dict):
            # e.g. compositeTypeRef: {apiVersion: "example.org/v1", kind: "XPostgreSQLInstance"}
            lookup_values = []
            for mo in match_on:
                v = field_val.get(mo)
                if v:
                    lookup_values.append((mo, str(v)))
                if lookup_values:
                    candidate_ids = [c_id for c_id in by_id
                                     if _concept_matches_all(c_id, lookup_values, by_id)]
                    for candidate_id in candidate_ids:
                        if candidate_id != src_concept.concept_id:
                            if candidate_id not in src_concept.related:
                                src_concept.related.append(candidate_id)

        elif isinstance(field_val, str):
            for mo in match_on:
                candidates = link_idx.get((mo, field_val.lower() if mo == "name" else field_val), [])
                for candidate in candidates:
                    if candidate is not None and candidate.concept_id != src_concept.concept_id:
                        if candidate.concept_id not in src_concept.related:
                            src_concept.related.append(candidate.concept_id)

    return concepts


def _concept_matches_all(concept_id: str, lookup_values: list[tuple[str, str]],
                         by_id: dict[str, Concept]) -> bool:
    c = by_id.get(concept_id)
    if not c:
        return False
    for attr, val in lookup_values:
        if attr == "kind":
            if c.title != val:
                return False
        elif attr == "apiVersion":
            # Check signature (extracted), then body_extra.yaml_doc (original)
            sig_api = c.signature.split("/")[0] if c.signature else ""
            if sig_api == val:
                continue
            yaml_doc = c.body_extra.get("yaml_doc") if c.body_extra else {}
            if yaml_doc.get("apiVersion") == val:
                continue
            return False
        elif attr == "name":
            if c.title.lower() != val.lower():
                return False
        elif attr == "group":
            if c.returns != val:
                return False
    return True


# ── Audit ───────────────────────────────────────────────────────────────────

def _log_audit(audit: dict[str, int], matched: list[str],
               unmatched: list[str], rules: list[dict]) -> None:
    """Log a summary of rule matches so users can verify rule application."""
    log.info(
        f"Domain classification audit: {sum(audit.values())} concepts matched, "
        f"{len(unmatched)} unmatched"
    )
    if log.isEnabledFor(logging.DEBUG) or True:
        # Always log at INFO the rule breakdown
        for rule_name, count in sorted(audit.items(), key=lambda x: -x[1]):
            log.info(f"  Rule [{rule_name}] matched {count} concept(s)")


# ── Validation ──────────────────────────────────────────────────────────────

def validate_rule_file(path: Path) -> list[str]:
    """Validate a rule file against the expected schema.

    Returns a list of error messages (empty = valid).
    """
    errors: list[str] = []

    if not path.exists():
        return [f"File not found: {path}"]

    if path.suffix not in (".yaml", ".yml", ".json"):
        return [f"Unsupported file format: {path.suffix}. Use .yaml, .yml, or .json"]

    data = _load_file(path)
    if not isinstance(data, dict):
        return [f"Root must be a mapping (dict), got {type(data).__name__}"]

    domain = data.get("domain")
    if not domain or not isinstance(domain, str):
        errors.append("Missing or invalid 'domain' field (must be a non-empty string)")

    rules = data.get("rules", [])
    if not isinstance(rules, list):
        errors.append("'rules' must be a list")
        return errors

    if not rules:
        errors.append("'rules' list is empty — add at least one rule")

    for i, rule in enumerate(rules):
        prefix = f"rules[{i}]"
        if not isinstance(rule, dict):
            errors.append(f"{prefix}: must be a mapping (dict), got {type(rule).__name__}")
            continue

        match = rule.get("match")
        if not match:
            errors.append(f"{prefix}: missing 'match' block (required)")
            continue
        if not isinstance(match, dict):
            errors.append(f"{prefix}.match: must be a mapping")

        # Check for invalid match operators
        if isinstance(match, dict):
            for k, v in match.items():
                if k in ("default", "require_keys", "has_key"):
                    continue
                if isinstance(v, dict):
                    for op in v:
                        if op not in ("$glob", "$regex"):
                            msg = f"{prefix}.match.{k}: unknown operator '{op}'. Use $glob or $regex."
                            errors.append(msg)

        # Check extract paths
        for j, ext in enumerate(rule.get("extract", [])):
            if not isinstance(ext, dict):
                errors.append(f"{prefix}.extract[{j}]: must be a mapping")
                continue
            if "from" not in ext:
                errors.append(f"{prefix}.extract[{j}]: missing 'from' field")
            if "to" not in ext:
                errors.append(f"{prefix}.extract[{j}]: missing 'to' field")
            valid_to = {"signature", "returns", "fields", "description"}
            if ext.get("to") not in valid_to:
                errors.append(
                    f"{prefix}.extract[{j}]: 'to' must be one of {valid_to}"
                )

        # Check link configs
        for j, link in enumerate(rule.get("links", [])):
            if not isinstance(link, dict):
                errors.append(f"{prefix}.links[{j}]: must be a mapping")
                continue
            if "field" not in link:
                errors.append(f"{prefix}.links[{j}]: missing 'field'")
            if "match_on" not in link:
                errors.append(f"{prefix}.links[{j}]: missing 'match_on'")

    return errors


# ── Listing ─────────────────────────────────────────────────────────────────

def list_domains() -> list[dict]:
    """List all discoverable domains with their source."""
    results = []
    seen = set()
    for domain_key, path in _discover_builtin():
        if domain_key not in seen:
            seen.add(domain_key)
            results.append({"domain": domain_key, "source": "builtin", "path": str(path)})
    for domain_key, path in _discover_project_local():
        if domain_key not in seen:
            seen.add(domain_key)
            results.append({"domain": domain_key, "source": "project", "path": str(path)})
        else:
            # Mark as overridden
            for r in results:
                if r["domain"] == domain_key:
                    r["source"] = "project (overrides builtin)"
                    r["path"] = str(path)
    return sorted(results, key=lambda x: x["domain"])
