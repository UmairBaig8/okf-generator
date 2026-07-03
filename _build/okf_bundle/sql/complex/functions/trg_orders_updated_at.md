---
description: Trigger defined in functions.sql
resource: sql/complex/functions.sql
tags:
- lang:sql
- type:Trigger
- module:sql
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:45:08Z'
title: trg_orders_updated_at
type: Trigger
---

# trg_orders_updated_at

Trigger defined in functions.sql

## Signature

```sql
CREATE TRIGGER trg_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION set_updated_at()
```

## Source
Lines 66–68 in `sql/complex/functions.sql`

## Related

- [functions](/sql/complex/functions.md)
