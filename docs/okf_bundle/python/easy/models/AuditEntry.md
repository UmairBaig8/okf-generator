---
concept_id: python/easy/models/AuditEntry
description: Immutable audit log entry recording a system action.
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
timestamp: '2026-07-10T18:29:30Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [models](/python/easy/models.md) |
