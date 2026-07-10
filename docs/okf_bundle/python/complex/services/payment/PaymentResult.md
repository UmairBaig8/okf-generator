---
concept_id: python/complex/services/payment/PaymentResult
description: Immutable result returned after processing a payment.
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
timestamp: '2026-07-10T14:55:11Z'
title: PaymentResult
type: Class
---

# PaymentResult

Immutable result returned after processing a payment.

## Decorators

- `dataclass`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `charge_id` | `str` | `` |
| `status` | `PaymentStatus` | `` |
| `amount_cents` | `int` | `` |
| `currency` | `str` | `` |
| `processed_at` | `datetime` | `` |
| `gateway_response` | `str` | `` |

## Docstring

Immutable result returned after processing a payment.

## Methods

- `to_dict`

## Source
Lines 30–48 in `python/complex/services/payment.py`

```py
class PaymentResult:
    """Immutable result returned after processing a payment."""

    charge_id: str
    status: PaymentStatus
    amount_cents: int
    currency: str
    processed_at: datetime = field(default_factory=datetime.utcnow)
    gateway_response: str = ""

    def to_dict(self) -> dict:
        """Serialize the result to a plain dictionary."""
        return {
            "charge_id": self.charge_id,
            "status": self.status.value,
            "amount_cents": self.amount_cents,
            "currency": self.currency,
            "processed_at": self.processed_at.isoformat(),
        }
```

## Relationships

| Type | Target |
|------|--------|
| related | [payment](/python/complex/services/payment.md) |
| related | [to_dict](/python/complex/services/payment/to_dict.md) |
| called_by | [process_payment](/python/complex/services/payment/process_payment.md) |
