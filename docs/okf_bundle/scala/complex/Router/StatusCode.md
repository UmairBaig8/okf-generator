---
concept_id: scala/complex/Router/StatusCode
description: Response status codes.
language: scala
okf_version: '0.2'
resource: scala/complex/Router.scala
tags:
- lang:scala
- type:Enum
- module:scala
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: StatusCode
type: Enum
---

# StatusCode

Response status codes.

## Signature

```scala
enum StatusCode
```

## Docstring

Response status codes.

## Source
Lines 22–24 in `scala/complex/Router.scala`

```scala
enum StatusCode {
  case Ok, NotFound, InternalServerError
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [Router](/scala/complex/Router.md) |
