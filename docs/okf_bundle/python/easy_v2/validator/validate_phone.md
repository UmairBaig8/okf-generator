---
concept_id: python/easy_v2/validator/validate_phone
description: Check if a string looks like a US phone number.
language: python
okf_version: '0.2'
resource: python/easy_v2/validator.py
tags:
- lang:python
- type:Function
- module:python
- domain:easy_v2
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T18:37:52Z'
title: validate_phone
type: Function
---

# validate_phone

Check if a string looks like a US phone number.

## Signature

```python
def validate_phone(phone: str) -> bool
```

## Docstring

Check if a string looks like a US phone number.

Args:
    phone: The phone string to validate.

Returns:
    True if the phone matches a basic pattern, False otherwise.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `phone` | `str` | `—` |

## Returns
`bool`

## Source
Lines 19–29 in `python/easy_v2/validator.py`

## Relationships

| Type | Target |
|------|--------|
| related | [validator](/python/easy_v2/validator.md) |
