---
description: Represents a user in the system.
resource: python/easy_v2/models.py
tags:
- lang:python
- type:Class
- module:python
- domain:easy_v2
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T19:06:43Z'
title: User
type: Class
---

# User

Represents a user in the system.

## Inheritance

- `TimestampMixin`

## Decorators

- `dataclass`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `user_id` | `str` | `` |
| `email` | `str` | `` |
| `display_name` | `str | None` | `` |
| `is_active` | `bool` | `` |
| `priority` | `Priority` | `` |

## Docstring

Represents a user in the system.

Attributes:
    user_id: Unique identifier for the user.
    email: User's email address.
    display_name: Optional human-readable name.
    is_active: Whether the user account is active.
    priority: User's notification priority level.

## Source
Lines 27–42 in `python/easy_v2/models.py`

## Related

- [models](/python/easy_v2/models.md)
