---
concept_id: go/complex/store/user/NewUserStore
description: NewUserStore creates and returns a new empty UserStore.
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
timestamp: '2026-07-07T06:58:41Z'
title: NewUserStore
type: Function
---

# NewUserStore

NewUserStore creates and returns a new empty UserStore.

## Signature

```go
func NewUserStore() *UserStore
```

## Docstring

NewUserStore creates and returns a new empty UserStore.

## Source
Lines 32–37 in `go/complex/store/user.go`

```go
func NewUserStore() *UserStore {
	return &UserStore{
		users: make(map[string]User),
		next:  1,
	}
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/go/complex/store/user.md) |
