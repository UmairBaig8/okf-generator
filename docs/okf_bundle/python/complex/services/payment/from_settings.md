---
concept_id: python/complex/services/payment/from_settings
description: 'Factory: create a service instance pre-configured from settings.'
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
timestamp: '2026-07-10T20:22:11Z'
title: from_settings
type: Function
---

# from_settings

Factory: create a service instance pre-configured from settings.

## Signature

```python
def from_settings(cls, api_key: str) -> 'PaymentService'
```

## Decorators

- `classmethod`

## Docstring

Factory: create a service instance pre-configured from settings.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `cls` | `—` | `—` |

| `api_key` | `str` | `—` |

## Returns
`'PaymentService'`

## Source
Lines 134–136 in `python/complex/services/payment.py`

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentService](/python/complex/services/payment/PaymentService.md) |
