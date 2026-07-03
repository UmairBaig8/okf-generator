---
description: Check if a string looks like a US phone number.
resource: python/easy_v2/validator.py
tags:
- lang:python
- type:Function
- module:python
- domain:easy_v2
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T19:07:05Z'
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

## Related

- [validator](/python/easy_v2/validator.md)
