---
concept_id: cpp/complex/containers/vector/Vector_T___push_back
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
timestamp: '2026-07-10T14:57:28Z'
title: Vector<T>::push_back
type: Function
---

# Vector<T>::push_back

## Signature

```cpp
template<<typename T>> void Vector<T>::push_back(const T& value)
```

## Type Parameters

- `typename T`

## Source
Lines 43–48 in `cpp/complex/containers/vector.cpp`

```cpp
void Vector<T>::push_back(const T& value) {
    if (size_ == capacity_) {
        reallocate(capacity_ == 0 ? kInitialCapacity : capacity_ * 2);
    }
    data_[size_++] = value;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [vector](/cpp/complex/containers/vector.md) |
