---
description: Table defined in schema.sql
resource: sql/complex/schema.sql
tags:
- lang:sql
- type:Table
- module:sql
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:45:03Z'
title: inventory
type: Table
---

# inventory

Table defined in schema.sql

## Signature

```sql
CREATE TABLE inventory (
    product_id  INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    sku         TEXT        NOT NULL UNIQUE,
    name        TEXT        NOT NULL,
    unit_price  NUMERIC(10 ...
```

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `product_id` | `INTEGER` | `PRIMARY KEY` |
| `sku` | `TEXT` | `NOT NULL UNIQUE` |
| `name` | `TEXT` | `NOT NULL` |
| `unit_price` | `NUMERIC(10,2)` | `NOT NULL` |
| `quantity` | `INTEGER` | `NOT NULL` |
| `reorder_at` | `INTEGER` | `NOT NULL` |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` |

## Source
Lines 15–23 in `sql/complex/schema.sql`

## Related

- [schema](/sql/complex/schema.md)
