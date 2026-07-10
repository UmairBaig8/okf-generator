---
concept_id: python/easy_v2/utils/parse_iso_date
description: Safely parse an ISO 8601 date string, returning None on failure.
language: python
okf_version: '0.2'
resource: python/easy_v2/utils.py
tags:
- lang:python
- type:Function
- module:python
- domain:easy_v2
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T18:42:48Z'
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
Lines 61–75 in `python/easy_v2/utils.py`

## Relationships

| Type | Target |
|------|--------|
| related | [utils](/python/easy_v2/utils.md) |
