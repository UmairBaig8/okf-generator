---
concept_id: c/complex/linked_list/node_create_int_value
language: c
okf_version: '0.2'
resource: c/complex/linked_list.c
tags:
- lang:c
- type:Function
- module:c
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: node_create(int value)
type: Function
---

# node_create(int value)

## Signature

```c
Node node_create(int value)()
```

## Source
Lines 12–18 in `c/complex/linked_list.c`

```c
static Node* node_create(int value) {
    Node* node = (Node*)malloc(sizeof(Node));
    if (!node) return NULL;
    node->data = value;
    node->next = NULL;
    return node;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [linked_list](/c/complex/linked_list.md) |
