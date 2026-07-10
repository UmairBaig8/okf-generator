---
concept_id: cpp/complex/containers/vector/Vector_T___reserve
language: cpp
okf_version: '0.2'
resource: cpp/complex/containers/vector.cpp
tags:
- lang:cpp
- type:Function
- module:cpp
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: Vector<T>::reserve
type: Function
---

# Vector<T>::reserve

## Signature

```cpp
template<<typename T>> void Vector<T>::reserve(std::size_t new_cap)
```

## Type Parameters

- `typename T`

## Source
Lines 87–91 in `cpp/complex/containers/vector.cpp`

```cpp
void Vector<T>::reserve(std::size_t new_cap) {
    if (new_cap > capacity_) {
        reallocate(new_cap);
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [vector](/cpp/complex/containers/vector.md) |
