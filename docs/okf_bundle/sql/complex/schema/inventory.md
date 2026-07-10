---
concept_id: sql/complex/schema/inventory
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
timestamp: '2026-07-10T14:55:12Z'
title: inventory
type: Table
---

# inventory

Table defined in schema.sql

## Signature

```sql
CREATE TABLE inventory (
    product_id  INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    sku         TEXT        NOT NULL UNIQUE,
    name        TEXT        NOT NULL,
    unit_price  NUMERIC(10 ...
```

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `product_id` | `INTEGER` | `PRIMARY KEY` |
| `sku` | `TEXT` | `NOT NULL UNIQUE` |
| `name` | `TEXT` | `NOT NULL` |
| `unit_price` | `NUMERIC(10,2)` | `NOT NULL` |
| `quantity` | `INTEGER` | `NOT NULL` |
| `reorder_at` | `INTEGER` | `NOT NULL` |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` |

## Source
Lines 15–23 in `sql/complex/schema.sql`

```sql
CREATE TABLE inventory (
    product_id  INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    sku         TEXT        NOT NULL UNIQUE,
    name        TEXT        NOT NULL,
    unit_price  NUMERIC(10,2) NOT NULL CHECK (unit_price > 0),
    quantity    INTEGER     NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    reorder_at  INTEGER     NOT NULL DEFAULT 10,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Relationships

| Type | Target |
|------|--------|
| related | [schema](/sql/complex/schema.md) |
