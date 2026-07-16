---
concept_id: python/complex/services/payment/init_1
language: python
okf_version: '0.2'
resource: python/complex/services/payment.py
tags:
- lang:python
- type:Function
- module:python
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-16T07:24:59Z'
title: __init__
type: Function
---

# __init__

## Signature

```python
def __init__(self, api_key: str, idempotency_ttl_seconds: int = 3600) -> None
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `api_key` | `str` | `—` |

| `idempotency_ttl_seconds` | `int` | `3600` |

## Returns
`None`

## Source
Lines 59–64 in `python/complex/services/payment.py`

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentService](/python/complex/services/payment/PaymentService.md) |
