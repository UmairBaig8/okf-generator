---
concept_id: dart/easy/calculator/Calculator
description: A simple calculator.
language: dart
okf_version: '0.2'
resource: dart/easy/calculator.dart
tags:
- lang:dart
- type:Class
- module:dart
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: Calculator
type: Class
---

# Calculator

A simple calculator.

## Signature

```dart
class Calculator
```

## Docstring

A simple calculator.

## Methods

- `add`
- `subtract`
- `version`
- `Calculator`

## Source
Lines 2–13 in `dart/easy/calculator.dart`

```dart
class Calculator {
  int result = 0;

  Calculator(this.result);

  /// Add a value to the result.
  int add(int value) => result += value;

  int subtract(int value) => result -= value;

  static String version() => '1.0.0';
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [calculator](/dart/easy/calculator.md) |
