---
concept_id: python/complex/api/get_charge
description: Retrieve details for a previously created charge.
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
timestamp: '2026-07-11T09:16:36Z'
title: get_charge
type: Function
---

# get_charge

Retrieve details for a previously created charge.

## Signature

```python
def get_charge(self, charge_id: str) -> dict | None
```

## Docstring

Retrieve details for a previously created charge.

Args:
    charge_id: The unique identifier returned by the gateway.

Returns:
    Charge details dict, or None if not found.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `charge_id` | `str` | `—` |

## Returns
`dict | None`

## Source
Lines 80–90 in `python/complex/api.py`

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentAPI](/python/complex/api/PaymentAPI.md) |
| calls | [lookup_charge](/python/complex/services/payment/lookup_charge.md) |
| calls | [to_dict](/python/complex/services/payment/to_dict.md) |
