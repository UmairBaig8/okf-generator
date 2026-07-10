---
concept_id: python/easy/utils/merge_dicts
description: Merge two dictionaries, with ``overlay`` values taking priority.
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
timestamp: '2026-07-10T18:29:30Z'
title: merge_dicts
type: Function
---

# merge_dicts

Merge two dictionaries, with ``overlay`` values taking priority.

## Signature

```python
def merge_dicts(base: dict, overlay: dict, deep: bool = True) -> dict
```

## Docstring

Merge two dictionaries, with ``overlay`` values taking priority.

Args:
    base: Base dictionary.
    overlay: Overlay dictionary whose values override base values.
    deep: If True, recursively merge nested dictionaries (default True).

Returns:
    New merged dictionary (neither input is mutated).

## Parameters

| Name | Type | Default |
|------|------|---------|
| `base` | `dict` | `—` |

| `overlay` | `dict` | `—` |

| `deep` | `bool` | `True` |

## Returns
`dict`

## Source
Lines 104–121 in `python/easy/utils.py`

## Relationships

| Type | Target |
|------|--------|
| related | [utils](/python/easy/utils.md) |
