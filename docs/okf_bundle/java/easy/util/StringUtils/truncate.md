---
concept_id: java/easy/util/StringUtils/truncate
description: Truncates a string to the specified maximum length.
language: java
okf_version: '0.2'
resource: java/easy/util/StringUtils.java
tags:
- lang:java
- type:Function
- module:java
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:57:28Z'
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

```java
    public static String truncate(String text, int maxLen) {
        if (text == null || text.length() <= maxLen) {
            return text;
        }
        return text.substring(0, Math.max(0, maxLen - 3)) + "...";
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [StringUtils](/java/easy/util/StringUtils.md) |
