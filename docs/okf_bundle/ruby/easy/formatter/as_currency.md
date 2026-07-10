---
concept_id: ruby/easy/formatter/as_currency
description: Format a number as currency with the given symbol.
language: ruby
okf_version: '0.2'
resource: ruby/easy/formatter.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:easy
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: as_currency
type: Function
---

# as_currency

Format a number as currency with the given symbol.

## Signature

```ruby
def self.as_currency(amount, symbol = "$")
```

## Visibility

- `singleton`

## Docstring

Format a number as currency with the given symbol.
@param amount [Numeric] the amount to format
@param symbol [String] currency symbol (default $)
@return [String] formatted currency string

## Returns
`String`

## Source
Lines 7–10 in `ruby/easy/formatter.rb`

```rb
  def self.as_currency(amount, symbol = "$")
    formatted = format("%.2f", amount)
    "#{symbol}#{formatted}"
  end
```

## Relationships

| Type | Target |
|------|--------|
| related | [formatter](/ruby/easy/formatter.md) |
