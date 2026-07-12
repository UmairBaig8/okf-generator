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
timestamp: '2026-07-12T07:14:59Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [functions](/sql/complex/functions.md) |
