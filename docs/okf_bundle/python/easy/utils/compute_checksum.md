---
concept_id: python/easy/utils/compute_checksum
description: Compute hex digest of a string using the specified hash algorithm.
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
title: compute_checksum
type: Function
---

# compute_checksum

Compute hex digest of a string using the specified hash algorithm.

## Signature

```python
def compute_checksum(data: str, algorithm: str = 'sha256') -> str
```

## Docstring

Compute hex digest of a string using the specified hash algorithm.

Args:
    data: Input string to hash.
    algorithm: Hash algorithm name (``sha256``, ``sha1``, ``md5``).

Returns:
    Hex digest string.

Raises:
    ValueError: If the algorithm is not supported by ``hashlib``.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `data` | `str` | `—` |

| `algorithm` | `str` | `'sha256'` |

## Returns
`str`

## Source
Lines 40–58 in `python/easy/utils.py`

## Relationships

| Type | Target |
|------|--------|
| related | [utils](/python/easy/utils.md) |
| calls | [update](/typescript/complex/utils/db/update.md) |
