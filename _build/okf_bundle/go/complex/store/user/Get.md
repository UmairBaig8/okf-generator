---
description: Get retrieves a single user by ID.
resource: go/complex/store/user.go
tags:
- lang:go
- type:Function
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:27Z'
title: Get
type: Function
---

# Get

Get retrieves a single user by ID.

## Signature

```go
func (s *UserStore) Get(id string) (User, error)
```

## Docstring

Get retrieves a single user by ID.

## Source
Lines 51–59 in `go/complex/store/user.go`

## Related

- [user](/go/complex/store/user.md)

## Called By

- [GetUser](/go/complex/handlers/user/GetUser.md)
