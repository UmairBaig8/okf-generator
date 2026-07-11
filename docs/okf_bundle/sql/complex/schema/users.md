---
concept_id: sql/complex/schema/users
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
timestamp: '2026-07-11T09:16:36Z'
title: users
type: Table
---

# users

Table defined in schema.sql

## Signature

```sql
CREATE TABLE users (
    id          INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    email       TEXT        NOT NULL UNIQUE,
    password_hash TEXT      NOT NULL,
    display_name TEXT,
    is_ ...
```

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `id` | `INTEGER` | `PRIMARY KEY` |
| `email` | `TEXT` | `NOT NULL UNIQUE` |
| `password_hash` | `TEXT` | `NOT NULL` |
| `display_name` | `TEXT` | `` |
| `is_active` | `BOOLEAN` | `NOT NULL` |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` |

## Source
Lines 5–13 in `sql/complex/schema.sql`

## Relationships

| Type | Target |
|------|--------|
| related | [schema](/sql/complex/schema.md) |
