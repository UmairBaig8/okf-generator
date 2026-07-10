---
concept_id: sql/easy/schema/idx_products_category
description: Index defined in schema.sql
language: sql
okf_version: '0.2'
resource: sql/easy/schema.sql
tags:
- lang:sql
- type:Index
- module:sql
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T18:22:20Z'
title: idx_products_category
type: Index
---

# idx_products_category

Index defined in schema.sql

## Signature

```sql
CREATE INDEX idx_products_category ON products(category_id)
```

## Source
Lines 21–21 in `sql/easy/schema.sql`

## Relationships

| Type | Target |
|------|--------|
| related | [schema](/sql/easy/schema.md) |
