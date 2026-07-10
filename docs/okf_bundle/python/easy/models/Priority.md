---
concept_id: python/easy/models/Priority
description: Priority level for a task or notification.
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
title: Priority
type: Class
---

# Priority

Priority level for a task or notification.

## Inheritance

- `Enum`

## Docstring

Priority level for a task or notification.

## Source
Lines 9–15 in `python/easy/models.py`

```py
class Priority(Enum):
    """Priority level for a task or notification."""

    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()
```

## Relationships

| Type | Target |
|------|--------|
| related | [models](/python/easy/models.md) |
