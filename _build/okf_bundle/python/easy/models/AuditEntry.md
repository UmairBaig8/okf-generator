---
description: Immutable audit log entry recording a system action.
resource: python/easy/models.py
tags:
- lang:python
- type:Class
- module:python
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:04Z'
title: AuditEntry
type: Class
---

# AuditEntry

Immutable audit log entry recording a system action.

## Inheritance

- `TimestampMixin`

## Decorators

- `dataclass`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `entry_id` | `str` | `` |
| `actor` | `str` | `` |
| `action` | `str` | `` |
| `resource` | `str` | `` |
| `details` | `dict` | `` |

## Docstring

Immutable audit log entry recording a system action.

## Source
Lines 55–62 in `python/easy/models.py`

## Related

- [models](/python/easy/models.md)
