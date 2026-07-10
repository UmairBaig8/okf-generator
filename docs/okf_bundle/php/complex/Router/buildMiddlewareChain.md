---
concept_id: php/complex/Router/buildMiddlewareChain
description: HTTP Router with middleware support.
language: php
okf_version: '0.2'
resource: php/complex/Router.php
tags:
- lang:php
- type:Function
- module:php
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: buildMiddlewareChain
type: Function
---

# buildMiddlewareChain

HTTP Router with middleware support.

## Signature

```php
function buildMiddlewareChain(array $route): callable
```

## Visibility

- `private`

## Docstring

HTTP Router with middleware support.

## Source
Lines 34–40 in `php/complex/Router.php`

```php
    private function buildMiddlewareChain(array $route): callable {
        $handler = $route['handler'];
        foreach (array_reverse(array_merge($this->middleware, $route['middleware'])) as $mw) {
            $handler = fn($req) => $mw->process($req, $handler);
        }
        return $handler;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Router](/php/complex/Router.md) |
