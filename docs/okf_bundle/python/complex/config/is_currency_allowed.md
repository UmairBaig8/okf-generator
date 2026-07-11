---
concept_id: python/complex/config/is_currency_allowed
description: Check whether a currency code is in the allowed set.
language: python
okf_version: '0.2'
resource: python/complex/config.py
tags:
- lang:python
- type:Function
- module:python
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-11T09:38:55Z'
title: is_currency_allowed
type: Function
---

# is_currency_allowed

Check whether a currency code is in the allowed set.

## Signature

```python
def is_currency_allowed(self, currency: str) -> bool
```

## Docstring

Check whether a currency code is in the allowed set.

Args:
    currency: Three-letter ISO 4217 currency code.

Returns:
    True if the currency is accepted by this service.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `currency` | `str` | `—` |

## Returns
`bool`

## Source
Lines 44–53 in `python/complex/config.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Settings](/python/complex/config/Settings.md) |
