---
concept_id: php/complex/MiddlewareInterface/process
description: Middleware interface for the HTTP pipeline.
language: php
okf_version: '0.2'
resource: php/complex/MiddlewareInterface.php
tags:
- lang:php
- type:Function
- module:php
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-11T11:41:46Z'
title: process
type: Function
---

# process

Middleware interface for the HTTP pipeline.

## Signature

```php
function process(RequestInterface $request, callable $next): mixed
```

## Visibility

- `public`

## Docstring

Middleware interface for the HTTP pipeline.

## Source
Lines 11–11 in `php/complex/MiddlewareInterface.php`

## Relationships

| Type | Target |
|------|--------|
| related | [MiddlewareInterface](/php/complex/MiddlewareInterface.md) |
