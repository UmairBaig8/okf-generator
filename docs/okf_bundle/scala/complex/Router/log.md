---
concept_id: scala/complex/Router/log
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
timestamp: '2026-07-10T15:03:07Z'
title: log
type: Function
---

# log

Top-level helper.

## Signature

```scala
def log(message: String): Unit
```

## Docstring

Top-level helper.

## Source
Lines 18–18 in `scala/complex/Router.scala`

```scala
  def log(message: String): Unit = println(s"[LOG] $message")
```

## Relationships

| Type | Target |
|------|--------|
| related | [Router](/scala/complex/Router.md) |
