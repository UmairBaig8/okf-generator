---
concept_id: ruby/complex/services/report_service/ReportService
language: ruby
okf_version: '0.2'
resource: ruby/complex/services/report_service.rb
tags:
- lang:ruby
- type:Class
- module:ruby
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: ReportService
type: Class
---

# ReportService

## Signature

```ruby
class ReportService
```

## Methods

- `initialize`
- `generate`
- `schedule`
- `find`
- `run_due`
- `summary`
- `next_id`

## Source
Lines 5–61 in `ruby/complex/services/report_service.rb`

```rb
  class ReportService
    def initialize
      @reports = []
    end

    # Generate a new report from the given data source.
    # @param title [String] report title
    # @yield [Report] the newly created report for customization
    # @return [Models::Report] the generated report
    def generate(title)
      report = Models::Report.new(next_id, title)
      yield report if block_given?
      @reports << report
      report
    end

    # Schedule a report to run on a recurring basis.
    # @param title [String] report title
    # @param schedule [String] "daily" or "hourly"
    # @return [Models::ScheduledReport]
    def schedule(title, schedule = "daily")
      report = Models::ScheduledReport.new(next_id, title, schedule)
      @reports << report
      report
    end

    # Find a report by its ID.
    # @param id [Integer] report identifier
    # @return [Models::Report, nil]
    def find(id)
      @reports.find { |r| r.id == id }
    end

    # Execute all due scheduled reports.
    # @yield [Models::ScheduledReport] each report that was executed
    # @return [Array<Models::ScheduledReport>] executed reports
    def run_due
      due = @reports.select { |r| r.is_a?(Models::ScheduledReport) && r.due? }
      due.each do |report|
        ReportRunner.new(report).execute
        report.mark_as_run!
        yield report if block_given?
      end
      due
    end

    # Return a summary of all managed reports.
    def summary
      @reports.map(&:summary)
    end

    private

    def next_id
      @reports.length + 1
    end
  end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report_service](/ruby/complex/services/report_service.md) |
| calls | [find](/ruby/complex/services/report_service/find.md) |
| calls | [due?](/ruby/complex/models/report/due.md) |
| calls | [execute](/ruby/complex/services/report_service/execute.md) |
| calls | [mark_as_run!](/ruby/complex/models/report/mark_as_run.md) |
