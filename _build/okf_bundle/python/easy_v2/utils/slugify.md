---
description: Convert arbitrary text into a URL-safe slug.
resource: python/easy_v2/utils.py
tags:
- lang:python
- type:Function
- module:python
- domain:easy_v2
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T19:06:59Z'
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
Lines 11–24 in `python/easy_v2/utils.py`

## Related

- [utils](/python/easy_v2/utils.md)
