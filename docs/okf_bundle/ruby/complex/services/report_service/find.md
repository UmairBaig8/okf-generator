---
concept_id: ruby/complex/services/report_service/find
description: Find a report by its ID.
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
timestamp: '2026-07-10T18:45:41Z'
title: find
type: Function
---

# find

Find a report by its ID.

## Signature

```ruby
def find(id)
```

## Docstring

Find a report by its ID.
@param id [Integer] report identifier
@return [Models::Report, nil]

## Returns
`Models::Report, nil`

## Source
Lines 34–36 in `ruby/complex/services/report_service.rb`

## Relationships

| Type | Target |
|------|--------|
| related | [report_service](/ruby/complex/services/report_service.md) |
| called_by | [ReportService](/ruby/complex/services/report_service/ReportService.md) |
| called_by | [Services](/ruby/complex/services/report_service/Services.md) |
| called_by | [Router](/scala/complex/Router/Router.md) |
| called_by | [dispatch](/scala/complex/Router/dispatch.md) |
