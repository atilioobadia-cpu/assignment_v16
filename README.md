# Alpha Assignment Management

Professional service assignment management for Alpha Associates (T) Limited.
Built on ERPNext Projects, Tasks, Timesheets and Frappe HR.

## Installation

```bash
bench get-app https://github.com/atilioobadia-cpu/Alpha_Assignment_Management.git
bench --site yoursite install-app alpha_assignment_mgmt
bench --site yoursite migrate
```

`install-app` runs `after_install` automatically, which creates all roles, naming series, project types, and activity types.

## What Gets Installed

### 9 Roles
Alpha Partner/Director, Alpha Engagement Manager, Alpha Branch Manager, Alpha Client Owner, Alpha Reviewer, Alpha Staff, Alpha HR Admin, Alpha Tax Officer, Alpha Managing Director

### 7 Custom DocTypes
| DocType | Submittable | Naming |
|---------|-------------|--------|
| Alpha Assignment Origination | Yes | AOR-.YYYY.-.##### |
| Alpha Engagement SLA | Yes | AATL-SLA-.YYYY.-.##### |
| Document Request Register | No | hash |
| Review Gate Register | Yes | hash |
| Client Delay Log | No | hash |
| Client Risk Register | No | hash |
| Assignment Closure Certificate | Yes | hash |

### 7 Project Types
Tax Compliance, TRA Support, Audit Readiness, Monthly Bookkeeping, Accounting Reconstruction, Advisory, ERPNext Implementation

### 16 Activity Types
Tax Preparation, Tax Review, Tax Filing, Audit Fieldwork, Audit Review, Bookkeeping Entry, Bookkeeping Review, Reconciliation, Advisory Call, Advisory Report, ERPNext Setup, ERPNext Training, Client Communication, Internal Meeting, Training/CPD, Administrative

### Custom Fields on Core DocTypes
- **Project** (8 fields): Assignment Origination, Engagement SLA, Branch Manager, Engagement Manager, Client Owner, Risk Rating, Service Line, Closure Certificate
- **Task** (5 fields): Requires Review, Evidence Attached, Evidence Exception, Review Gate, Client Delay Log
- **Goal** (6 fields): Related Project, Related Task, Assignment Origination, Metric Type, Target Value, Actual Value
- **Appraisal** (3 fields): Assignments Completed, SLA Compliance Rate, Utilization Rate

### Workflow
Alpha Assignment Origination: Draft → Submitted → Under Review → Approved/Rejected → Project Created → Closed

### Server Overrides
| DocType | Hook | Purpose |
|---------|------|---------|
| Project | before_insert | Gated: only Approved originations can create Projects |
| Project | on_update | Auto-creates SLA; updates origination status; closure gating |
| Task | validate | Evidence attachment, review gate, client delay logging |
| Task | on_update | Overdue notification |
| Timesheet | validate | Project link required on each row |
| Appraisal | validate | Auto-calculates assignments, SLA rate, utilization |

### Scheduler Events
- **Daily**: SLA breach check + overdue task notification
- **Weekly (Mon)**: Productivity report emailed to Engagement Managers

### Custom Reports
- **Staff Productivity**: Hours logged, active/completed projects per employee
- **SLA Compliance Overview**: SLA status, deadline, health (On Track/Overdue/Breached)

## Quick Start

1. Assign roles to users (System Manager → Role Permission Manager)
2. Create an **Alpha Assignment Origination** (Draft)
3. Submit → workflow progresses through Under Review → Approved
4. Create a **Project** linked to the approved Origination (Project Type required)
5. SLA is auto-created on save
6. Staff work tasks with evidence and review gates
7. Close: Create **Assignment Closure Certificate** → set Project = Completed

For detailed step-by-step workflow, see `docs/OPERATIONAL_GUIDE.md`.
