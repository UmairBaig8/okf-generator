---
concept_id: sql/complex/functions/set_updated_at
description: 'Trigger: automatically update updated_at before any row change.'
language: sql
okf_version: '0.2'
resource: sql/complex/functions.sql
tags:
- lang:sql
- type:Function
- module:sql
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T19:08:02Z'
title: set_updated_at
type: Function
---

# set_updated_at

Trigger: automatically update updated_at before any row change.

## Signature

```sql
CREATE OR REPLACE FUNCTION set_updated_at()
```

## Docstring

Trigger: automatically update updated_at before any row change.

## Source
Lines 54–60 in `sql/complex/functions.sql`

## Relationships

| Type | Target |
|------|--------|
| related | [functions](/sql/complex/functions.md) |
