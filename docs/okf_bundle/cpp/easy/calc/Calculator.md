---
concept_id: cpp/easy/calc/Calculator
description: A simple calculator that maintains an internal accumulator.
language: c
okf_version: '0.2'
resource: cpp/easy/calc.h
tags:
- lang:c
- type:Function
- module:cpp
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:11Z'
title: Calculator
type: Function
---

# Calculator

A simple calculator that maintains an internal accumulator.

## Signature

```c
class Calculator()
```

## Docstring

A simple calculator that maintains an internal accumulator.

## Source
Lines 8–34 in `cpp/easy/calc.h`

```h
    class Calculator {
    public:
        /// Construct a Calculator with an optional initial value.
        explicit Calculator(double initial = 0.0);

        /// Add a value to the accumulator.
        Calculator& add(double value);

        /// Subtract a value from the accumulator.
        Calculator& subtract(double value);

        /// Multiply the accumulator by a value.
        Calculator& multiply(double value);

        /// Divide the accumulator by a value.
        /// @throws std::invalid_argument if value is zero.
        Calculator& divide(double value);

        /// Return the current accumulator value.
        double value() const;

        /// Reset the accumulator to zero.
        void clear();

    private:
        double accumulator_;
    };
```

## Relationships

| Type | Target |
|------|--------|
| related | [calc](/cpp/easy/calc.md) |
