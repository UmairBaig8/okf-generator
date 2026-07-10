---
concept_id: python/complex/services/payment/to_dict
description: Serialize the result to a plain dictionary.
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
timestamp: '2026-07-10T14:57:28Z'
title: to_dict
type: Function
---

# to_dict

Serialize the result to a plain dictionary.

## Signature

```python
def to_dict(self) -> dict
```

## Docstring

Serialize the result to a plain dictionary.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

## Returns
`dict`

## Source
Lines 40–48 in `python/complex/services/payment.py`

```py
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
| related | [PaymentResult](/python/complex/services/payment/PaymentResult.md) |
| called_by | [charge](/python/complex/api/charge.md) |
| called_by | [get_charge](/python/complex/api/get_charge.md) |
| called_by | [json_response](/python/complex/api/json_response.md) |
