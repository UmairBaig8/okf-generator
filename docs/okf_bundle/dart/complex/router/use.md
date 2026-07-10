---
concept_id: dart/complex/router/use
language: dart
okf_version: '0.2'
resource: dart/complex/router.dart
tags:
- lang:dart
- type:Function
- module:dart
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:11Z'
title: use
type: Function
---

# use

## Signature

```dart
voiduse(Middleware mw)
```

## Source
Lines 23–23 in `dart/complex/router.dart`

```dart
  void use(Middleware mw) => _middleware.add(mw);
```

## Relationships

| Type | Target |
|------|--------|
| related | [router](/dart/complex/router.md) |
