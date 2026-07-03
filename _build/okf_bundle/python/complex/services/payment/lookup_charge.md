---
description: Look up a previously processed charge by its identifier.
resource: python/complex/services/payment.py
tags:
- lang:python
- type:Function
- module:python
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:18Z'
title: lookup_charge
type: Function
---

# lookup_charge

Look up a previously processed charge by its identifier.

## Signature

```python
def lookup_charge(self, charge_id: str, idempotency_key: str | None) -> PaymentResult | None
```

## Docstring

Look up a previously processed charge by its identifier.

Args:
    charge_id: The charge UUID returned by ``process_payment``.
    idempotency_key: Optional key to narrow the search.

Returns:
    The ``PaymentResult`` if found, or None.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |
| `charge_id` | `str` | `—` |
| `idempotency_key` | `str | None` | `—` |

## Returns
`PaymentResult | None`

## Source
Lines 107–122 in `python/complex/services/payment.py`

## Related

- [PaymentService](/python/complex/services/payment/PaymentService.md)

## Called By

- [get_charge](/python/complex/api/get_charge.md)
