---
concept_id: python/complex/services/payment/init
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
timestamp: '2026-07-10T17:15:25Z'
title: __init__
type: Function
---

# __init__

## Signature

```python
def __init__(self, message: str, code: str = 'payment_error') -> None
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `message` | `str` | `—` |

| `code` | `str` | `'payment_error'` |

## Returns
`None`

## Source
Lines 24–26 in `python/complex/services/payment.py`

```py
    def __init__(self, message: str, code: str = "payment_error") -> None:
        self.code = code
        super().__init__(message)
```

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentError](/python/complex/services/payment/PaymentError.md) |
