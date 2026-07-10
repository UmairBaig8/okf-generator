---
concept_id: scala/complex/Router/Router
description: HTTP Router with middleware support.
language: scala
okf_version: '0.2'
resource: scala/complex/Router.scala
tags:
- lang:scala
- type:Class
- module:scala
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:11Z'
title: Router
type: Class
---

# Router

HTTP Router with middleware support.

## Signature

```scala
class Router
```

## Docstring

HTTP Router with middleware support.

## Methods

- `add`
- `dispatch`

## Source
Lines 2–12 in `scala/complex/Router.scala`

```scala
class Router {
  private var routes: List[Route] = List.empty

  def add(method: String, path: String, handler: () => Any): Unit = {
    routes = routes :+ Route(method, path, handler)
  }

  def dispatch(method: String, path: String): Option[Any] = {
    routes.find(r => r.method == method && r.path == path).map(_.handler())
  }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [Router](/scala/complex/Router.md) |
| calls | [Route](/scala/complex/Router/Route.md) |
| calls | [find](/ruby/complex/services/report_service/find.md) |
