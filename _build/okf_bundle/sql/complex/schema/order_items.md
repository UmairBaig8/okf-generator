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
title: order_items
type: Table
---

# order_items

Table defined in schema.sql

## Signature

```sql
CREATE TABLE order_items (
    order_id    INTEGER     NOT NULL REFERENCES orders(id),
    product_id  INTEGER     NOT NULL REFERENCES inventory(product_id),
    quantity    INTEGER     NOT NULL CHECK ...
```

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `order_id` | `INTEGER` | `NOT NULL REFERENCES orders` |
| `product_id` | `INTEGER` | `NOT NULL REFERENCES inventory` |
| `quantity` | `INTEGER` | `NOT NULL` |
| `unit_price` | `NUMERIC(10,2)` | `NOT NULL` |

## Source
Lines 36–42 in `sql/complex/schema.sql`

## Related

- [schema](/sql/complex/schema.md)
