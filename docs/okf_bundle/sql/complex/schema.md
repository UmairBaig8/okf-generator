---
concept_id: sql/complex/schema
description: Enterprise order management schema with audit trail.
language: sql
okf_version: '0.2'
resource: sql/complex/schema.sql
tags:
- lang:sql
- type:Module
- module:sql
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-11T09:04:22Z'
title: schema
type: Module
---

# schema

Enterprise order management schema with audit trail.

## Docstring

Enterprise order management schema with audit trail.

## Relationships

| Type | Target |
|------|--------|
| related | [order_status](/sql/complex/schema/order_status.md) |
| related | [users](/sql/complex/schema/users.md) |
| related | [inventory](/sql/complex/schema/inventory.md) |
| related | [idx_inventory_low_stock](/sql/complex/schema/idx_inventory_low_stock.md) |
| related | [orders](/sql/complex/schema/orders.md) |
| related | [order_items](/sql/complex/schema/order_items.md) |
| related | [audit_log](/sql/complex/schema/audit_log.md) |
| related | [idx_audit_log_table](/sql/complex/schema/idx_audit_log_table.md) |
| related | [idx_audit_log_time](/sql/complex/schema/idx_audit_log_time.md) |
