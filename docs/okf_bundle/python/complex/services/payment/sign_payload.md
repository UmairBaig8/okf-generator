---
concept_id: python/complex/services/payment/sign_payload
language: python
okf_version: '0.2'
resource: python/complex/services/payment.py
tags:
- lang:python
- type:Function
- module:python
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentService](/python/complex/services/payment/PaymentService.md) |
| called_by | [process_payment](/python/complex/services/payment/process_payment.md) |
