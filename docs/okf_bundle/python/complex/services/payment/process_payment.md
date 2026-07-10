---
concept_id: python/complex/services/payment/process_payment
description: Submit a payment to the external gateway.
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

```py
    def process_payment(
        self,
        customer_id: str,
        amount_cents: int,
        currency: str,
        metadata: dict | None = None,
        idempotency_key: str | None = None,
    ) -> PaymentResult:
        """Submit a payment to the external gateway.

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
        """
        idem_key = idempotency_key or self._generate_idempotency_key(customer_id, amount_cents)
        cached = self._idempotency_cache.get(idem_key)
        if cached:
            return cached

        charge_id = f"ch_{uuid.uuid4().hex}"
        signature = self._sign_payload(f"{customer_id}:{amount_cents}:{currency}")

        result = PaymentResult(
            charge_id=charge_id,
            status=PaymentStatus.SUCCEEDED,
            amount_cents=amount_cents,
            currency=currency,
            gateway_response=signature,
        )
        self._idempotency_cache[idem_key] = result
        return result
```

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentService](/python/complex/services/payment/PaymentService.md) |
| calls | [_sign_payload](/python/complex/services/payment/sign_payload.md) |
| calls | [PaymentResult](/python/complex/services/payment/PaymentResult.md) |
| calls | [_generate_idempotency_key](/python/complex/services/payment/generate_idempotency_key.md) |
| called_by | [charge](/python/complex/api/charge.md) |
