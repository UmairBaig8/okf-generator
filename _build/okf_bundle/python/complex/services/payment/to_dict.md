---
description: Serialize the result to a plain dictionary.
resource: python/complex/services/payment.py
tags:
- lang:python
- type:Function
- module:python
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:18Z'
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

## Related

- [PaymentResult](/python/complex/services/payment/PaymentResult.md)

## Called By

- [charge](/python/complex/api/charge.md)
- [get_charge](/python/complex/api/get_charge.md)
- [json_response](/python/complex/api/json_response.md)
