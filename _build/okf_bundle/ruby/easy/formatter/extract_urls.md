---
description: Extract all URLs from a block of text.
resource: ruby/easy/formatter.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:44:10Z'
title: extract_urls
type: Function
---

# extract_urls

Extract all URLs from a block of text.

## Signature

```ruby
def self.extract_urls(text, &block)
```

## Visibility

- `singleton`

## Docstring

Extract all URLs from a block of text.
@param text [String] input text
@yield [String] each found URL
@return [Array<String>] list of found URLs

## Returns
`Array<String>`

## Source
Lines 33–37 in `ruby/easy/formatter.rb`

## Related

- [formatter](/ruby/easy/formatter.md)
