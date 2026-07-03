---
resource: python/complex/services/payment.py
tags:
- lang:python
- type:Function
- module:python
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:18Z'
title: _generate_idempotency_key
type: Function
---

# _generate_idempotency_key

## Signature

```python
def _generate_idempotency_key(self, customer_id: str, amount_cents: int) -> str
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |
| `customer_id` | `str` | `—` |
| `amount_cents` | `int` | `—` |

## Returns
`str`

## Source
Lines 124–126 in `python/complex/services/payment.py`

## Related

- [PaymentService](/python/complex/services/payment/PaymentService.md)

## Called By

- [process_payment](/python/complex/services/payment/process_payment.md)
