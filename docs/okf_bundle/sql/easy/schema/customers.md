---
concept_id: sql/easy/schema/customers
description: Table defined in schema.sql
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
timestamp: '2026-07-10T17:15:25Z'
title: customers
type: Table
---

# customers

Table defined in schema.sql

## Signature

```sql
CREATE TABLE customers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email       TEXT    NOT NULL UNIQUE,
    first_name  TEXT    NOT NULL,
    last_name   TEXT    NOT NULL,
    phone       ...
```

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `id` | `INTEGER` | `PRIMARY KEY` |
| `email` | `TEXT` | `NOT NULL UNIQUE` |
| `first_name` | `TEXT` | `NOT NULL` |
| `last_name` | `TEXT` | `NOT NULL` |
| `phone` | `TEXT` | `` |
| `created_at` | `TEXT` | `NOT NULL` |

## Source
Lines 24–31 in `sql/easy/schema.sql`

```sql
CREATE TABLE customers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email       TEXT    NOT NULL UNIQUE,
    first_name  TEXT    NOT NULL,
    last_name   TEXT    NOT NULL,
    phone       TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

## Relationships

| Type | Target |
|------|--------|
| related | [schema](/sql/easy/schema.md) |
