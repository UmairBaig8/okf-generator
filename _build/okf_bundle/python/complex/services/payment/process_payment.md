---
description: Submit a payment to the external gateway.
resource: python/complex/services/payment.py
tags:
- lang:python
- type:Function
- module:python
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:18Z'
title: process_payment
type: Function
---

# process_payment

Submit a payment to the external gateway.

## Signature

```python
def process_payment(self, customer_id: str, amount_cents: int, currency: str, metadata: dict | None = None, idempotency_key: str | None = None) -> PaymentResult
```

## Docstring

Submit a payment to the external gateway.

Args:
    customer_id: The customer to charge.
    amount_cents: Amount in the smallest currency unit.
    currency: ISO 4217 currency code.
    metadata: Optional additional data for the gateway.
    idempotency_key: Unique key to prevent duplicate charges.

Returns:
    A ``PaymentResult`` describing the outcome.

Raises:
    PaymentError: If the gateway rejects the payment.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |
| `customer_id` | `str` | `—` |
| `amount_cents` | `int` | `—` |
| `currency` | `str` | `—` |
| `metadata` | `dict | None` | `None` |
| `idempotency_key` | `str | None` | `None` |

## Returns
`PaymentResult`

## Source
Lines 66–105 in `python/complex/services/payment.py`

## Related

- [PaymentService](/python/complex/services/payment/PaymentService.md)

## Calls

- [_sign_payload](/python/complex/services/payment/sign_payload.md)
- [PaymentResult](/python/complex/services/payment/PaymentResult.md)
- [_generate_idempotency_key](/python/complex/services/payment/generate_idempotency_key.md)

## Called By

- [charge](/python/complex/api/charge.md)
