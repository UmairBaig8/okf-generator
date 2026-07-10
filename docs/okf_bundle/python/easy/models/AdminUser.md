---
concept_id: python/easy/models/AdminUser
description: An administrative user with elevated system access.
language: python
okf_version: '0.2'
resource: python/easy/models.py
tags:
- lang:python
- type:Class
- module:python
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
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

```py
class AdminUser(User):
    """An administrative user with elevated system access."""

    role: str = "admin"
    permissions: list[str] = field(default_factory=lambda: ["read", "write", "delete"])
    access_level: int = 10
```

## Relationships

| Type | Target |
|------|--------|
| related | [models](/python/easy/models.md) |
