---
concept_id: python/easy_v2/validator/validate_email
description: Check if a string looks like a valid email address.
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
timestamp: '2026-07-10T17:51:27Z'
title: validate_email
type: Function
---

# validate_email

Check if a string looks like a valid email address.

## Signature

```python
def validate_email(email: str) -> bool
```

## Docstring

Check if a string looks like a valid email address.

Args:
    email: The email string to validate.

Returns:
    True if the email matches a basic pattern, False otherwise.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `email` | `str` | `—` |

## Returns
`bool`

## Source
Lines 6–16 in `python/easy_v2/validator.py`

## Relationships

| Type | Target |
|------|--------|
| related | [validator](/python/easy_v2/validator.md) |
