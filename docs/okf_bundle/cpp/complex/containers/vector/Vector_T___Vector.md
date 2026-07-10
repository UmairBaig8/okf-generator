---
concept_id: cpp/complex/containers/vector/Vector_T___Vector
language: cpp
okf_version: '0.2'
resource: cpp/complex/containers/vector.cpp
tags:
- lang:cpp
- type:Function
- module:cpp
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: Vector<T>::Vector
type: Function
---

# Vector<T>::Vector

## Signature

```cpp
template<<typename T>> Vector<T>::Vector()
```

## Type Parameters

- `typename T`

## Source
Lines 7–8 in `cpp/complex/containers/vector.cpp`

```cpp
Vector<T>::Vector() noexcept
    : data_(nullptr), size_(0), capacity_(0) {}
```

## Relationships

| Type | Target |
|------|--------|
| related | [vector](/cpp/complex/containers/vector.md) |
