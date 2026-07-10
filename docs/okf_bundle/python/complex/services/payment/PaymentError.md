---
concept_id: python/complex/services/payment/PaymentError
description: Raised when a payment operation fails at the gateway level.
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
title: PaymentError
type: Class
---

# PaymentError

Raised when a payment operation fails at the gateway level.

## Inheritance

- `Exception`

## Docstring

Raised when a payment operation fails at the gateway level.

## Methods

- `__init__`

## Source
Lines 21–26 in `python/complex/services/payment.py`

```py
class PaymentError(Exception):
    """Raised when a payment operation fails at the gateway level."""

    def __init__(self, message: str, code: str = "payment_error") -> None:
        self.code = code
        super().__init__(message)
```

## Relationships

| Type | Target |
|------|--------|
| related | [payment](/python/complex/services/payment.md) |
| related | [__init__](/python/complex/services/payment/init.md) |
