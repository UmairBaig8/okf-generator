---
concept_id: sql/complex/schema/idx_audit_log_time
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
timestamp: '2026-07-12T22:02:43Z'
title: idx_audit_log_time
type: Index
---

# idx_audit_log_time

Index defined in schema.sql

## Signature

```sql
CREATE INDEX idx_audit_log_time ON audit_log(changed_at)
```

## Source
Lines 56–56 in `sql/complex/schema.sql`

## Relationships

| Type | Target |
|------|--------|
| related | [schema](/sql/complex/schema.md) |
