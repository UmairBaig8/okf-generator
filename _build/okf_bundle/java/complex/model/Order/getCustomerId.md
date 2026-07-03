---
resource: java/complex/model/Order.java
tags:
- lang:java
- type:Function
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:42Z'
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

## Related

- [Order](/java/complex/model/Order.md)

## Called By

- [OrderRepo](/java/complex/repository/OrderRepo/OrderRepo.md)
- [findByCustomerId](/java/complex/repository/OrderRepo/findByCustomerId.md)
- [PaymentService](/java/complex/service/PaymentService/PaymentService.md)
- [charge](/java/complex/service/PaymentService/charge.md)
