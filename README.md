# AIMS — Alpha Assignment Management System

<p align="center">
  <strong>End-to-end assignment lifecycle management for professional service firms</strong>
  <br>
  Built on <a href="https://frappeframework.com/">Frappe</a> v16 &amp; <a href="https://erpnext.com/">ERPNext</a> v16
  <br><br>
  <a href="https://github.com/atilioobadia-cpu/assignment_v16/releases"><img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version"></a>
  <a href="https://frappeframework.com/"><img src="https://img.shields.io/badge/Frappe-16-green" alt="Frappe"></a>
  <a href="https://erpnext.com/"><img src="https://img.shields.io/badge/ERPNext-16-green" alt="ERPNext"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-brightgreen" alt="Python"></a>
  <a href="#license"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="License"></a>
</p>

---

## Overview

AIMS is a comprehensive **assignment management platform** purpose-built for professional service firms — accounting practices, audit firms, consulting organizations, and advisory firms. The system provides end-to-end visibility and control over client engagements, from origination through closure, with integrated SLA tracking, quality gates, risk management, and performance analytics.

Every engagement follows a structured, auditable workflow. Every task has a designated owner. Every delay is logged and escalated. Every completed engagement closes with a formal certificate and triggers performance feedback.

---

## Architecture

```
Customer → Origination → Review/Approval → Project → Tasks → Closure → Performance Feedback
    ↑                        ↑                   ↑                     ↑
  ERPNext             7-state workflow     SLA tracking         360-degree reviews
  Contacts            Review gates         Dependency gates     Utilization metrics
  Templates           Risk assessment      Evidence mgmt        Certificates
```

The system extends ERPNext with custom doctypes, workflow states, server-side scripting, and client-side automation — all within a single Frappe app.

---

## Features

### Assignment Origination & Workflow
- **Structured Intake Form** — Single-point capture of client details, service line, engagement type, risk rating, commercial terms, and evidence requirements
- **Seven-State Approval Workflow** — Draft → Submitted → Under Review → Approved → Project Created → Completed → Closed, with role-based transition ownership
- **Intelligent Auto-Population** — Client name, contact details, tax information, and focal person auto-fill from existing ERPNext Customer and Contact records
- **Template-Driven Task Generation** — Pre-configured task templates for Tax Compliance, Audit Readiness, Bookkeeping, TRA Support, and Accounting Reconstruction, each with mapped dependencies

### Project Execution & Compliance
- **Review Gates** — Mandatory quality checkpoints enforced before task completion
- **Evidence Management** — Document attachment requirements with exception handling for audit-ready engagement files
- **SLA Tracking & Escalation** — Automated SLA creation on project start, with deadline calculation, breach detection, and escalation alerts for overdue tasks
- **Time Tracking** — Custom time logs with billable/non-billable categorization and activity breakdown

### Risk & Delay Management
- **Client Delay Logging** — Automated delay capture with escalation levels (Warning → Critical → Override) and management override capability
- **Engagement Risk Register** — Risk assessment by type, severity, probability, and mitigation status, linked directly to the assignment

### Performance & Human Resources
- **Employee Performance Metrics** — Auto-computed utilization rates, billable ratios, task completion rates, and SLA compliance percentages
- **Role-Based Goal Templates** — Automatic performance goal creation tied to employee job roles
- **360-Degree Feedback** — Structured feedback collection with self-assessment, peer review, and manager review workflows

### Dashboards & Reporting
- **Operations Dashboard (AIMS Desk)** — Real-time engagement charts, key performance indicators, and quick-action shortcuts for daily management
- **Executive Dashboard (CEO)** — High-level portfolio metrics, trend analysis, and assignment intake monitoring
- **Standard Reports** — Staff Productivity, SLA Compliance Overview, and Employee Performance reports

---

## Installation

### Prerequisites

| Component | Required Version |
|-----------|-----------------|
| Frappe Framework | v16 |
| ERPNext | v16 |
| HRMS | v16 |
| Python | 3.10 or later |
| MariaDB | 10.6 or later |
| Node.js | 18+ (for assets) |

### Setup

```bash
# 1. Download the app
bench get-app https://github.com/atilioobadia-cpu/assignment_v16.git

# 2. Install on your site
bench --site your-site install-app alpha_assignment_mgmt

# 3. Apply database migrations
bench --site your-site migrate

# 4. Build assets
bench build
```

The installation process automatically provisions:

| Resource | Count |
|----------|-------|
| Custom Roles | 7 |
| Naming Series | 1 (AOR-YYYY-#####) |
| Project Templates | 5 |
| Template Tasks | 55 |
| Custom DocTypes | 10+ |
| Dashboard Charts | 6+ |
| Workspaces | 2 (Operations + Executive) |

### Post-Installation Checklist

1. **Enable the scheduler** — `bench --site your-site enable-scheduler`
2. **Configure outgoing email** — Setup an email account at *Settings → Email Account* for approval and notification dispatch
3. **Assign user roles** — Map Frabe users to AIMS roles via *Settings → Role Permission Manager*
4. **Create Employee records** — Link each Frabe user to an Employee record for performance tracking
5. **Add Customer records** — Create Client entries in ERPNext before originating assignments

---

## Documentation

| Document | Description |
|----------|-------------|
| [Operational Guide](docs/OPERATIONAL_GUIDE.md) | Step-by-step workflow procedures, role responsibilities, and operational policies |
| [UI Testing Guide](docs/UI_TESTING_GUIDE.md) | Comprehensive 17-phase validation checklist with 75+ test scenarios covering the full engagement lifecycle |

---

## Testing

```bash
bench --site your-site execute alpha_assignment_mgmt.e2e_test.run_test
```

The end-to-end integration suite validates the complete engagement lifecycle:
- Customer creation with contact and tax information sync
- Assignment origination with auto-population and workflow transitions
- Task auto-generation, assignment, and dependency enforcement
- SLA creation, breach detection, and delay escalation
- Closure certificate generation and project completion
- Performance feedback creation and notification dispatch
- Timesheet API integration
- Custom field and workspace availability

---

## Support

**Developer:** Atilio Obadia  
**Email:** [atilioobadia@gmail.com](mailto:atilioobadia@gmail.com)  

For issues, feature requests, or contributions, please open a ticket on the [GitHub repository](https://github.com/atilioobadia-cpu/assignment_v16/issues).

---

## License

Proprietary — Alpha Associates (T) Limited. All rights reserved.

This software is confidential and may not be reproduced, distributed, or transmitted without the express written permission of Alpha Associates (T) Limited.
