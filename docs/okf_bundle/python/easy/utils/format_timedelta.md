---
concept_id: python/easy/utils/format_timedelta
description: Format a timedelta into a human-readable string.
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
timestamp: '2026-07-10T17:42:36Z'
title: format_timedelta
type: Function
---

# format_timedelta

Format a timedelta into a human-readable string.

## Signature

```python
def format_timedelta(delta: timedelta, precision: int = 2) -> str
```

## Docstring

Format a timedelta into a human-readable string.

Args:
    delta: The timedelta to format.
    precision: Number of most significant units to show (default 2).

Returns:
    String like ``"3 days, 4 hours"`` or ``"5 minutes, 10 seconds"``.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `delta` | `timedelta` | `—` |

| `precision` | `int` | `2` |

## Returns
`str`

## Source
Lines 78–101 in `python/easy/utils.py`

## Relationships

| Type | Target |
|------|--------|
| related | [utils](/python/easy/utils.md) |
