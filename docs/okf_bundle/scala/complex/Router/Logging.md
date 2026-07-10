---
concept_id: scala/complex/Router/Logging
description: Logging middleware trait.
language: scala
okf_version: '0.2'
resource: scala/complex/Router.scala
tags:
- lang:scala
- type:Interface
- module:scala
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T15:03:07Z'
title: Logging
type: Interface
---

# Logging

Logging middleware trait.

## Signature

```scala
trait Logging
```

## Docstring

Logging middleware trait.

## Methods

- `log`

## Source
Lines 17–19 in `scala/complex/Router.scala`

```scala
trait Logging {
  def log(message: String): Unit = println(s"[LOG] $message")
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [Router](/scala/complex/Router.md) |
