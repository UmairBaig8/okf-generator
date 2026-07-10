---
concept_id: go/complex/handlers/user/CreateUser
description: CreateUser returns an HTTP handler that creates a new user.
language: go
okf_version: '0.2'
resource: go/complex/handlers/user.go
tags:
- lang:go
- type:Function
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T19:11:07Z'
title: CreateUser
type: Function
---

# CreateUser

CreateUser returns an HTTP handler that creates a new user.

## Signature

```go
func CreateUser(s *store.UserStore) http.HandlerFunc
```

## Docstring

CreateUser returns an HTTP handler that creates a new user.

## Source
Lines 39–54 in `go/complex/handlers/user.go`

## Relationships

| Type | Target |
|------|--------|
| related | [user](/go/complex/handlers/user.md) |
| calls | [Create](/go/complex/store/user/Create.md) |
| called_by | [registerRoutes](/go/complex/server/server/registerRoutes.md) |
