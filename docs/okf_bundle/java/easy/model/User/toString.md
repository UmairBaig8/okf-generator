---
concept_id: java/easy/model/User/toString
language: java
okf_version: '0.2'
resource: java/easy/model/User.java
tags:
- lang:java
- type:Function
- module:java
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T19:11:07Z'
title: toString
type: Function
---

# toString

## Signature

```java
String toString()
```

## Decorators

- `@Override`

## Visibility

- `public`

## Source
Lines 86–89 in `java/easy/model/User.java`

## Relationships

| Type | Target |
|------|--------|
| related | [User](/java/easy/model/User.md) |
| called_by | [PaymentService](/java/complex/service/PaymentService/PaymentService.md) |
| called_by | [charge](/java/complex/service/PaymentService/charge.md) |
| called_by | [StringUtils](/java/easy/util/StringUtils/StringUtils.md) |
| called_by | [toSnakeCase](/java/easy/util/StringUtils/toSnakeCase.md) |
| called_by | [ApiServer](/javascript/complex/server/ApiServer.md) |
| called_by | [_parseBody](/javascript/complex/server/parseBody.md) |
| called_by | [User](/kotlin/complex/src/main/kotlin/com/okfgen/service/model/User/User.md) |
| called_by | [toSnakeCase](/kotlin/easy/src/main/kotlin/com/okfgen/utils/Strings/toSnakeCase.md) |
