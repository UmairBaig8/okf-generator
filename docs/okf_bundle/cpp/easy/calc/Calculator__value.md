---
concept_id: cpp/easy/calc/Calculator__value
language: cpp
okf_version: '0.2'
resource: cpp/easy/calc.cpp
tags:
- lang:cpp
- type:Function
- module:cpp
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: Calculator::value
type: Function
---

# Calculator::value

## Signature

```cpp
double Calculator::value()
```

## Source
Lines 32–34 in `cpp/easy/calc.cpp`

```cpp
double Calculator::value() const {
    return accumulator_;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [calc](/cpp/easy/calc.md) |
