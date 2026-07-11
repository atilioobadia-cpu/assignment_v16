# AIMS — Alpha Assignment Management System

> Professional service assignment management for **Alpha Associates (T) Limited**, built on [ERPNext](https://erpnext.com/) v16, [Frappe](https://frappeframework.com/) v16, and [HRMS](https://frappehrms.com/) v16.

AIMS manages the full lifecycle of client engagements — from origination and SLA tracking through task execution, quality review, and formal closure — inside a single ERPNext installation.

---

## Key Features

| Capability | Description |
|---|---|
| **Assignment Origination** | Structured intake with client details, service line, risk rating, commercial terms, and evidence tracking |
| **Workflow Automation** | 7-state workflow (Draft → Submitted → Under Review → Approved → Project Created → Closed) with role-based transitions |
| **Project Templates** | 5 pre-seeded templates (Tax Compliance, Audit Readiness, Bookkeeping, Accounting Reconstruction, TRA Support) with 55 auto-generated tasks |
| **SLA Tracking** | Auto-created SLA per project with breach detection, warning emails, and escalation |
| **Review Gates** | Quality control checkpoints — tasks require approved review before completion |
| **Evidence & Documentation** | Tasks require evidence attachment or approved exception before marking complete |
| **Client Delay Logging** | Auto-creates delay logs when tasks are blocked by client; escalation levels 1–4; Branch Manager override |
| **Risk Register** | Track engagement risks by type, rating, mitigation, and status |
| **Closure Certificate** | Formal closure checklist — blocks project completion until all items verified |
| **Performance & HR** | Auto-computed employee metrics, appraisal goal creation from role-based templates, feedback system |
| **Dashboards** | AIMS Desk (operational) and CEO Dashboard (executive) with charts, number cards, and workflow shortcuts |
| **Automated Reports** | Staff Productivity, SLA Compliance Overview, Employee Performance |
| **Email Notifications** | SLA breach/warning alerts, overdue task notifications, weekly productivity reports |

---

## Architecture

```
alpha_assignment_mgmt/
├── alpha_assignment_management/
│   ├── doctype/                    # 11 Custom DocTypes
│   │   ├── alpha_assignment_origination/
│   │   ├── alpha_engagement_sla/
│   │   ├── alpha_project_template/
│   │   ├── alpha_task_template/    # Child table
│   │   ├── document_request_register/
│   │   ├── review_gate_register/
│   │   ├── client_delay_log/
│   │   ├── client_risk_register/
│   │   ├── assignment_closure_certificate/
│   │   ├── performance_feedback/
│   │   └── alpha_evidence_attachment/  # Child table
│   ├── report/                     # 3 Query Reports
│   ├── workspace/                  # 2 Dashboards (AIMS Desk, CEO)
│   └── alpha_assignment_management/module.txt
├── overrides/
│   ├── project.py                  # SLA auto-creation, closure gate
│   ├── task.py                     # Evidence, review, delay, dependency gates
│   ├── assignment_origination.py   # Project + task auto-generation on approval
│   ├── timesheet.py                # Project link enforcement
│   └── appraisal.py                # HR Goals auto-creation from role templates
├── fixtures/
│   ├── custom_fields.json          # 67 custom fields across 6 core DocTypes
│   └── alpha_assignment_origination_workflow.json
├── public/js/
│   ├── project.js                  # Origination auto-fill, navigation
│   └── task.js                     # Navigation to linked records
├── setup/
│   └── __init__.py                 # after_install, after_migrate
├── tasks/
│   ├── sla.py                      # Daily SLA breach check + email
│   ├── notifications.py            # Overdue alerts, weekly productivity
│   └── performance.py              # Daily employee metrics
└── hooks.py
```

---

## Custom DocTypes

### Primary Workflow

| DocType | Purpose |
|---|---|
| **Alpha Assignment Origination** | Central intake document — captures assignment identity, client info, commercial terms, risk, team, evidence |
| **Alpha Engagement SLA** | SLA commitments per project — level (A–E), deadlines, breach status |
| **Document Request Register** | Tracks client-provided documents — request, follow-up, receipt, rejection |
| **Review Gate Register** | Quality checkpoint — preparer/reviewer workflow with approval/return |
| **Client Delay Log** | Client-caused delays — escalation levels, impact, Branch Manager override |
| **Client Risk Register** | Engagement risks — type, rating, root cause, mitigation, status |
| **Assignment Closure Certificate** | Formal closure — 6-item checklist, approval chain |

### Templates & Support

| DocType | Purpose |
|---|---|
| **Alpha Project Template** | Reusable project definitions with task breakdowns |
| **Alpha Task Template** | Child table — task subject, hours, sequence, dependencies, owner role |
| **Performance Feedback** | Structured employee feedback — type, rating, strengths, improvements |
| **Alpha Evidence Attachment** | Child table — file, description, date, notes |

---

## Custom Fields on Core DocTypes

| DocType | Fields | Key Additions |
|---|---|---|
| **Project** | 21 | Origination link, SLA link, team (BM/EM/Client Owner), risk rating, service line, billing (SO/SI/status), closure certificate |
| **Task** | 15 | Review required, evidence attached/exception, review gate, delay log, dependencies, expected hours, sequence |
| **Goal** | 11 | Related project/task, origination link, metric type, target vs actual |
| **Appraisal** | 5 | Assignments completed, SLA compliance rate, utilization rate (all auto-computed) |
| **Employee** | 9 | Hours logged (30d), tasks completed (30d), active assignments, SLA compliance, utilization |
| **Timesheet Detail** | 5 | Billable flag, output note, evidence reference, client delay flag |

---

## Workflow

```
Draft ──── Submitted ──── Under Review ──── Approved ──── Project Created ──── Closed
  │                          │      │                            │
  │                      Approve  Reject                    Close Assignment
  │                          │      │
  │                          │   Re-submit ──→ Submitted
  │                          │
  └──────────────────────────┘
```

| Transition | Role Required |
|---|---|
| Submit | Alpha Tax Officer |
| Send to Review | Alpha Engagement Manager |
| Approve / Reject | Alpha Branch Manager |
| Create Project | Alpha Engagement Manager |
| Close Assignment | Alpha Managing Director |

---

## Automation

### On Origination Approval
- **Project created** with naming convention `AATL-{year}-{type}-{client}-{seq}`
- **Tasks auto-generated** from matched Alpha Project Template
- **SLA auto-created** and submitted
- **Document Requests auto-created** based on service line

### On Task Update
- **Evidence gate** — blocks completion without evidence or approved exception
- **Review gate** — blocks completion if review is pending
- **Delay auto-logging** — creates Client Delay Log on "Waiting for Client"
- **Dependency enforcement** — prevents starting tasks with incomplete dependencies
- **Overdue notification** — emails Engagement Manager + assigned users
- **SLA auto-breach** — marks SLA as Breached when tasks go overdue

### On Project Update
- **Closure gate** — blocks status change to "Completed" without Closure Certificate

### On Appraisal Submit
- **HR Goals auto-created** from role-based templates (5 roles × 6 goals = 30 weighted goals)

### Scheduled Jobs
| Schedule | Job | Action |
|---|---|---|
| Daily | `daily_sla_breach_check` | Breach expired SLAs, warn approaching deadlines |
| Daily | `daily_overdue_task_notification` | Email overdue task alerts |
| Daily | `daily_performance_computation` | Compute employee metrics (hours, tasks, utilization) |
| Weekly (Mon) | `weekly_productivity_report` | Email per-Engagement Manager productivity summary |

---

## Roles

| Role | Access Level |
|---|---|
| Alpha Managing Director | Full access, workflow approvals, closure |
| Alpha Partner/Director | Full access, strategic oversight |
| Alpha Branch Manager | Branch-level oversight, review approvals, delay override |
| Alpha Engagement Manager | Project management, review initiation, task assignment |
| Alpha Tax Officer | Tax-specific origination, submission, filing |
| Alpha Reviewer | Quality review, task assessment |
| Alpha Staff | Task execution, document handling |
| Alpha Client Owner | Client relationship, project visibility |
| Alpha HR Admin | Performance feedback, HR metrics |

---

## Dashboards

### AIMS Desk (All Staff)
Number cards for Active Assignments, Active Projects, Pending Reviews, Overdue SLAs. Full-width Assignments Trend chart. 13 workflow-ordered shortcuts following the operational flow: Origination → Projects → SLAs → Tasks → Timesheets → Documents → Reviews → Delays → Risks → Closure → Reporting.

### CEO Dashboard (Directors)
Executive overview with Monthly Assignment Intake (full-width bar chart), Risk Distribution (pie), Client Delays by Impact (bar), Open Risks by Type (bar). Number cards for Total Assignments YTD, Open Risks, Active Staff, Active Clients.

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

`install-app` automatically creates all roles, naming series, project types, activity types, project templates, dashboard charts, number cards, and workspace layouts.

### Post-Install Setup

1. **Enable the scheduler** — `bench --site yoursite enable-scheduler`
2. **Configure an outgoing email account** — Setup → Email → Email Account
3. **Assign roles to users** — Setup → Role Permission Manager
4. **Create Employee records** with `user_id` linked to Frappe users and proper designations
5. **Create Customer records** in ERPNext

---

## Reports

| Report | Description |
|---|---|
| Staff Productivity | Hours logged, active/completed projects per employee |
| SLA Compliance Overview | SLA status, deadline, health (On Track / Overdue / Breached) |
| Employee Performance | Computed metrics — hours, tasks, utilization, SLA rate |

---

## Email Notifications

| Trigger | Recipients | Content |
|---|---|---|
| SLA Breach | Engagement Manager + Branch Manager | SLA details, deadline, breach alert |
| SLA Breach Warning (24h) | Engagement Manager + Branch Manager | SLA details, time remaining |
| Overdue Task | Engagement Manager + Assigned Users | Task, project, client, due date |
| Weekly Productivity | Each Engagement Manager | Per-project hours, tasks completed, totals |

---

## License

Proprietary — Alpha Associates (T) Limited. All rights reserved.
