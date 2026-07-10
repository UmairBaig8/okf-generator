---
concept_id: scala/complex/Router/Route
language: scala
okf_version: '0.2'
resource: scala/complex/Router.scala
tags:
- lang:scala
- type:Class
- module:scala
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:42Z'
title: Route
type: Class
---

# Route

## Signature

```scala
class Route
```

## Source
Lines 14–14 in `scala/complex/Router.scala`

```scala
case class Route(method: String, path: String, handler: () => Any)
```

## Relationships

| Type | Target |
|------|--------|
| related | [Router](/scala/complex/Router.md) |
| called_by | [Router](/scala/complex/Router/Router.md) |
| called_by | [add](/scala/complex/Router/add.md) |
