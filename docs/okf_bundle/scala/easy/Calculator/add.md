---
concept_id: scala/easy/Calculator/add
description: Top-level helper.
language: scala
okf_version: '0.2'
resource: scala/easy/Calculator.scala
tags:
- lang:scala
- type:Function
- module:scala
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T15:03:07Z'
title: add
type: Function
---

# add

Top-level helper.

## Signature

```scala
def add(value: Int): Int
```

## Docstring

Top-level helper.

## Source
Lines 5–8 in `scala/easy/Calculator.scala`

```scala
  def add(value: Int): Int = {
    result += value
    result
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Calculator](/scala/easy/Calculator.md) |
