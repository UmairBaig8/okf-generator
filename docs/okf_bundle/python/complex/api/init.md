---
concept_id: python/complex/api/init
language: python
okf_version: '0.2'
resource: python/complex/api.py
tags:
- lang:python
- type:Function
- module:python
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: __init__
type: Function
---

# __init__

## Signature

```python
def __init__(self, service: PaymentService | None = None) -> None
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `service` | `PaymentService | None` | `None` |

## Returns
`None`

## Source
Lines 43–44 in `python/complex/api.py`

```py
    def __init__(self, service: PaymentService | None = None) -> None:
        self._service = service or PaymentService(api_key=settings.payment_gateway_key)
```

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentAPI](/python/complex/api/PaymentAPI.md) |
