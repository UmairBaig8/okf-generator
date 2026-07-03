---
description: Truncate text to a maximum length, appending an ellipsis.
resource: ruby/easy/formatter.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:44:10Z'
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

## Related

- [formatter](/ruby/easy/formatter.md)
