---
description: Generate a new report from the given data source.
resource: ruby/complex/services/report_service.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:44:20Z'
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

## Related

- [report_service](/ruby/complex/services/report_service.md)
