---
concept_id: sql/complex/functions/trg_inventory_updated_at
description: Trigger defined in functions.sql
language: sql
okf_version: '0.2'
resource: sql/complex/functions.sql
tags:
- lang:sql
- type:Trigger
- module:sql
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:42:36Z'
title: trg_inventory_updated_at
type: Trigger
---

# trg_inventory_updated_at

Trigger defined in functions.sql

## Signature

```sql
CREATE TRIGGER trg_inventory_updated_at
    BEFORE UPDATE ON inventory
    FOR EACH ROW EXECUTE FUNCTION set_updated_at()
```

## Source
Lines 70–72 in `sql/complex/functions.sql`

## Relationships

| Type | Target |
|------|--------|
| related | [functions](/sql/complex/functions.md) |
