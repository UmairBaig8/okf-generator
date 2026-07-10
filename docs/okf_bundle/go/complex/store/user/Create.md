---
concept_id: go/complex/store/user/Create
description: Create inserts a new user and returns it with an auto-generated ID.
language: go
okf_version: '0.2'
resource: go/complex/store/user.go
tags:
- lang:go
- type:Function
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T19:56:16Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [user](/go/complex/store/user.md) |
| called_by | [CreateUser](/go/complex/handlers/user/CreateUser.md) |
