---
concept_id: go/complex/store/user/List
description: List returns all users in the store.
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

```go
func (s *UserStore) List() ([]User, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	result := make([]User, 0, len(s.users))
	for _, u := range s.users {
		result = append(result, u)
	}
	return result, nil
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/go/complex/store/user.md) |
| called_by | [ListUsers](/go/complex/handlers/user/ListUsers.md) |
