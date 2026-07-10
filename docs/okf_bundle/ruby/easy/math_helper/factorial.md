---
concept_id: ruby/easy/math_helper/factorial
description: Compute the factorial of a non-negative integer.
language: ruby
okf_version: '0.2'
resource: ruby/easy/math_helper.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: factorial
type: Function
---

# factorial

Compute the factorial of a non-negative integer.

## Signature

```ruby
def self.factorial(n)
```

## Visibility

- `singleton`

## Docstring

Compute the factorial of a non-negative integer.
@param n [Integer] input number
@return [Integer] factorial result

## Returns
`Integer`

## Source
Lines 6–9 in `ruby/easy/math_helper.rb`

```rb
  def self.factorial(n)
    raise ArgumentError, "n must be non-negative" if n < 0
    (1..n).reduce(1) { |product, i| product * i }
  end
```

## Relationships

| Type | Target |
|------|--------|
| related | [math_helper](/ruby/easy/math_helper.md) |
