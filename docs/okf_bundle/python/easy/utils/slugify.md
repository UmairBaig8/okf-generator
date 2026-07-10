---
concept_id: python/easy/utils/slugify
description: Convert arbitrary text into a URL-safe slug.
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
timestamp: '2026-07-10T18:42:48Z'
title: slugify
type: Function
---

# slugify

Convert arbitrary text into a URL-safe slug.

## Signature

```python
def slugify(text: str, max_length: int = 80) -> str
```

## Docstring

Convert arbitrary text into a URL-safe slug.

Args:
    text: Input string to slugify.
    max_length: Maximum length of the resulting slug (default 80).

Returns:
    Lowercase slug with non-alphanumeric characters replaced by hyphens.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `text` | `str` | `—` |

| `max_length` | `int` | `80` |

## Returns
`str`

## Source
Lines 11–24 in `python/easy/utils.py`

## Relationships

| Type | Target |
|------|--------|
| related | [utils](/python/easy/utils.md) |
