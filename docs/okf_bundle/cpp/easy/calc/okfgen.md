---
concept_id: cpp/easy/calc/okfgen
description: Namespace for basic arithmetic operations.
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
title: okfgen
type: Function
---

# okfgen

Namespace for basic arithmetic operations.

## Signature

```c
namespace okfgen()
```

## Docstring

Namespace for basic arithmetic operations.

## Source
Lines 5–36 in `cpp/easy/calc.h`

```h
namespace okfgen {

    /// A simple calculator that maintains an internal accumulator.
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

}  // namespace okfgen
```

## Relationships

| Type | Target |
|------|--------|
| related | [calc](/cpp/easy/calc.md) |
