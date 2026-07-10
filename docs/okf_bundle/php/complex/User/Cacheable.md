---
concept_id: php/complex/User/Cacheable
language: php
okf_version: '0.2'
resource: php/complex/User.php
tags:
- lang:php
- type:Class
- module:php
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:11Z'
title: Cacheable
type: Class
---

# Cacheable

## Signature

```php
trait Cacheable
```

## Methods

- `getFromCache`

## Source
Lines 32–37 in `php/complex/User.php`

```php
trait Cacheable {
    private array $cache = [];
    public function getFromCache(string $key): mixed {
        return $this->cache[$key] ?? null;
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/php/complex/User.md) |
