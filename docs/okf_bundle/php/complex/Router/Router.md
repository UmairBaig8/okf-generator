---
concept_id: php/complex/Router/Router
description: HTTP Router with middleware support.
language: php
okf_version: '0.2'
resource: php/complex/Router.php
tags:
- lang:php
- type:Class
- module:php
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:11Z'
title: Router
type: Class
---

# Router

HTTP Router with middleware support.

## Signature

```php
class Router
```

## Docstring

HTTP Router with middleware support.

## Methods

- `addRoute`
- `dispatch`
- `buildMiddlewareChain`
- `addMiddleware`

## Source
Lines 11–45 in `php/complex/Router.php`

```php
class Router {
    private array $routes = [];
    private array $middleware = [];

    public function addRoute(string $method, string $path, callable $handler, array $middleware = []): void {
        $this->routes[] = [
            'method' => $method,
            'path' => $path,
            'handler' => $handler,
            'middleware' => $middleware,
        ];
    }

    public function dispatch(RequestInterface $request): mixed {
        foreach ($this->routes as $route) {
            if ($route['method'] === $request->getMethod() && $route['path'] === $request->getUri()) {
                $chain = $this->buildMiddlewareChain($route);
                return $chain($request);
            }
        }
        throw new \RuntimeException('No matching route', 404);
    }

    private function buildMiddlewareChain(array $route): callable {
        $handler = $route['handler'];
        foreach (array_reverse(array_merge($this->middleware, $route['middleware'])) as $mw) {
            $handler = fn($req) => $mw->process($req, $handler);
        }
        return $handler;
    }

    public function addMiddleware(MiddlewareInterface $mw): void {
        $this->middleware[] = $mw;
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [Router](/php/complex/Router.md) |
