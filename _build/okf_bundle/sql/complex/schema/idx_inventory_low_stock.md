---
description: Index defined in schema.sql
resource: sql/complex/schema.sql
tags:
- lang:sql
- type:Index
- module:sql
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:45:03Z'
title: idx_inventory_low_stock
type: Index
---

# idx_inventory_low_stock

Index defined in schema.sql

## Signature

```sql
CREATE INDEX idx_inventory_low_stock ON inventory(quantity) WHERE quantity <= reorder_at
```

## Source
Lines 25–25 in `sql/complex/schema.sql`

## Related

- [schema](/sql/complex/schema.md)
