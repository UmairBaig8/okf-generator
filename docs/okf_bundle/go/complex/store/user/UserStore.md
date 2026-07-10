---
concept_id: go/complex/store/user/UserStore
description: UserStore provides thread-safe CRUD operations for User entities.
language: go
okf_version: '0.2'
resource: go/complex/store/user.go
tags:
- lang:go
- type:Class
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:57:28Z'
title: UserStore
type: Class
---

# UserStore

UserStore provides thread-safe CRUD operations for User entities.

## Signature

```go
type UserStore struct
```

## Docstring

UserStore provides thread-safe CRUD operations for User entities.

## Methods

- `mu`
- `users`
- `next`

## Source
Lines 25–29 in `go/complex/store/user.go`

```go
type UserStore struct {
	mu    sync.RWMutex
	users map[string]User
	next  int
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/go/complex/store/user.md) |
