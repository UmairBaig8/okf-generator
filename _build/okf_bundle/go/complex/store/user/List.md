---
description: List returns all users in the store.
resource: go/complex/store/user.go
tags:
- lang:go
- type:Function
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:27Z'
title: List
type: Function
---

# List

List returns all users in the store.

## Signature

```go
func (s *UserStore) List() ([]User, error)
```

## Docstring

List returns all users in the store.

## Source
Lines 40–48 in `go/complex/store/user.go`

## Related

- [user](/go/complex/store/user.md)

## Called By

- [ListUsers](/go/complex/handlers/user/ListUsers.md)
