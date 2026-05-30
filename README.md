# AlertManager Report Manager

AlertManager Report Manager is a lightweight reporting and analytics platform for Prometheus Alertmanager.

It collects alert events through Alertmanager webhooks, stores them in a historical database, and generates actionable reports that help teams identify noisy alerts, recurring issues, and monitoring gaps.

## Why?

Alertmanager excels at routing and delivering notifications, but it is not designed to provide long-term historical analysis of alert activity.

As infrastructures grow, teams often face challenges such as:

* Alert fatigue caused by repetitive notifications
* Alerts that never become incidents but occur frequently
* Difficulties identifying noisy or poorly tuned alert rules
* Lack of visibility into alert trends over time
* Limited data for improving monitoring quality

AlertManager Report Manager addresses these challenges by transforming alert events into meaningful operational insights.

## Features

### Alert History

Persist all Alertmanager events in a relational database, including:

* Firing and resolved states
* Labels and annotations
* Alert metadata
* Original webhook payloads
* Grouping information

### Historical Reporting

Generate HTML and PDF reports containing:

* Executive summaries
* Alert activity metrics
* Most frequent alerts
* Trend analysis
* Service and team breakdowns
* Alert growth and recurrence analysis

### Repetitive Alert Detection

Identify alerts that may not be critical individually but become important due to their frequency.

Examples include:

* Repeated warning-level alerts
* Alerts affecting multiple hosts or services
* Rapidly growing alert patterns
* Flapping alerts

### Alert Quality Analysis

Help teams improve monitoring quality by highlighting:

* Noisy alert rules
* Candidates for threshold tuning
* Candidates for alert suppression
* Candidates for automatic ticket creation

### Custom Label Awareness

Leverage custom labels to enrich reporting and classification.

Examples:

```yaml
team: platform
service: payments
category: capacity
criticality: tier1
ticket_policy: repetitive
```

This enables reports grouped by ownership, business criticality, service domain, or operational category.

## Use Cases

* Alert fatigue reduction
* Monitoring quality reviews
* SRE and platform engineering reporting
* Recurring issue detection
* Alert rule optimization
* Capacity and reliability analysis
* Automated ticket candidate identification

## Philosophy

Not every alert deserves a ticket.

Many alerts are too minor to require immediate action, yet become significant when they occur repeatedly over time.

AlertManager Report Manager helps teams identify these patterns and convert operational noise into actionable information.

> A single alert may be noise. The same alert occurring 100 times in a week is a problem worth investigating.
