---
description: Create inserts a new user and returns it with an auto-generated ID.
resource: go/complex/store/user.go
tags:
- lang:go
- type:Function
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:27Z'
title: Create
type: Function
---

# Create

Create inserts a new user and returns it with an auto-generated ID.

## Signature

```go
func (s *UserStore) Create(input CreateUserInput) (User, error)
```

## Docstring

Create inserts a new user and returns it with an auto-generated ID.

## Source
Lines 62–75 in `go/complex/store/user.go`

## Related

- [user](/go/complex/store/user.md)

## Called By

- [CreateUser](/go/complex/handlers/user/CreateUser.md)
