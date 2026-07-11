---
concept_id: python/complex/api/health_check
description: Return the current health status of the API and its dependencies.
language: python
okf_version: '0.2'
resource: python/complex/api.py
tags:
- lang:python
- type:Function
- module:python
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-11T09:16:36Z'
title: health_check
type: Function
---

# health_check

Return the current health status of the API and its dependencies.

## Signature

```python
def health_check(cls) -> dict
```

## Decorators

- `classmethod`

## Docstring

Return the current health status of the API and its dependencies.

Returns:
    Dict with ``status``, ``timestamp``, and ``version`` keys.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `cls` | `—` | `—` |

## Returns
`dict`

## Source
Lines 93–103 in `python/complex/api.py`

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentAPI](/python/complex/api/PaymentAPI.md) |
