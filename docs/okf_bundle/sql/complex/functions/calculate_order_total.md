---
concept_id: sql/complex/functions/calculate_order_total
description: Calculate the total for an order based on its items.
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
timestamp: '2026-07-12T09:19:36Z'
title: calculate_order_total
type: Function
---

# calculate_order_total

Calculate the total for an order based on its items.

## Signature

```sql
CREATE OR REPLACE FUNCTION calculate_order_total(p_order_id INTEGER)
```

## Docstring

Calculate the total for an order based on its items.

## Source
Lines 4–19 in `sql/complex/functions.sql`

## Relationships

| Type | Target |
|------|--------|
| related | [functions](/sql/complex/functions.md) |
