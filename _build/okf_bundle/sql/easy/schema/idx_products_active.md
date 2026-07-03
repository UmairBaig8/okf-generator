---
description: Index defined in schema.sql
resource: sql/easy/schema.sql
tags:
- lang:sql
- type:Index
- module:sql
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:45:00Z'
title: idx_products_active
type: Index
---

# idx_products_active

Index defined in schema.sql

## Signature

```sql
CREATE INDEX idx_products_active ON products(active) WHERE active = 1
```

## Source
Lines 22–22 in `sql/easy/schema.sql`

## Related

- [schema](/sql/easy/schema.md)
