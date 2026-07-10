---
concept_id: c/complex/linked_list/list_create_void
description: include "linked_list.h"
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
timestamp: '2026-07-10T17:15:25Z'
title: list_create(void)
type: Function
---

# list_create(void)

include "linked_list.h"

## Signature

```c
LinkedList list_create(void)()
```

## Docstring

include "linked_list.h"
include <stdlib.h>

## Source
Lines 4–10 in `c/complex/linked_list.c`

```c
LinkedList* list_create(void) {
    LinkedList* list = (LinkedList*)malloc(sizeof(LinkedList));
    if (!list) return NULL;
    list->head = NULL;
    list->size = 0;
    return list;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [linked_list](/c/complex/linked_list.md) |
