---
concept_id: c/complex/linked_list/Node
language: c
okf_version: '0.2'
resource: c/complex/linked_list.h
tags:
- lang:c
- type:Class
- module:c
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: Node
type: Class
---

# Node

## Signature

```c
struct Node
```

## Source
Lines 5–8 in `c/complex/linked_list.h`

```h
typedef struct Node {
    int data;
    struct Node* next;
} Node;
```

## Relationships

| Type | Target |
|------|--------|
| related | [linked_list](/c/complex/linked_list.md) |
