---
concept_id: cpp/complex/main/main
description: include "containers/vector.h"
language: cpp
okf_version: '0.2'
resource: cpp/complex/main.cpp
tags:
- lang:cpp
- type:Function
- module:cpp
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:57:28Z'
title: main
type: Function
---

# main

include "containers/vector.h"

## Signature

```cpp
int main()
```

## Docstring

include "containers/vector.h"
include <iostream>
include <cassert>

## Source
Lines 5–28 in `cpp/complex/main.cpp`

```cpp
int main() {
    okfgen::Vector<int> vec;
    assert(vec.empty());
    assert(vec.size() == 0);

    vec.push_back(10);
    vec.push_back(20);
    vec.push_back(30);
    assert(vec.size() == 3);
    assert(vec.at(1) == 20);

    vec.pop_back();
    assert(vec.size() == 2);

    okfgen::Vector<int> copy(vec);
    assert(copy.size() == 2);
    assert(copy[0] == 10);

    vec.clear();
    assert(vec.empty());

    std::cout << "All Vector tests passed." << std::endl;
    return 0;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [complex](/cpp/complex/main.md) |
