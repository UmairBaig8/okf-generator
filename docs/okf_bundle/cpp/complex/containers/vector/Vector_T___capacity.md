---
concept_id: cpp/complex/containers/vector/Vector_T___capacity
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
timestamp: '2026-07-10T17:15:25Z'
title: Vector<T>::capacity
type: Function
---

# Vector<T>::capacity

## Signature

```cpp
template<<typename T>> std::size_t Vector<T>::capacity()
```

## Type Parameters

- `typename T`

## Source
Lines 94–96 in `cpp/complex/containers/vector.cpp`

```cpp
std::size_t Vector<T>::capacity() const noexcept {
    return capacity_;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [vector](/cpp/complex/containers/vector.md) |
