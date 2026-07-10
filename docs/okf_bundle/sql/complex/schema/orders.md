---
concept_id: sql/complex/schema/orders
description: Table defined in schema.sql
language: sql
okf_version: '0.2'
resource: sql/complex/schema.sql
tags:
- lang:sql
- type:Table
- module:sql
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T18:42:48Z'
title: orders
type: Table
---

# orders

Table defined in schema.sql

## Signature

```sql
CREATE TABLE orders (
    id          INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id     INTEGER     NOT NULL REFERENCES users(id),
    status      order_status NOT NULL DEFAULT 'pendin ...
```

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `id` | `INTEGER` | `PRIMARY KEY` |
| `user_id` | `INTEGER` | `NOT NULL REFERENCES users` |
| `status` | `order_status` | `NOT NULL` |
| `total` | `NUMERIC(12,2)` | `NOT NULL` |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` |

## Source
Lines 27–34 in `sql/complex/schema.sql`

## Relationships

| Type | Target |
|------|--------|
| related | [schema](/sql/complex/schema.md) |
