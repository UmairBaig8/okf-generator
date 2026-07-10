---
concept_id: sql/complex/schema/audit_log
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
timestamp: '2026-07-10T17:51:27Z'
title: audit_log
type: Table
---

# audit_log

Table defined in schema.sql

## Signature

```sql
CREATE TABLE audit_log (
    id          INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    table_name  TEXT        NOT NULL,
    record_id   INTEGER     NOT NULL,
    action      TEXT        NOT N ...
```

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `id` | `INTEGER` | `PRIMARY KEY` |
| `table_name` | `TEXT` | `NOT NULL` |
| `record_id` | `INTEGER` | `NOT NULL` |
| `action` | `TEXT` | `NOT NULL` |
| `old_values` | `JSONB` | `` |
| `new_values` | `JSONB` | `` |
| `changed_by` | `INTEGER` | `REFERENCES users` |
| `changed_at` | `TIMESTAMPTZ` | `NOT NULL` |

## Source
Lines 44–53 in `sql/complex/schema.sql`

## Relationships

| Type | Target |
|------|--------|
| related | [schema](/sql/complex/schema.md) |
