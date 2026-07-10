---
concept_id: python/complex/api/service
description: Return the underlying payment service instance.
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
timestamp: '2026-07-10T20:08:44Z'
title: service
type: Function
---

# service

Return the underlying payment service instance.

## Signature

```python
def service(self) -> PaymentService
```

## Decorators

- `property`

## Docstring

Return the underlying payment service instance.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

## Returns
`PaymentService`

## Source
Lines 47–49 in `python/complex/api.py`

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentAPI](/python/complex/api/PaymentAPI.md) |
