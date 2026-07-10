---
concept_id: python/easy/utils/parse_iso_date
description: Safely parse an ISO 8601 date string, returning None on failure.
language: python
okf_version: '0.2'
resource: python/easy/utils.py
tags:
- lang:python
- type:Function
- module:python
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: parse_iso_date
type: Function
---

# parse_iso_date

Safely parse an ISO 8601 date string, returning None on failure.

## Signature

```python
def parse_iso_date(value: str | None) -> datetime | None
```

## Docstring

Safely parse an ISO 8601 date string, returning None on failure.

Args:
    value: ISO 8601 date string or None.

Returns:
    Parsed datetime, or None if the input is None or unparseable.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `value` | `str | None` | `—` |

## Returns
`datetime | None`

## Source
Lines 61–75 in `python/easy/utils.py`

```py
def parse_iso_date(value: str | None) -> datetime | None:
    """Safely parse an ISO 8601 date string, returning None on failure.

    Args:
        value: ISO 8601 date string or None.

    Returns:
        Parsed datetime, or None if the input is None or unparseable.
    """
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None
```

## Relationships

| Type | Target |
|------|--------|
| related | [utils](/python/easy/utils.md) |
