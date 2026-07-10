---
concept_id: cpp/easy/calc/Calculator__multiply_double_value
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
title: '& Calculator::multiply(double value)'
type: Function
---

# & Calculator::multiply(double value)

## Signature

```cpp
Calculator & Calculator::multiply(double value)()
```

## Source
Lines 19–22 in `cpp/easy/calc.cpp`

```cpp
Calculator& Calculator::multiply(double value) {
    accumulator_ *= value;
    return *this;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [calc](/cpp/easy/calc.md) |
