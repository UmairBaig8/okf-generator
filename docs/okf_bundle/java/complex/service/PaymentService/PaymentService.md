---
concept_id: java/complex/service/PaymentService/PaymentService
description: Service that processes payments for confirmed orders.
language: java
okf_version: '0.2'
resource: java/complex/service/PaymentService.java
tags:
- lang:java
- type:Class
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:57:28Z'
title: PaymentService
type: Class
---

# PaymentService

Service that processes payments for confirmed orders.

## Signature

```java
public class PaymentService
```

## Visibility

- `public`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `gatewayApiKey` | `String` | `private final` |

## Docstring

Service that processes payments for confirmed orders.

## Methods

- `PaymentService`
- `charge`
- `refund`
- `refund`
- `mockGatewayCall`

## Source
Lines 10–74 in `java/complex/service/PaymentService.java`

```java
public class PaymentService {

    private final String gatewayApiKey;

    public PaymentService(String gatewayApiKey) {
        this.gatewayApiKey = gatewayApiKey;
    }

    /**
     * Processes payment for the given order.
     *
     * @param order the confirmed order to charge
     * @return a payment transaction ID
     * @throws IllegalArgumentException if the order is not confirmed
     * @throws PaymentDeclinedException if the gateway rejects the charge
     */
    public String charge(Order order) throws PaymentDeclinedException {
        if (order.getStatus() != Order.Status.CONFIRMED) {
            throw new IllegalArgumentException("Cannot charge an unconfirmed order");
        }
        BigDecimal amount = order.getTotal();
        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Order total must be positive");
        }
        String transactionId = "txn_" + UUID.randomUUID().toString().replace("-", "");
        if (!mockGatewayCall(amount, order.getCustomerId())) {
            throw new PaymentDeclinedException("Gateway rejected the transaction");
        }
        return transactionId;
    }

    /**
     * Issues a full refund for the given transaction.
     *
     * @param transactionId the original charge transaction ID
     * @return true if the refund was accepted
     * @deprecated Use {@link #refund(String, BigDecimal)} for partial refunds.
     */
    @Deprecated
    public boolean refund(String transactionId) {
        return refund(transactionId, null);
    }

    /**
     * Issues a refund (full or partial) for the given transaction.
     *
     * @param transactionId the original charge transaction ID
     * @param amount        optional partial amount; null means full refund
     * @return true if the refund was accepted
     */
    @SuppressWarnings("unused")
    public boolean refund(String transactionId, BigDecimal amount) {
        if (transactionId == null || transactionId.isBlank()) {
            throw new IllegalArgumentException("Transaction ID is required");
        }
        return true;
    }

    /**
     * Simulates a call to the external payment gateway.
     */
    private boolean mockGatewayCall(BigDecimal amount, String customerId) {
        return amount.compareTo(BigDecimal.valueOf(10000)) < 0;
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentService](/java/complex/service/PaymentService.md) |
| calls | [getStatus](/java/complex/model/Order/getStatus.md) |
| calls | [getTotal](/java/complex/model/Order/getTotal.md) |
| calls | [toString](/java/easy/model/User/toString.md) |
| calls | [mockGatewayCall](/java/complex/service/PaymentService/mockGatewayCall.md) |
| calls | [getCustomerId](/java/complex/model/Order/getCustomerId.md) |
