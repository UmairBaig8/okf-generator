"""Fast OKF frontmatter serializer.

Replaces ``yaml.safe_dump`` for the fixed OKF v0.2 frontmatter schema.
Handles only ``str``, ``list[str]``, and ``int`` values — all other types
fall back to ``yaml.safe_dump`` for safety.

Every emitted document is validated to round-trip through ``yaml.safe_load``
back to the original dict (see ``tests/test_frontmatter.py``).
"""

import yaml

# YAML 1.1 bare-word keywords that evaluate to non-string types
_YAML_BOOL = frozenset({"true", "false", "yes", "no", "on", "off"})
_YAML_NULL = frozenset({"null", "~"})
_YAML_KEYWORDS = _YAML_BOOL | _YAML_NULL

# Characters inside a value that force YAML double-quoting
_UNSAFE_INNER = frozenset({':', '#', '"', '\'', '*', '&', '!', '|', '>',
                           '%', '@', '`', '{', '}', '[', ']', ',',
                           '\n', '\r'})

# First characters that force YAML double-quoting
_UNSAFE_LEAD = frozenset({'-', '?', '!', '&', '*', '#', '%', '@', '`',
                          '{', '}', '[', ']', ',', ' '})

# Fields excluded from OKF frontmatter — never emitted (runtime-only fields)
_EXCLUDED_FIELDS = frozenset({"calls", "called_by", "possible_calls",
                               "calls_raw", "imports", "related",
                               "related_semantic", "body_extra",
                               "fields", "methods", "params",
                               "source_lines", "type_params",
                               "inheritance", "decorators",
                               "visibility", "docstring",
                               "signature", "returns", "usage_example",
                               "side_effects", "design_pattern",
                               "deprecation_notes", "security",
                               "complexity",
                               })


def _looks_like_number(val: str) -> bool:
    """True if *val* could be parsed as a number, int, or version string."""
    if not val:
        return False
    try:
        float(val)
        return True
    except ValueError:
        pass
    return val.lstrip('-').isdigit()


_DATE_RE = None  # lazy import re

def _looks_like_date(val: str) -> bool:
    """True if *val* looks like a date/timestamp YAML would parse as a date obj."""
    global _DATE_RE
    if _DATE_RE is None:
        import re as _re
        _DATE_RE = _re.compile(
            r'^\d{4}-\d{2}-\d{2}'  # 2026-07-19 or 2026-07-19T12:00:00Z
        )
    return bool(_DATE_RE.match(val))


def _needs_quoting(val: str) -> bool:
    if not val:
        return True
    if val[0] in _UNSAFE_LEAD:
        return True
    if val != val.strip():  # leading or trailing whitespace
        return True
    if any(c in _UNSAFE_INNER for c in val):
        return True
    if val.lower() in _YAML_KEYWORDS:
        return True
    if _looks_like_number(val):
        return True
    if _looks_like_date(val):
        return True
    return False


def _quote(val: str) -> str:
    escaped = val.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'


def _serialize_value(val) -> str:
    if isinstance(val, str):
        if val == "":
            return '""'
        if _needs_quoting(val):
            # Use double-quoted scalar with C-style escapes for special chars
            escaped = (val
                       .replace('\\', '\\\\')
                       .replace('"', '\\"')
                       .replace('\n', '\\n')
                       .replace('\r', '\\r')
                       .replace('\t', '\\t'))
            return f'"{escaped}"'
        return val
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    # Fallback for unsupported types
    return yaml.safe_dump(val, default_flow_style=False).strip()


def dump_frontmatter(metadata: dict) -> str:
    """Serialize an OKF frontmatter dict to a ``---``-delimited YAML block.

    Fast path for the fixed OKF schema (``str`` / ``list[str]`` / ``int``
    values).  Falls back to ``yaml.safe_dump`` if the dict contains
    unexpected types.
    """
    if not metadata:
        return "---\n---\n"

    # Check if all values are supported types — fallback otherwise
    for v in metadata.values():
        if v is not None and not isinstance(v, (str, list, int, float, bool)):
            return "---\n" + yaml.safe_dump(metadata, default_flow_style=False, allow_unicode=True) + "---\n"

    lines = ["---"]
    for key, value in metadata.items():
        if key in _EXCLUDED_FIELDS:
            continue
        if value is None:
            continue
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {_serialize_value(item)}")
        else:
            lines.append(f"{key}: {_serialize_value(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n"
