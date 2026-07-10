---
concept_id: go/complex/store/user/User
description: User represents a user entity in the system.
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
timestamp: '2026-07-07T06:58:41Z'
title: User
type: Class
---

# User

User represents a user entity in the system.

## Signature

```go
type User struct
```

## Docstring

User represents a user entity in the system.

## Methods

- `ID`
- `Name`
- `Email`
- `CreatedAt`

## Source
Lines 11–16 in `go/complex/store/user.go`

```go
type User struct {
	ID        string    `json:"id"`
	Name      string    `json:"name"`
	Email     string    `json:"email"`
	CreatedAt time.Time `json:"created_at"`
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/go/complex/store/user.md) |
