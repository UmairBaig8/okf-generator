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
timestamp: '2026-07-14T18:42:52Z'
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
