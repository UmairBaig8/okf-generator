---
concept_id: java/complex/repository/OrderRepo/OrderRepo
description: In-memory implementation of {@link Repository} for Order entities.
language: java
okf_version: '0.2'
resource: java/complex/repository/OrderRepo.java
tags:
- lang:java
- type:Class
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:57:28Z'
title: OrderRepo
type: Class
---

# OrderRepo

In-memory implementation of {@link Repository} for Order entities.

## Signature

```java
public class OrderRepo
```

## Visibility

- `public`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `store` | `Map<String, Order>` | `private final` |

## Docstring

In-memory implementation of {@link Repository} for Order entities.

## Methods

- `save`
- `findById`
- `findAll`
- `deleteById`
- `count`
- `findByCustomerId`

## Source
Lines 24–67 in `java/complex/repository/OrderRepo.java`

```java
public class OrderRepo implements Repository<Order> {

    private final Map<String, Order> store = new ConcurrentHashMap<>();

    @Override
    public Order save(Order order) {
        Objects.requireNonNull(order, "Order must not be null");
        store.put(order.getId(), order);
        return order;
    }

    @Override
    public Optional<Order> findById(String id) {
        return Optional.ofNullable(store.get(id));
    }

    @Override
    public List<Order> findAll() {
        return new ArrayList<>(store.values());
    }

    @Override
    public void deleteById(String id) {
        store.remove(id);
    }

    @Override
    public long count() {
        return store.size();
    }

    /**
     * Finds all orders belonging to a specific customer.
     *
     * @param customerId the customer identifier
     * @return list of orders for that customer
     */
    public List<Order> findByCustomerId(String customerId) {
        return store.values().stream()
                .filter(o -> o.getCustomerId().equals(customerId))
                .sorted()
                .collect(Collectors.toList());
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [OrderRepo](/java/complex/repository/OrderRepo.md) |
| calls | [equals](/java/complex/model/Order/equals.md) |
| calls | [getCustomerId](/java/complex/model/Order/getCustomerId.md) |
