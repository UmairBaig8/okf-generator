---
concept_id: c/complex/linked_list/list_destroy
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
title: list_destroy
type: Function
---

# list_destroy

## Signature

```c
void list_destroy(LinkedList* list)
```

## Source
Lines 81–89 in `c/complex/linked_list.c`

```c
void list_destroy(LinkedList* list) {
    Node* cur = list->head;
    while (cur) {
        Node* next = cur->next;
        free(cur);
        cur = next;
    }
    free(list);
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [linked_list](/c/complex/linked_list.md) |
