---
description: Table defined in schema.sql
resource: sql/easy/schema.sql
tags:
- lang:sql
- type:Table
- module:sql
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:45:00Z'
title: products
type: Table
---

# products

Table defined in schema.sql

## Signature

```sql
CREATE TABLE products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    sku         TEXT    NOT NULL UNIQUE,
    name        TEXT     ...
```

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `id` | `INTEGER` | `PRIMARY KEY` |
| `category_id` | `INTEGER` | `NOT NULL REFERENCES categories` |
| `sku` | `TEXT` | `NOT NULL UNIQUE` |
| `name` | `TEXT` | `NOT NULL` |
| `price` | `REAL` | `NOT NULL` |
| `stock` | `INTEGER` | `NOT NULL` |
| `active` | `INTEGER` | `NOT NULL` |
| `created_at` | `TEXT` | `NOT NULL` |

## Source
Lines 10–19 in `sql/easy/schema.sql`

## Related

- [schema](/sql/easy/schema.md)
