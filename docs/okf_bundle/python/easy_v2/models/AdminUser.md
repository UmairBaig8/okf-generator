---
concept_id: python/easy_v2/models/AdminUser
description: An administrative user with elevated system access.
language: python
okf_version: '0.2'
resource: python/easy_v2/models.py
tags:
- lang:python
- type:Class
- module:python
- domain:easy_v2
- git:branch:HEAD
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
Lines 46–51 in `python/easy_v2/models.py`

## Relationships

| Type | Target |
|------|--------|
| related | [models](/python/easy_v2/models.md) |
