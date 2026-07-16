---
concept_id: python/complex/api/validate_amount
description: Check that an amount is within acceptable bounds.
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
timestamp: '2026-07-16T08:11:36Z'
title: validate_amount
type: Function
---

# validate_amount

Check that an amount is within acceptable bounds.

## Signature

```python
def validate_amount(amount_cents: int) -> bool
```

## Decorators

- `staticmethod`

## Docstring

Check that an amount is within acceptable bounds.

Args:
    amount_cents: Amount in cents to validate.

Returns:
    True if the amount is valid, False otherwise.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `amount_cents` | `int` | `—` |

## Returns
`bool`

## Source
Lines 106–115 in `python/complex/api.py`

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentAPI](/python/complex/api/PaymentAPI.md) |
