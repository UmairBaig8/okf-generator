---
concept_id: python/complex/config/is_production
description: Check whether the service is running in production mode.
language: python
okf_version: '0.2'
resource: python/complex/config.py
tags:
- lang:python
- type:Function
- module:python
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T19:11:07Z'
title: is_production
type: Function
---

# is_production

Check whether the service is running in production mode.

## Signature

```python
def is_production(self) -> bool
```

## Docstring

Check whether the service is running in production mode.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

## Returns
`bool`

## Source
Lines 40–42 in `python/complex/config.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Settings](/python/complex/config/Settings.md) |
