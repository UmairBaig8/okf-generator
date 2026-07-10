---
concept_id: python/complex/services/payment/PaymentService
description: Core payment service that communicates with the external gateway.
language: python
okf_version: '0.2'
resource: python/complex/services/payment.py
tags:
- lang:python
- type:Class
- module:python
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: PaymentService
type: Class
---

# PaymentService

Core payment service that communicates with the external gateway.

## Docstring

Core payment service that communicates with the external gateway.

Args:
    api_key: Secret API key for authenticating with the gateway.
    idempotency_ttl_seconds: How long to keep idempotency keys in memory.

## Methods

- `__init__`
- `process_payment`
- `lookup_charge`
- `_generate_idempotency_key`
- `_sign_payload`
- `from_settings`

## Source
Lines 51–136 in `python/complex/services/payment.py`

```py
class PaymentService:
    """Core payment service that communicates with the external gateway.

    Args:
        api_key: Secret API key for authenticating with the gateway.
        idempotency_ttl_seconds: How long to keep idempotency keys in memory.
    """

    def __init__(self, api_key: str, idempotency_ttl_seconds: int = 3600) -> None:
        if not api_key:
            raise ValueError("API key is required")
        self._api_key = api_key
        self._idempotency_ttl = idempotency_ttl_seconds
        self._idempotency_cache: dict[str, PaymentResult] = {}

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

    def _generate_idempotency_key(self, customer_id: str, amount_cents: int) -> str:
        raw = f"{customer_id}:{amount_cents}:{uuid.uuid4().hex}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _sign_payload(self, payload: str) -> str:
        return hmac.new(
            self._api_key.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()

    @classmethod
    def from_settings(cls, api_key: str) -> "PaymentService":
        """Factory: create a service instance pre-configured from settings."""
        return cls(api_key=api_key)
```

## Relationships

| Type | Target |
|------|--------|
| related | [payment](/python/complex/services/payment.md) |
| related | [__init__](/python/complex/services/payment/init.md) |
| related | [process_payment](/python/complex/services/payment/process_payment.md) |
| related | [lookup_charge](/python/complex/services/payment/lookup_charge.md) |
| related | [_generate_idempotency_key](/python/complex/services/payment/generate_idempotency_key.md) |
| related | [_sign_payload](/python/complex/services/payment/sign_payload.md) |
| related | [from_settings](/python/complex/services/payment/from_settings.md) |
