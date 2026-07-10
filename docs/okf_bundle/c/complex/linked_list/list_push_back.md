---
concept_id: c/complex/linked_list/list_push_back
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
timestamp: '2026-07-10T15:03:07Z'
title: list_push_back
type: Function
---

# list_push_back

## Signature

```c
int list_push_back(LinkedList* list, int value)
```

## Source
Lines 29–41 in `c/complex/linked_list.c`

```c
int list_push_back(LinkedList* list, int value) {
    Node* node = node_create(value);
    if (!node) return -1;
    if (!list->head) {
        list->head = node;
    } else {
        Node* cur = list->head;
        while (cur->next) cur = cur->next;
        cur->next = node;
    }
    list->size++;
    return 0;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [linked_list](/c/complex/linked_list.md) |
