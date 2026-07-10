---
concept_id: php/easy/User/LoggerInterface
description: Logger interface for dependency resolution.
language: php
okf_version: '0.2'
resource: php/easy/User.php
tags:
- lang:php
- type:Interface
- module:php
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:11Z'
title: LoggerInterface
type: Interface
---

# LoggerInterface

Logger interface for dependency resolution.

## Signature

```php
interface LoggerInterface
```

## Docstring

Logger interface for dependency resolution.

## Methods

- `log`
- `error`

## Source
Lines 42–45 in `php/easy/User.php`

```php
interface LoggerInterface {
    public function log(string $message): void;
    public function error(string $message): void;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/php/easy/User.md) |
