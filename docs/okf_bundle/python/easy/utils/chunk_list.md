---
concept_id: python/easy/utils/chunk_list
description: Split a sequence into fixed-size chunks.
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
timestamp: '2026-07-10T19:27:26Z'
title: chunk_list
type: Function
---

# chunk_list

Split a sequence into fixed-size chunks.

## Signature

```python
def chunk_list(items: Sequence[T], chunk_size: int = 100) -> list[list[T]]
```

## Docstring

Split a sequence into fixed-size chunks.

Args:
    items: Sequence of items to chunk.
    chunk_size: Maximum number of items per chunk (default 100).

Returns:
    List of chunks, each a list of up to ``chunk_size`` items.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `items` | `Sequence[T]` | `—` |

| `chunk_size` | `int` | `100` |

## Returns
`list[list[T]]`

## Source
Lines 27–37 in `python/easy/utils.py`

## Relationships

| Type | Target |
|------|--------|
| related | [utils](/python/easy/utils.md) |
