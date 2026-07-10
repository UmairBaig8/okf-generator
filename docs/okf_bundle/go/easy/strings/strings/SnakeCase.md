---
concept_id: go/easy/strings/strings/SnakeCase
description: SnakeCase converts a CamelCase string to snake_case.
language: go
okf_version: '0.2'
resource: go/easy/strings/strings.go
tags:
- lang:go
- type:Function
- module:go
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: SnakeCase
type: Function
---

# SnakeCase

SnakeCase converts a CamelCase string to snake_case.

## Signature

```go
func SnakeCase(s string) string
```

## Docstring

SnakeCase converts a CamelCase string to snake_case.

## Source
Lines 10–23 in `go/easy/strings/strings.go`

```go
func SnakeCase(s string) string {
	var result strings.Builder
	for i, r := range s {
		if unicode.IsUpper(r) {
			if i > 0 {
				result.WriteRune('_')
			}
			result.WriteRune(unicode.ToLower(r))
		} else {
			result.WriteRune(r)
		}
	}
	return result.String()
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [strings](/go/easy/strings/strings.md) |
