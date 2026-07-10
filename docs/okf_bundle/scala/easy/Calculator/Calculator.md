---
concept_id: scala/easy/Calculator/Calculator
description: A simple calculator.
language: scala
okf_version: '0.2'
resource: scala/easy/Calculator.scala
tags:
- lang:scala
- type:Class
- module:scala
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T15:03:07Z'
title: Calculator
type: Class
---

# Calculator

A simple calculator.

## Signature

```scala
class Calculator
```

## Docstring

A simple calculator.

## Methods

- `add`
- `getResult`

## Source
Lines 2–11 in `scala/easy/Calculator.scala`

```scala
class Calculator {
  private var result: Int = 0

  def add(value: Int): Int = {
    result += value
    result
  }

  def getResult: Int = result
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [Calculator](/scala/easy/Calculator.md) |
