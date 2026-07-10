---
concept_id: sql/complex/schema/idx_inventory_low_stock
description: Index defined in schema.sql
language: sql
okf_version: '0.2'
resource: sql/complex/schema.sql
tags:
- lang:sql
- type:Index
- module:sql
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T19:11:07Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [schema](/sql/complex/schema.md) |
