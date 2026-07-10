---
concept_id: ruby/easy/formatter/TextFormatter
description: Class-based wrapper for the Formatter module.
language: ruby
okf_version: '0.2'
resource: ruby/easy/formatter.rb
tags:
- lang:ruby
- type:Class
- module:ruby
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: TextFormatter
type: Class
---

# TextFormatter

Class-based wrapper for the Formatter module.

## Signature

```ruby
class TextFormatter
```

## Docstring

Class-based wrapper for the Formatter module.

## Methods

- `initialize`
- `title_case`
- `truncate`

## Source
Lines 41–55 in `ruby/easy/formatter.rb`

```rb
class TextFormatter
  attr_reader :text

  def initialize(text)
    @text = text
  end

  def title_case
    Formatter.title_case(@text)
  end

  def truncate(max_len = 60)
    Formatter.truncate(@text, max_len)
  end
end
```

## Relationships

| Type | Target |
|------|--------|
| related | [formatter](/ruby/easy/formatter.md) |
