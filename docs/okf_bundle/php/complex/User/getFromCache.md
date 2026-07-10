---
concept_id: php/complex/User/getFromCache
language: php
okf_version: '0.2'
resource: php/complex/User.php
tags:
- lang:php
- type:Function
- module:php
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: getFromCache
type: Function
---

# getFromCache

## Signature

```php
function getFromCache(string $key): mixed
```

## Visibility

- `public`

## Source
Lines 34–36 in `php/complex/User.php`

```php
    public function getFromCache(string $key): mixed {
        return $this->cache[$key] ?? null;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/php/complex/User.md) |
