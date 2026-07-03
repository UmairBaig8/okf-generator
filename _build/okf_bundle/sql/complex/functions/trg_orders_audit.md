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
title: trg_orders_audit
type: Trigger
---

# trg_orders_audit

Trigger defined in functions.sql

## Signature

```sql
CREATE TRIGGER trg_orders_audit
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION audit_order_changes()
```

## Source
Lines 88–90 in `sql/complex/functions.sql`

## Related

- [functions](/sql/complex/functions.md)
