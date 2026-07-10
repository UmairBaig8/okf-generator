---
concept_id: sql/easy/schema/active_products
description: View defined in schema.sql
language: sql
okf_version: '0.2'
resource: sql/easy/schema.sql
tags:
- lang:sql
- type:View
- module:sql
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T18:24:42Z'
title: active_products
type: View
---

# active_products

View defined in schema.sql

## Signature

```sql
CREATE VIEW active_products AS
SELECT p.id, p.name, p.price, c.name AS category
FROM products p
JOIN categories c ON c.id = p.category_id
WHERE p.active = 1
```

## Source
Lines 33–37 in `sql/easy/schema.sql`

## Relationships

| Type | Target |
|------|--------|
| related | [schema](/sql/easy/schema.md) |
