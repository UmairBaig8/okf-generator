---
concept_id: scala/complex/Router/add
description: Top-level helper.
language: scala
okf_version: '0.2'
resource: scala/complex/Router.scala
tags:
- lang:scala
- type:Function
- module:scala
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T18:29:30Z'
title: add
type: Function
---

# add

Top-level helper.

## Signature

```scala
def add(method: String, path: String, handler: () => Any): Unit
```

## Docstring

Top-level helper.

## Source
Lines 5–7 in `scala/complex/Router.scala`

## Relationships

| Type | Target |
|------|--------|
| related | [Router](/scala/complex/Router.md) |
| calls | [Route](/scala/complex/Router/Route.md) |
| called_by | [Order](/java/complex/model/Order/Order.md) |
| called_by | [addItem](/java/complex/model/Order/addItem.md) |
