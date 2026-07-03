---
description: Index defined in schema.sql
resource: sql/complex/schema.sql
tags:
- lang:sql
- type:Index
- module:sql
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:45:03Z'
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

## Related

- [schema](/sql/complex/schema.md)
