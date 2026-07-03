---
description: Schedule a report to run on a recurring basis.
resource: ruby/complex/services/report_service.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:44:20Z'
title: schedule
type: Function
---

# schedule

Schedule a report to run on a recurring basis.

## Signature

```ruby
def schedule(title, schedule = "daily")
```

## Docstring

Schedule a report to run on a recurring basis.
@param title [String] report title
@param schedule [String] "daily" or "hourly"
@return [Models::ScheduledReport]

## Returns
`Models::ScheduledReport`

## Source
Lines 25–29 in `ruby/complex/services/report_service.rb`

## Related

- [report_service](/ruby/complex/services/report_service.md)
