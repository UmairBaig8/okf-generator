---
concept_id: cpp/easy/calc/Calculator__divide_double_value
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
timestamp: '2026-07-10T14:57:28Z'
title: '& Calculator::divide(double value)'
type: Function
---

# & Calculator::divide(double value)

## Signature

```cpp
Calculator & Calculator::divide(double value)()
```

## Source
Lines 24–30 in `cpp/easy/calc.cpp`

```cpp
Calculator& Calculator::divide(double value) {
    if (value == 0.0) {
        throw std::invalid_argument("Division by zero");
    }
    accumulator_ /= value;
    return *this;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [calc](/cpp/easy/calc.md) |
