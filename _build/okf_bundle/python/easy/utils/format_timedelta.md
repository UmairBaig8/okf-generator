---
description: Format a timedelta into a human-readable string.
resource: python/easy/utils.py
tags:
- lang:python
- type:Function
- module:python
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:01Z'
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

## Related

- [utils](/python/easy/utils.md)
