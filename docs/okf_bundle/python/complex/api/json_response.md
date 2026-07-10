---
concept_id: python/complex/api/json_response
description: Decorator that wraps the return value as a JSON-serializable dict.
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
timestamp: '2026-07-10T19:13:46Z'
title: json_response
type: Function
---

# json_response

Decorator that wraps the return value as a JSON-serializable dict.

## Signature

```python
def json_response(func)
```

## Docstring

Decorator that wraps the return value as a JSON-serializable dict.

Expects the wrapped function to return a dict or a Pydantic-like model
with a ``to_dict()`` method.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `func` | `—` | `—` |

## Source
Lines 16–37 in `python/complex/api.py`

## Relationships

| Type | Target |
|------|--------|
| related | [api](/python/complex/api.md) |
| calls | [to_dict](/python/complex/services/payment/to_dict.md) |
| calls | [error](/php/complex/User/error.md) |
