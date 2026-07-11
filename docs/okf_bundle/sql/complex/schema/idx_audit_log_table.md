---
concept_id: sql/complex/schema/idx_audit_log_table
description: Index defined in schema.sql
language: sql
okf_version: '0.2'
resource: sql/complex/schema.sql
tags:
- lang:sql
- type:Index
- module:sql
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-11T09:34:13Z'
title: idx_audit_log_table
type: Index
---

# idx_audit_log_table

Index defined in schema.sql

## Signature

```sql
CREATE INDEX idx_audit_log_table ON audit_log(table_name, record_id)
```

## Source
Lines 55–55 in `sql/complex/schema.sql`

## Relationships

| Type | Target |
|------|--------|
| related | [schema](/sql/complex/schema.md) |
