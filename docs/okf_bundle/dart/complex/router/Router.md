---
concept_id: dart/complex/router/Router
description: HTTP Router with middleware support.
language: dart
okf_version: '0.2'
resource: dart/complex/router.dart
tags:
- lang:dart
- type:Class
- module:dart
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: Router
type: Class
---

# Router

HTTP Router with middleware support.

## Signature

```dart
class Router
```

## Docstring

HTTP Router with middleware support.

## Methods

- `get`
- `post`
- `dispatch`
- `use`

## Source
Lines 2–24 in `dart/complex/router.dart`

```dart
class Router {
  final List<Route> _routes = [];
  final List<Middleware> _middleware = [];

  void get(String path, Function handler) {
    _routes.add(Route('GET', path, handler));
  }

  void post(String path, Function handler) {
    _routes.add(Route('POST', path, handler));
  }

  dynamic dispatch(String method, String path) {
    for (final route in _routes) {
      if (route.method == method && route.path == path) {
        return route.handler();
      }
    }
    throw Exception('404');
  }

  void use(Middleware mw) => _middleware.add(mw);
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [router](/dart/complex/router.md) |
