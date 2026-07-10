---
concept_id: cpp/complex/containers/vector/Vector_T___empty
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
timestamp: '2026-07-10T15:03:07Z'
title: Vector<T>::empty
type: Function
---

# Vector<T>::empty

## Signature

```cpp
template<<typename T>> bool Vector<T>::empty()
```

## Type Parameters

- `typename T`

## Source
Lines 77–79 in `cpp/complex/containers/vector.cpp`

```cpp
bool Vector<T>::empty() const noexcept {
    return size_ == 0;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [vector](/cpp/complex/containers/vector.md) |
