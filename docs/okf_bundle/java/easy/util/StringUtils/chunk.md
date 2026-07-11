---
concept_id: java/easy/util/StringUtils/chunk
description: Splits a string into chunks of the given size.
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
timestamp: '2026-07-11T09:16:36Z'
title: chunk
type: Function
---

# chunk

Splits a string into chunks of the given size.

## Signature

```java
List<String> chunk(String text, int size)
```

## Visibility

- `public`
- `static`

## Docstring

Splits a string into chunks of the given size.
@param text  the input string
@param size  chunk size in characters
@return list of string chunks

## Parameters

| Name | Type | Default |
|------|------|---------|
| `text` | `—` | `—` |

| `size` | `—` | `—` |

## Returns
`list of string chunks`

## Source
Lines 75–84 in `java/easy/util/StringUtils.java`

## Relationships

| Type | Target |
|------|--------|
| related | [StringUtils](/java/easy/util/StringUtils.md) |
