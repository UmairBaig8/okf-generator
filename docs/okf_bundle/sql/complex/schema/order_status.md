---
concept_id: sql/complex/schema/order_status
description: Enterprise order management schema with audit trail.
language: sql
okf_version: '0.2'
resource: sql/complex/schema.sql
tags:
- lang:sql
- type:Type
- module:sql
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T19:32:24Z'
title: order_status
type: Type
---

# order_status

Enterprise order management schema with audit trail.

## Signature

```sql
CREATE TYPE order_status AS ENUM ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')
```

## Docstring

Enterprise order management schema with audit trail.

## Source
Lines 3–3 in `sql/complex/schema.sql`

## Relationships

| Type | Target |
|------|--------|
| related | [schema](/sql/complex/schema.md) |
