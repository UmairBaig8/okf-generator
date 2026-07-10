---
concept_id: sql/easy/schema/idx_products_active
description: Index defined in schema.sql
language: sql
okf_version: '0.2'
resource: sql/easy/schema.sql
tags:
- lang:sql
- type:Index
- module:sql
- domain:easy
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:42Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [schema](/sql/easy/schema.md) |
