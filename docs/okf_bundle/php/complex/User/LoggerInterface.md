---
concept_id: php/complex/User/LoggerInterface
language: php
okf_version: '0.2'
resource: php/complex/User.php
tags:
- lang:php
- type:Interface
- module:php
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T15:03:07Z'
title: LoggerInterface
type: Interface
---

# LoggerInterface

## Signature

```php
interface LoggerInterface
```

## Methods

- `log`
- `error`

## Source
Lines 27–30 in `php/complex/User.php`

```php
interface LoggerInterface {
    public function log(string $message): void;
    public function error(string $message): void;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/php/complex/User.md) |
