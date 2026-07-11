# AIMS — Alpha Assignment Management System

> Assignment lifecycle management for professional service firms. Built on [ERPNext](https://erpnext.com/) v16 and [Frappe](https://frappeframework.com/) v16.

---

## Overview

AIMS manages client engagements from intake to closure inside ERPNext — origination, SLA tracking, task execution, quality review, documentation, risk management, and formal closure. Designed for firms that need structured workflows, accountability, and audit trails across every engagement.

---

## Features

- **Assignment Origination** — Structured intake capturing client details, service line, risk rating, commercial terms, and evidence tracking
- **Workflow Automation** — Role-based state transitions with approval gates and rejection/re-submission paths
- **Project Templates** — Pre-built task sequences for common engagement types with dependency mapping and auto-generation
- **SLA Management** — Auto-created SLA tracking per project with breach detection and escalation alerts
- **Quality Review Gates** — Mandatory review checkpoints before task completion
- **Evidence & Documentation** — Attachment requirements and exception handling for audit-ready records
- **Client Delay Tracking** — Automated delay logging, escalation levels, and management override
- **Risk Register** — Engagement risk tracking by type, severity, and mitigation status
- **Closure Certification** — Formal completion checklist blocking premature project closure
- **Performance Management** — Auto-computed employee metrics, role-based goal templates, and structured feedback
- **Dashboards** — Operational and executive views with charts, KPIs, and workflow shortcuts
- **Automated Notifications** — SLA alerts, overdue task warnings, and periodic productivity reports

---

## Reports

| Report | Description |
|---|---|
| Staff Productivity | Hours logged, active/completed projects per employee |
| SLA Compliance | Status tracking with health indicators |
| Employee Performance | Computed metrics for hours, tasks, utilization, and compliance |

---

## Installation

### Prerequisites

- Frappe v16
- ERPNext v16
- HRMS v16

### Install

```bash
bench get-app git@github.com:atilioobadia-cpu/assignment_v16.git
bench --site yoursite install-app alpha_assignment_mgmt
bench --site yoursite migrate
```

The install automatically provisions all configuration — roles, project types, activity types, templates, dashboards, and reports.

### Post-Install

1. Enable the scheduler — `bench --site yoursite enable-scheduler`
2. Configure an outgoing email account in Setup → Email
3. Assign roles to users via Setup → Role Permission Manager
4. Create Employee records with linked Frappe users
5. Create Customer records in ERPNext

---

## Documentation

For detailed workflow guide and operational procedures, see [docs/OPERATIONAL_GUIDE.md](docs/OPERATIONAL_GUIDE.md).

---

## License

Proprietary — Alpha Associates (T) Limited. All rights reserved.
