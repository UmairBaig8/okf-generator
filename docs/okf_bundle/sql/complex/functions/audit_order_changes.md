---
concept_id: sql/complex/functions/audit_order_changes
description: 'Trigger: log all changes to orders to the audit table.'
language: sql
okf_version: '0.2'
resource: sql/complex/functions.sql
tags:
- lang:sql
- type:Function
- module:sql
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:12Z'
title: audit_order_changes
type: Function
---

# audit_order_changes

Trigger: log all changes to orders to the audit table.

## Signature

```sql
CREATE OR REPLACE FUNCTION audit_order_changes()
```

## Docstring

Trigger: log all changes to orders to the audit table.

## Source
Lines 75–86 in `sql/complex/functions.sql`

```sql
CREATE OR REPLACE FUNCTION audit_order_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, changed_by)
    VALUES ('orders', COALESCE(NEW.id, OLD.id),
            TG_OP,
            CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD)::jsonb END,
            CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW)::jsonb END,
            NULL);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

## Relationships

| Type | Target |
|------|--------|
| related | [functions](/sql/complex/functions.md) |
