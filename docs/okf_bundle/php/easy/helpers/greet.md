---
concept_id: php/easy/helpers/greet
description: Greet a user by name.
language: php
okf_version: '0.2'
resource: php/easy/helpers.php
tags:
- lang:php
- type:Function
- module:php
- domain:easy
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: greet
type: Function
---

# greet

Greet a user by name.

## Signature

```php
function greet(string $name): string
```

## Docstring

Greet a user by name.

## Source
Lines 6–8 in `php/easy/helpers.php`

```php
function greet(string $name): string {
    return "Hello, " . $name;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [helpers](/php/easy/helpers.md) |
