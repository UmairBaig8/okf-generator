---
concept_id: python/complex/api/PaymentAPI
description: High-level API for processing payments through external gateways.
language: python
okf_version: '0.2'
resource: python/complex/api.py
tags:
- lang:python
- type:Class
- module:python
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: PaymentAPI
type: Class
---

# PaymentAPI

High-level API for processing payments through external gateways.

## Docstring

High-level API for processing payments through external gateways.

## Methods

- `__init__`
- `service`
- `charge`
- `get_charge`
- `health_check`
- `validate_amount`

## Source
Lines 40–115 in `python/complex/api.py`

```py
class PaymentAPI:
    """High-level API for processing payments through external gateways."""

    def __init__(self, service: PaymentService | None = None) -> None:
        self._service = service or PaymentService(api_key=settings.payment_gateway_key)

    @property
    def service(self) -> PaymentService:
        """Return the underlying payment service instance."""
        return self._service

    @json_response
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

    def get_charge(self, charge_id: str) -> dict | None:
        """Retrieve details for a previously created charge.

        Args:
            charge_id: The unique identifier returned by the gateway.

        Returns:
            Charge details dict, or None if not found.
        """
        result = self._service.lookup_charge(charge_id, idempotency_key=None)
        return result.to_dict() if result else None

    @classmethod
    def health_check(cls) -> dict:
        """Return the current health status of the API and its dependencies.

        Returns:
            Dict with ``status``, ``timestamp``, and ``version`` keys.
        """
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.version,
        }

    @staticmethod
    def validate_amount(amount_cents: int) -> bool:
        """Check that an amount is within acceptable bounds.

        Args:
            amount_cents: Amount in cents to validate.

        Returns:
            True if the amount is valid, False otherwise.
        """
        return 1 <= amount_cents <= 9_999_999
```

## Relationships

| Type | Target |
|------|--------|
| related | [api](/python/complex/api.md) |
| related | [__init__](/python/complex/api/init.md) |
| related | [service](/python/complex/api/service.md) |
| related | [charge](/python/complex/api/charge.md) |
| related | [get_charge](/python/complex/api/get_charge.md) |
| related | [health_check](/python/complex/api/health_check.md) |
| related | [validate_amount](/python/complex/api/validate_amount.md) |
