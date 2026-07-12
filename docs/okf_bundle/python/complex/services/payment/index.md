---
description: Knowledge index for python/complex/services/payment
resource: python/complex/services/payment
timestamp: '2026-07-12T07:15:35Z'
title: payment
type: Index
---

# payment

## Classs

- [PaymentError](PaymentError.md) — Raised when a payment operation fails at the gateway level.
- [PaymentResult](PaymentResult.md) — Immutable result returned after processing a payment.
- [PaymentService](PaymentService.md) — Core payment service that communicates with the external gateway.
- [PaymentStatus](PaymentStatus.md) — Possible states of a payment transaction.

## Functions

- [__init__](init.md)
- [__init__](init_1.md)
- [_generate_idempotency_key](generate_idempotency_key.md)
- [_sign_payload](sign_payload.md)
- [from_settings](from_settings.md) — Factory: create a service instance pre-configured from settings.
- [lookup_charge](lookup_charge.md) — Look up a previously processed charge by its identifier.
- [process_payment](process_payment.md) — Submit a payment to the external gateway.
- [to_dict](to_dict.md) — Serialize the result to a plain dictionary.
