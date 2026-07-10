---
concept_id: c/easy/math/int_clamp
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
title: int_clamp
type: Function
---

# int_clamp

## Signature

```c
int int_clamp(int value, int low, int high)
```

## Source
Lines 18–22 in `c/easy/math.c`

```c
int int_clamp(int value, int low, int high) {
    if (value < low) return low;
    if (value > high) return high;
    return value;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [math](/c/easy/math.md) |
