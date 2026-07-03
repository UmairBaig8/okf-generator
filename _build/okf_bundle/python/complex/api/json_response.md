---
description: Decorator that wraps the return value as a JSON-serializable dict.
resource: python/complex/api.py
tags:
- lang:python
- type:Function
- module:python
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:11Z'
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

## Related

- [api](/python/complex/api.md)

## Calls

- [to_dict](/python/complex/services/payment/to_dict.md)
