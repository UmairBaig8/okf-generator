---
concept_id: ruby/complex/services/report_service/schedule
description: Schedule a report to run on a recurring basis.
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
timestamp: '2026-07-10T15:03:07Z'
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

```rb
    def schedule(title, schedule = "daily")
      report = Models::ScheduledReport.new(next_id, title, schedule)
      @reports << report
      report
    end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report_service](/ruby/complex/services/report_service.md) |
