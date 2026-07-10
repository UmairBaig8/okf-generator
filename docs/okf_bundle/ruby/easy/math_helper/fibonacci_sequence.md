---
concept_id: ruby/easy/math_helper/fibonacci_sequence
description: Generate a sequence of n Fibonacci numbers.
language: ruby
okf_version: '0.2'
resource: ruby/easy/math_helper.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:easy
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: fibonacci_sequence
type: Function
---

# fibonacci_sequence

Generate a sequence of n Fibonacci numbers.

## Signature

```ruby
def self.fibonacci_sequence(count)
```

## Visibility

- `singleton`

## Docstring

Generate a sequence of n Fibonacci numbers.
@param count [Integer] how many numbers to generate
@return [Array<Integer>] Fibonacci sequence

## Returns
`Array<Integer>`

## Source
Lines 22–29 in `ruby/easy/math_helper.rb`

```rb
  def self.fibonacci_sequence(count)
    return [] if count <= 0
    seq = [0, 1]
    while seq.length < count
      seq << seq[-1] + seq[-2]
    end
    seq.first(count)
  end
```

## Relationships

| Type | Target |
|------|--------|
| related | [math_helper](/ruby/easy/math_helper.md) |
