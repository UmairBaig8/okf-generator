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

## Related

- [schema](/sql/complex/schema.md)
