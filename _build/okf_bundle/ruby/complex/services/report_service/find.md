---
description: Find a report by its ID.
resource: ruby/complex/services/report_service.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:44:20Z'
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

## Related

- [report_service](/ruby/complex/services/report_service.md)

## Called By

- [ReportService](/ruby/complex/services/report_service/ReportService.md)
- [Services](/ruby/complex/services/report_service/Services.md)
