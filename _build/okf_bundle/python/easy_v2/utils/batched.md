---
description: Split items into batches (v2 — renamed from chunk_list with different
  default).
resource: python/easy_v2/utils.py
tags:
- lang:python
- type:Function
- module:python
- domain:easy_v2
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T19:06:59Z'
title: batched
type: Function
---

# batched

Split items into batches (v2 — renamed from chunk_list with different default).

## Signature

```python
def batched(items: Sequence[T], chunk_size: int = 50) -> list[list[T]]
```

## Docstring

Split items into batches (v2 — renamed from chunk_list with different default).

## Parameters

| Name | Type | Default |
|------|------|---------|
| `items` | `Sequence[T]` | `—` |
| `chunk_size` | `int` | `50` |

## Returns
`list[list[T]]`

## Source
Lines 124–126 in `python/easy_v2/utils.py`

## Related

- [utils](/python/easy_v2/utils.md)
