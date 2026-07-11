---
concept_id: java/complex/model/Order/getCustomerId
language: java
okf_version: '0.2'
resource: java/complex/model/Order.java
tags:
- lang:java
- type:Function
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-11T19:03:44Z'
title: getCustomerId
type: Function
---

# getCustomerId

## Signature

```java
String getCustomerId()
```

## Visibility

- `public`

## Source
Lines 84–84 in `java/complex/model/Order.java`

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/java/complex/model/Order.md) |
| called_by | [OrderRepo](/java/complex/repository/OrderRepo/OrderRepo.md) |
| called_by | [findByCustomerId](/java/complex/repository/OrderRepo/findByCustomerId.md) |
| called_by | [PaymentService](/java/complex/service/PaymentService/PaymentService.md) |
| called_by | [charge](/java/complex/service/PaymentService/charge.md) |
