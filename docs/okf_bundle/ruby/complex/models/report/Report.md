---
concept_id: ruby/complex/models/report/Report
language: ruby
okf_version: '0.2'
resource: ruby/complex/models/report.rb
tags:
- lang:ruby
- type:Class
- module:ruby
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: Report
type: Class
---

# Report

## Signature

```ruby
class Report
```

## Methods

- `initialize`
- `to_h`
- `summary`

## Source
Lines 3–26 in `ruby/complex/models/report.rb`

```rb
  class Report
    attr_reader :id, :title, :generated_at
    attr_accessor :data

    def initialize(id, title, data = {})
      @id = id
      @title = title
      @data = data
      @generated_at = Time.now.utc
    end

    def to_h
      {
        id: @id,
        title: @title,
        data: @data,
        generated_at: @generated_at.iso8601
      }
    end

    def summary
      "#{@title} (#{@data.length} entries)"
    end
  end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report](/ruby/complex/models/report.md) |
