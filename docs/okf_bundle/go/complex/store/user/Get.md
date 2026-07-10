---
concept_id: go/complex/store/user/Get
description: Get retrieves a single user by ID.
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
timestamp: '2026-07-10T17:15:25Z'
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

```go
func (s *UserStore) Get(id string) (User, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	user, ok := s.users[id]
	if !ok {
		return User{}, fmt.Errorf("user %q not found", id)
	}
	return user, nil
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/go/complex/store/user.md) |
| called_by | [GetUser](/go/complex/handlers/user/GetUser.md) |
