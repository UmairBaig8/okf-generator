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
timestamp: '2026-07-10T15:03:07Z'
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

```py
    def __init__(self, api_key: str, idempotency_ttl_seconds: int = 3600) -> None:
        if not api_key:
            raise ValueError("API key is required")
        self._api_key = api_key
        self._idempotency_ttl = idempotency_ttl_seconds
        self._idempotency_cache: dict[str, PaymentResult] = {}
```

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentService](/python/complex/services/payment/PaymentService.md) |
