---
concept_id: c/easy/math/int_sqrt
description: include "math.h"
language: c
okf_version: '0.2'
resource: c/easy/math.c
tags:
- lang:c
- type:Function
- module:c
- domain:easy
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: int_sqrt
type: Function
---

# int_sqrt

include "math.h"

## Signature

```c
int int_sqrt(int n)
```

## Docstring

include "math.h"

## Source
Lines 3–12 in `c/easy/math.c`

```c
int int_sqrt(int n) {
    if (n <= 0) return 0;
    int x = n;
    int y = (x + 1) / 2;
    while (y < x) {
        x = y;
        y = (x + n / x) / 2;
    }
    return x;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [math](/c/easy/math.md) |
