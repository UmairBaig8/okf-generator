---
concept_id: ruby/easy/formatter/Formatter
description: String and number formatting utilities.
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
timestamp: '2026-07-10T14:57:28Z'
title: Formatter
type: Class
---

# Formatter

String and number formatting utilities.

## Signature

```ruby
module Formatter
```

## Docstring

String and number formatting utilities.

## Methods

- `as_currency`
- `title_case`
- `truncate`
- `extract_urls`

## Source
Lines 2–38 in `ruby/easy/formatter.rb`

```rb
module Formatter
  # Format a number as currency with the given symbol.
  # @param amount [Numeric] the amount to format
  # @param symbol [String] currency symbol (default $)
  # @return [String] formatted currency string
  def self.as_currency(amount, symbol = "$")
    formatted = format("%.2f", amount)
    "#{symbol}#{formatted}"
  end

  # Convert a string to Title Case.
  # @param text [String] input text
  # @return [String] title-cased text
  def self.title_case(text)
    text.to_s.split.map(&:capitalize).join(" ")
  end

  # Truncate text to a maximum length, appending an ellipsis.
  # @param text [String] input text
  # @param max_len [Integer] maximum length
  # @return [String] truncated text
  def self.truncate(text, max_len = 60)
    return "" if text.nil?
    return text if text.length <= max_len
    text[0..max_len - 4] + "..."
  end

  # Extract all URLs from a block of text.
  # @param text [String] input text
  # @yield [String] each found URL
  # @return [Array<String>] list of found URLs
  def self.extract_urls(text, &block)
    urls = text.to_s.scan(%r{https?://[^\s]+})
    urls.each(&block) if block
    urls
  end
end
```

## Relationships

| Type | Target |
|------|--------|
| related | [formatter](/ruby/easy/formatter.md) |
