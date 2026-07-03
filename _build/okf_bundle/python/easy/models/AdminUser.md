---
description: An administrative user with elevated system access.
resource: python/easy/models.py
tags:
- lang:python
- type:Class
- module:python
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:04Z'
title: AdminUser
type: Class
---

# AdminUser

An administrative user with elevated system access.

## Inheritance

- `User`

## Decorators

- `dataclass`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `role` | `str` | `` |
| `permissions` | `list[str]` | `` |
| `access_level` | `int` | `` |

## Docstring

An administrative user with elevated system access.

## Source
Lines 46–51 in `python/easy/models.py`

## Related

- [models](/python/easy/models.md)
