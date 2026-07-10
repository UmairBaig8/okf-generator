---
concept_id: php/complex/Router/dispatch
description: HTTP Router with middleware support.
language: php
okf_version: '0.2'
resource: php/complex/Router.php
tags:
- lang:php
- type:Function
- module:php
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: dispatch
type: Function
---

# dispatch

HTTP Router with middleware support.

## Signature

```php
function dispatch(RequestInterface $request): mixed
```

## Visibility

- `public`

## Docstring

HTTP Router with middleware support.

## Source
Lines 24–32 in `php/complex/Router.php`

```php
    public function dispatch(RequestInterface $request): mixed {
        foreach ($this->routes as $route) {
            if ($route['method'] === $request->getMethod() && $route['path'] === $request->getUri()) {
                $chain = $this->buildMiddlewareChain($route);
                return $chain($request);
            }
        }
        throw new \RuntimeException('No matching route', 404);
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Router](/php/complex/Router.md) |
