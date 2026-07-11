---
concept_id: sql/easy/schema/available_inventory
description: Products available in stock with pricing info.
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
timestamp: '2026-07-11T19:56:54Z'
title: available_inventory
type: View
---

# available_inventory

Products available in stock with pricing info.

## Signature

```sql
CREATE VIEW available_inventory AS
SELECT p.id, p.sku, p.name, p.price, p.stock, c.name AS category
FROM products p
JOIN categories c ON c.id = p.category_id
WHERE p.active = 1 AND p.stock > 0
```

## Docstring

Products available in stock with pricing info.

## Source
Lines 40–44 in `sql/easy/schema.sql`

## Relationships

| Type | Target |
|------|--------|
| related | [schema](/sql/easy/schema.md) |
