---
concept_id: ruby/complex/services/report_service/generate
description: Generate a new report from the given data source.
language: ruby
okf_version: '0.2'
resource: ruby/complex/services/report_service.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:11Z'
title: generate
type: Function
---

# generate

Generate a new report from the given data source.

## Signature

```ruby
def generate(title)
```

## Docstring

Generate a new report from the given data source.
@param title [String] report title
@yield [Report] the newly created report for customization
@return [Models::Report] the generated report

## Returns
`Models::Report`

## Source
Lines 14–19 in `ruby/complex/services/report_service.rb`

```rb
    def generate(title)
      report = Models::Report.new(next_id, title)
      yield report if block_given?
      @reports << report
      report
    end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report_service](/ruby/complex/services/report_service.md) |
