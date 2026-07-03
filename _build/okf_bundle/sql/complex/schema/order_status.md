---
description: Enterprise order management schema with audit trail.
resource: sql/complex/schema.sql
tags:
- lang:sql
- type:Type
- module:sql
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:45:03Z'
title: order_status
type: Type
---

# order_status

Enterprise order management schema with audit trail.

## Signature

```sql
CREATE TYPE order_status AS ENUM ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')
```

## Docstring

Enterprise order management schema with audit trail.

## Source
Lines 3–3 in `sql/complex/schema.sql`

## Related

- [schema](/sql/complex/schema.md)
