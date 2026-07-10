---
concept_id: python/complex/api/charge
description: Charge a customer a given amount.
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
timestamp: '2026-07-10T14:57:28Z'
title: charge
type: Function
---

# charge

Charge a customer a given amount.

## Signature

```python
def charge(self, customer_id: str, amount_cents: int, currency: str = 'USD', metadata: dict | None = None) -> dict
```

## Decorators

- `json_response`

## Docstring

Charge a customer a given amount.

Args:
    customer_id: Unique identifier for the customer.
    amount_cents: Amount in the smallest currency unit.
    currency: Three-letter ISO 4217 currency code.
    metadata: Optional key-value pairs to attach to the charge.

Returns:
    A dict containing the payment result fields.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `customer_id` | `str` | `—` |

| `amount_cents` | `int` | `—` |

| `currency` | `str` | `'USD'` |

| `metadata` | `dict | None` | `None` |

## Returns
`dict`

## Source
Lines 52–78 in `python/complex/api.py`

```py
    def charge(
        self,
        customer_id: str,
        amount_cents: int,
        currency: str = "USD",
        metadata: dict | None = None,
    ) -> dict:
        """Charge a customer a given amount.

        Args:
            customer_id: Unique identifier for the customer.
            amount_cents: Amount in the smallest currency unit.
            currency: Three-letter ISO 4217 currency code.
            metadata: Optional key-value pairs to attach to the charge.

        Returns:
            A dict containing the payment result fields.
        """
        if amount_cents <= 0:
            raise PaymentError("Amount must be a positive integer.")
        result = self._service.process_payment(
            customer_id=customer_id,
            amount_cents=amount_cents,
            currency=currency.upper(),
            metadata=metadata or {},
        )
        return result.to_dict()
```

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentAPI](/python/complex/api/PaymentAPI.md) |
| calls | [process_payment](/python/complex/services/payment/process_payment.md) |
| calls | [to_dict](/python/complex/services/payment/to_dict.md) |
