---
description: 'Factory: create a service instance pre-configured from settings.'
resource: python/complex/services/payment.py
tags:
- lang:python
- type:Function
- module:python
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:18Z'
title: from_settings
type: Function
---

# from_settings

Factory: create a service instance pre-configured from settings.

## Signature

```python
def from_settings(cls, api_key: str) -> 'PaymentService'
```

## Decorators

- `classmethod`

## Docstring

Factory: create a service instance pre-configured from settings.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `cls` | `—` | `—` |
| `api_key` | `str` | `—` |

## Returns
`'PaymentService'`

## Source
Lines 134–136 in `python/complex/services/payment.py`

## Related

- [PaymentService](/python/complex/services/payment/PaymentService.md)
