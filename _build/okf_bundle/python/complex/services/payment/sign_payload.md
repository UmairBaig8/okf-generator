---
resource: python/complex/services/payment.py
tags:
- lang:python
- type:Function
- module:python
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:18Z'
title: _sign_payload
type: Function
---

# _sign_payload

## Signature

```python
def _sign_payload(self, payload: str) -> str
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |
| `payload` | `str` | `—` |

## Returns
`str`

## Source
Lines 128–131 in `python/complex/services/payment.py`

## Related

- [PaymentService](/python/complex/services/payment/PaymentService.md)

## Called By

- [process_payment](/python/complex/services/payment/process_payment.md)
