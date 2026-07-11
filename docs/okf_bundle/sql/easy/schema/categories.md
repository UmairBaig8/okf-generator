---
concept_id: sql/easy/schema/categories
description: E-commerce schema with categories, products, and customer tables.
language: sql
okf_version: '0.2'
resource: sql/easy/schema.sql
tags:
- lang:sql
- type:Table
- module:sql
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-11T10:49:18Z'
title: categories
type: Table
---

# categories

E-commerce schema with categories, products, and customer tables.

## Signature

```sql
CREATE TABLE categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    description TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
)
```

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `id` | `INTEGER` | `PRIMARY KEY` |
| `name` | `TEXT` | `NOT NULL UNIQUE` |
| `description` | `TEXT` | `` |
| `created_at` | `TEXT` | `NOT NULL` |

## Docstring

E-commerce schema with categories, products, and customer tables.

## Source
Lines 3–8 in `sql/easy/schema.sql`

## Relationships

| Type | Target |
|------|--------|
| related | [schema](/sql/easy/schema.md) |
