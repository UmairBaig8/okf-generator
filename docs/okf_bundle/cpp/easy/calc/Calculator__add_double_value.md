---
concept_id: cpp/easy/calc/Calculator__add_double_value
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
title: '& Calculator::add(double value)'
type: Function
---

# & Calculator::add(double value)

## Signature

```cpp
Calculator & Calculator::add(double value)()
```

## Source
Lines 9–12 in `cpp/easy/calc.cpp`

```cpp
Calculator& Calculator::add(double value) {
    accumulator_ += value;
    return *this;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [calc](/cpp/easy/calc.md) |
