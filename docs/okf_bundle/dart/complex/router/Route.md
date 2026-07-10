---
concept_id: dart/complex/router/Route
language: dart
okf_version: '0.2'
resource: dart/complex/router.dart
tags:
- lang:dart
- type:Class
- module:dart
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: Route
type: Class
---

# Route

## Signature

```dart
class Route
```

## Methods

- `Route`

## Source
Lines 26–32 in `dart/complex/router.dart`

```dart
class Route {
  final String method;
  final String path;
  final Function handler;

  Route(this.method, this.path, this.handler);
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [router](/dart/complex/router.md) |
