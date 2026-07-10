---
concept_id: cpp/easy/calc/Calculator__subtract_double_value
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
title: '& Calculator::subtract(double value)'
type: Function
---

# & Calculator::subtract(double value)

## Signature

```cpp
Calculator & Calculator::subtract(double value)()
```

## Source
Lines 14–17 in `cpp/easy/calc.cpp`

```cpp
Calculator& Calculator::subtract(double value) {
    accumulator_ -= value;
    return *this;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [calc](/cpp/easy/calc.md) |
