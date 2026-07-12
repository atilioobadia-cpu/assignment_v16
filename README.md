# AIMS — Alpha Assignment Management System

<p align="center">
  <strong>End-to-end assignment lifecycle management for professional service firms</strong>
</p>

<p align="center">
  Built on <a href="https://erpnext.com/">ERPNext</a> v16 &amp; <a href="https://frappeframework.com/">Frappe</a> v16
</p>

<p align="center">
  <a href="#features">Features</a> &bull;
  <a href="#architecture">Architecture</a> &bull;
  <a href="#installation">Installation</a> &bull;
  <a href="#documentation">Documentation</a> &bull;
  <a href="#license">License</a>
</p>

---

## About

**AIMS** is a comprehensive assignment management platform built for professional service firms — accounting firms, consulting practices, and advisory organizations. It provides full visibility and control over client engagements from the moment an assignment is originated through to formal closure, with built-in SLA tracking, quality gates, risk management, and performance analytics.

Every assignment follows a structured, auditable workflow. Every task has ownership. Every delay is tracked. Every engagement closes with a certificate.

---

## Features

### Origination & Workflow
- **Structured Intake** — Capture client details, service line, risk rating, commercial terms, and evidence requirements in a single form
- **Role-Based Workflow** — Seven-state approval process with clear ownership at each transition (Draft → Submitted → Under Review → Approved → Project Created → Closed)
- **Auto-Population** — Client details, contact information, and project templates auto-fill from existing records

### Project Execution
- **Template-Driven Task Generation** — Pre-built task sequences for Tax Compliance, Audit Readiness, Bookkeeping, TRA Support, and Accounting Reconstruction, with dependency mapping
- **SLA Tracking** — Auto-created engagement SLAs with deadline calculation, breach detection, and escalation alerts
- **Time Tracking** — Custom timesheet fields for billable hours, non-billable hours, and activity categorization

### Quality & Compliance
- **Review Gates** — Mandatory quality checkpoints before task completion
- **Evidence Management** — Attachment requirements with exception handling for audit-ready documentation
- **Closure Certification** — Multi-point completion checklist that blocks premature project closure

### Risk & Delay Management
- **Client Delay Logging** — Automated delay tracking with escalation levels and management override capability
- **Risk Register** — Engagement risk assessment by type, severity, probability, and mitigation status

### Performance & HR
- **Employee Metrics** — Auto-computed utilization, billable ratio, task completion rate, and SLA compliance
- **Role-Based Goal Templates** — Automatic goal creation linked to employee roles
- **Structured Feedback** — 360-degree performance feedback with self, peer, and manager reviews

### Dashboards & Reporting
- **Operational Dashboard (AIMS Desk)** — Real-time charts, KPIs, and quick actions for day-to-day management
- **Executive Dashboard (CEO)** — High-level metrics, trend analysis, and assignment intake monitoring
- **Reports** — Staff Productivity, SLA Compliance Overview, and Employee Performance reports

---

## Architecture

```
alpha_assignment_mgmt/
├── alpha_assignment_management/       # Core DocTypes
│   ├── doctype/
│   │   ├── alpha_assignment_origination/   # Assignment intake
│   │   ├── alpha_engagement_sla/           # SLA tracking
│   │   ├── document_request_register/      # Document management
│   │   ├── review_gate_register/           # Quality gates
│   │   ├── client_delay_log/               # Delay tracking
│   │   ├── client_risk_register/           # Risk management
│   │   ├── assignment_closure_certificate/ # Closure workflow
│   │   ├── performance_feedback/           # HR feedback
│   │   └── alpha_project_template/         # Task templates
│   └── workspace/
│       ├── alpha_assignment_desk/          # Operations dashboard
│       └── ceo_assignment_dashboard/       # Executive dashboard
├── overrides/                          # Core business logic
│   ├── project.py                      # Project lifecycle hooks
│   ├── assignment_origination.py       # Origination → Project automation
│   ├── task.py                         # Task gates and SLA breach
│   ├── appraisal.py                    # Performance metrics
│   └── timesheet.py                    # Time tracking validation
├── tasks/                              # Scheduled jobs
│   ├── sla.py                          # Daily SLA breach checks
│   ├── notifications.py                # Alerts and reports
│   └── performance.py                  # Employee metric computation
├── fixtures/                           # Pre-configured data
│   ├── custom_fields.json              # 66 custom fields across 6 DocTypes
│   └── alpha_assignment_origination_workflow.json
├── setup/                              # Installation & migration
│   └── __init__.py                     # Auto-provisioning on install
├── public/js/                          # Client-side enhancements
├── report/                             # Custom reports
└── tests/                              # Integration test suite (13 tests)
```

---

## Installation

### Prerequisites

| Component | Version |
|-----------|---------|
| Frappe Framework | v16 |
| ERPNext | v16 |
| HRMS | v16 |
| Python | 3.10+ |
| MariaDB | 10.6+ |

### Install

```bash
bench get-app https://github.com/atilioobadia-cpu/assignment_v16.git
bench --site your-site install-app alpha_assignment_mgmt
bench --site your-site migrate
```

The installer automatically provisions all configuration:
- 7 custom roles
- Naming series for assignments
- Project types and activity types
- 5 project templates with 55 tasks
- Dashboard charts and number cards
- Workspace layouts

### Post-Install Checklist

1. **Enable scheduler** — `bench --site your-site enable-scheduler`
2. **Configure email** — Set up outgoing email account in Setup → Email
3. **Assign roles** — Map users to AIMS roles via Setup → Role Permission Manager
4. **Create employees** — Link Employee records to Frappe user accounts
5. **Add customers** — Create Customer records in ERPNext for client assignments

---

## Documentation

| Document | Description |
|----------|-------------|
| [Operational Guide](docs/OPERATIONAL_GUIDE.md) | Workflow procedures and role responsibilities |
| [UI Testing Guide](docs/UI_TESTING_GUIDE.md) | 17-phase validation checklist with 75+ test steps |

---

## Testing

```bash
bench --site your-site execute alpha_assignment_mgmt.tests.test_integration.run_all_tests
```

Run the full integration suite — 13 tests covering the complete assignment lifecycle from customer setup through performance feedback.

---

## Developer

**Atilio Obadia**
Email: [atilioobadia@gmail.com](mailto:atilioobadia@gmail.com)

---

## License

Proprietary — Alpha Associates (T) Limited. All rights reserved.
