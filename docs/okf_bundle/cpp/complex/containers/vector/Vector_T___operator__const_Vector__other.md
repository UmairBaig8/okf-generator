---
concept_id: cpp/complex/containers/vector/Vector_T___operator__const_Vector__other
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
timestamp: '2026-07-10T14:55:11Z'
title: '& Vector<T>::operator=(const Vector& other)'
type: Function
---

# & Vector<T>::operator=(const Vector& other)

## Signature

```cpp
template<<typename T>> Vector<T> & Vector<T>::operator=(const Vector& other)()
```

## Type Parameters

- `typename T`

## Source
Lines 27–35 in `cpp/complex/containers/vector.cpp`

```cpp
Vector<T>& Vector<T>::operator=(const Vector& other) {
    if (this != &other) {
        Vector tmp(other);
        std::swap(data_, tmp.data_);
        std::swap(size_, tmp.size_);
        std::swap(capacity_, tmp.capacity_);
    }
    return *this;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [vector](/cpp/complex/containers/vector.md) |
