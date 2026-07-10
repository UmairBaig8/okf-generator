---
concept_id: c/complex/linked_list/list_remove
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
timestamp: '2026-07-10T14:55:11Z'
title: list_remove
type: Function
---

# list_remove

## Signature

```c
int list_remove(LinkedList* list, int value)
```

## Source
Lines 53–67 in `c/complex/linked_list.c`

```c
int list_remove(LinkedList* list, int value) {
    Node *cur = list->head, *prev = NULL;
    while (cur) {
        if (cur->data == value) {
            if (prev) prev->next = cur->next;
            else list->head = cur->next;
            free(cur);
            list->size--;
            return 0;
        }
        prev = cur;
        cur = cur->next;
    }
    return -1;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [linked_list](/c/complex/linked_list.md) |
