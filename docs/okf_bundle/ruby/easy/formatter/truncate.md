---
concept_id: ruby/easy/formatter/truncate
description: Truncate text to a maximum length, appending an ellipsis.
language: ruby
okf_version: '0.2'
resource: ruby/easy/formatter.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-16T07:24:59Z'
title: truncate
type: Function
---

# truncate

Truncate text to a maximum length, appending an ellipsis.

## Signature

```ruby
def self.truncate(text, max_len = 60)
```

## Visibility

- `singleton`

## Docstring

Truncate text to a maximum length, appending an ellipsis.
@param text [String] input text
@param max_len [Integer] maximum length
@return [String] truncated text

## Returns
`String`

## Source
Lines 23–27 in `ruby/easy/formatter.rb`

## Relationships

| Type | Target |
|------|--------|
| related | [formatter](/ruby/easy/formatter.md) |
