---
concept_id: python/complex/services/payment/lookup_charge
description: Look up a previously processed charge by its identifier.
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
timestamp: '2026-07-10T14:57:28Z'
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

```py
    def lookup_charge(
        self, charge_id: str, idempotency_key: str | None
    ) -> PaymentResult | None:
        """Look up a previously processed charge by its identifier.

        Args:
            charge_id: The charge UUID returned by ``process_payment``.
            idempotency_key: Optional key to narrow the search.

        Returns:
            The ``PaymentResult`` if found, or None.
        """
        for result in self._idempotency_cache.values():
            if result.charge_id == charge_id:
                return result
        return None
```

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentService](/python/complex/services/payment/PaymentService.md) |
| called_by | [get_charge](/python/complex/api/get_charge.md) |
