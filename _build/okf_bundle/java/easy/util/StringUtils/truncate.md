---
description: Truncates a string to the specified maximum length.
resource: java/easy/util/StringUtils.java
tags:
- lang:java
- type:Function
- module:java
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:34Z'
title: truncate
type: Function
---

# truncate

Truncates a string to the specified maximum length.

## Signature

```java
String truncate(String text, int maxLen)
```

## Visibility

- `public`
- `static`

## Docstring

Truncates a string to the specified maximum length.
@param text    the input string
@param maxLen  maximum allowed length
@return truncated string with "..." appended if shortened

## Parameters

| Name | Type | Default |
|------|------|---------|
| `text` | `—` | `—` |
| `maxLen` | `—` | `—` |

## Returns
`truncated string with "..." appended if shortened`

## Source
Lines 36–41 in `java/easy/util/StringUtils.java`

## Related

- [StringUtils](/java/easy/util/StringUtils.md)
