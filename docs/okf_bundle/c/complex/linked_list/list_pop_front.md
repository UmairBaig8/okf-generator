---
concept_id: c/complex/linked_list/list_pop_front
language: c
okf_version: '0.2'
resource: c/complex/linked_list.c
tags:
- lang:c
- type:Function
- module:c
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: list_pop_front
type: Function
---

# list_pop_front

## Signature

```c
int list_pop_front(LinkedList* list)
```

## Source
Lines 43–51 in `c/complex/linked_list.c`

```c
int list_pop_front(LinkedList* list) {
    if (!list->head) return 0;
    Node* old = list->head;
    int value = old->data;
    list->head = old->next;
    free(old);
    list->size--;
    return value;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [linked_list](/c/complex/linked_list.md) |
