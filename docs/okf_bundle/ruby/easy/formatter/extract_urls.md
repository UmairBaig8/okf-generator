---
concept_id: ruby/easy/formatter/extract_urls
description: Extract all URLs from a block of text.
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
timestamp: '2026-07-10T15:03:07Z'
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

```rb
  def self.extract_urls(text, &block)
    urls = text.to_s.scan(%r{https?://[^\s]+})
    urls.each(&block) if block
    urls
  end
```

## Relationships

| Type | Target |
|------|--------|
| related | [formatter](/ruby/easy/formatter.md) |
