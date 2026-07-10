---
concept_id: java/easy/util/StringUtils/toSnakeCase
description: Converts a CamelCase string to snake_case.
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
timestamp: '2026-07-07T06:58:41Z'
title: toSnakeCase
type: Function
---

# toSnakeCase

Converts a CamelCase string to snake_case.

## Signature

```java
String toSnakeCase(String camel)
```

## Visibility

- `public`
- `static`

## Docstring

Converts a CamelCase string to snake_case.
@param camel the CamelCase input
@return snake_case string

## Parameters

| Name | Type | Default |
|------|------|---------|
| `camel` | `—` | `—` |

## Returns
`snake_case string`

## Source
Lines 49–66 in `java/easy/util/StringUtils.java`

```java
    public static String toSnakeCase(String camel) {
        if (camel == null || camel.isEmpty()) {
            return camel;
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < camel.length(); i++) {
            char c = camel.charAt(i);
            if (Character.isUpperCase(c)) {
                if (i > 0) {
                    sb.append('_');
                }
                sb.append(Character.toLowerCase(c));
            } else {
                sb.append(c);
            }
        }
        return sb.toString();
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [StringUtils](/java/easy/util/StringUtils.md) |
| calls | [toString](/java/easy/model/User/toString.md) |
