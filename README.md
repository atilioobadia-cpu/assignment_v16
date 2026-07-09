# Alpha Assignment Management

Professional service assignment management for Alpha Associates (T) Limited.
Built on ERPNext Projects, Tasks, Timesheets and Frappe HR.
Alpha Assignment Management — Operational Guide
1. Overview
The Alpha Assignment Management Framework is a Frappe/ERPNext app that digitises the full client-assignment lifecycle for Alpha Associates (T) Limited:
Stage	What happens
Origination	Partner raises a new assignment, defines scope, risk, team
Approval	Branch Manager reviews, approves or rejects
Project Creation	System auto-creates a Project + Engagement SLA from an approved origination
Execution	Staff work through template-driven tasks with evidence gates
Review	High-risk tasks require Review Gate sign-off before completion
Closure	Assignment Closure Certificate issued, project closed
---
2. Installation
Prerequisites
ERPNext v16 site running on Frappe Bench
`hrms` app installed on the same site
Install the App
```bash
bench get-app https://github.com/atilioobadia-cpu/Alpha_Assignment_Management.git
bench --site yoursite install-app alpha_assignment_mgmt
bench --site yoursite migrate
```
Post-Install Setup
```bash
bench --site yoursite console
```
```python
exec(open(frappe.get_app_path('alpha_assignment_mgmt', 'setup', '__init__.py')).read())
after_install()
exit()
```
This creates:
8 Roles: Alpha Partner/Director, Alpha Engagement Manager, Alpha Branch Manager, Alpha Client Owner, Alpha Reviewer, Alpha Staff, Alpha HR Admin
7 Project Types: Tax Compliance, TRA Support, Audit Readiness, Monthly Bookkeeping, Accounting Reconstruction, Advisory, ERPNext Implementation
16 Activity Types: Tax Preparation, Audit Fieldwork, Bookkeeping Entry, etc.
Naming Series for all custom DocTypes
Load Project Templates
```bash
bench --site yoursite console
```
```python
exec(open(frappe.get_app_path('alpha_assignment_mgmt', 'scripts', 'run_setup.py')).read())
exit()
```
---
3. Roles & Permissions
Role	Typical User	Access
Alpha Partner/Director	Firm partners	Full access to all DocTypes (create, read, write, submit, delete, amend)
Alpha Engagement Manager	Assignment leads	Create & edit assignments, projects, SLAs; submit for review
Alpha Branch Manager	Branch heads	Read access; can initiate assignments for their branch
Alpha Client Owner	Client relationship owner	Read assignments; can log document requests
Alpha Reviewer	Quality/review staff	Read only; can create & approve Review Gates
Alpha Staff	Junior staff	Create & edit tasks, document requests, delay logs; read projects
Alpha HR Admin	HR personnel	Read-only access for performance reporting
System Manager	IT admin	Everything (Frappe default)
> **Setup**: Go to **Setting > Role Permission Manager** in ERPNext to assign users to roles.
---
4. The Full Workflow (Step by Step)
Step 1: Create an Assignment Origination
Desk > Alpha Assignment Desk > New Assignment Origination
Fill in:
Assignment Title — e.g. "Annual Tax Compliance — ABC Ltd FY2025"
Customer — select from existing
Service Line — Tax Compliance, Audit Readiness, etc.
Date Received — when the engagement was requested
Risk Rating — Low / Medium / High / Critical
Lead Branch Manager — the Partner overseeing this
Engagement Manager — the Manager running the assignment
Client Owner — relationship contact
Proposed Fee, Billing Method, Scope Notes
Save status is Draft
Step 2: Submit for Review
Click Menu > Submit (workflow action)
Status changes to Submitted
Step 3: Review & Approve
Branch Manager or Partner opens the Origination
Click Send to Review status becomes Under Review
Review the scope, risk, and fee
Click Approve status becomes Approved
Alternatively click Reject to send back for revision
Step 4: Create the Project
Go to Projects > Project > New
Set Project Name and Project Type
In the Alpha Assignment section, link to the Approved Origination
Save the system:
Validates the Origination is Approved
Auto-fills Service Line, Branch Manager, Engagement Manager, Client Owner, Risk Rating
Creates a linked Alpha Engagement SLA
Updates the Origination to Project Created
Step 5: Apply a Project Template
Open the Project
Set Project Template to the relevant service-line template (e.g. "Tax Compliance Template")
Save the template tasks are created automatically
Step 6: Execute Tasks
Staff work through tasks. Rules enforced by the system:
Evidence Gate: A task cannot be marked Completed unless `Evidence Attached` is checked or an `Evidence Exception` note is provided
Review Gate: If Requires Review is checked on a task, a Review Gate Register must be approved before completion
Client Delay: Changing a task to Waiting for Client auto-creates a Client Delay Log
How to Complete a Task:
Open the Task
Check Evidence Attached (or write an Exception note)
If high-risk: ensure a Review Gate is approved first
Set Status to Completed Save
Step 7: Create a Review Gate (for high-risk tasks)
Go to Alpha Assignment Desk > Review Gate Register > New
Link to the Task and assign a Reviewer
Save > Submit
Reviewer opens the gate, sets Approval Status to Approved, adds comments
Click Save (uses `db_set` internally to bypass submit restrictions)
Now the task can be completed
Step 8: Monitor SLAs
Each project gets an Alpha Engagement SLA at creation
The SLA Level is auto-assigned based on Project Type:
Tax Compliance / TRA Support SLA A - Urgent Statutory
Audit Readiness SLA B - Audit Readiness
Monthly Bookkeeping SLA C - Monthly Bookkeeping
Accounting Reconstruction SLA D - Reconstruction
Advisory / ERPNext Implementation SLA E - Advisory/Research/Training
SLA status is Active by default; the daily scheduler marks breached SLAs and sends email warnings
Step 9: Close the Assignment
Ensure all tasks are completed
Create an Assignment Closure Certificate:
Link to the Project and Origination
Confirm client acceptance
Save > Submit
Open the Project, set Status = Completed
The Origination is now eligible for Close Assignment workflow action
---
5. Reports
Staff Productivity
Desk > Alpha Assignment Desk > Staff Productivity
Shows per-employee: tasks completed, tasks overdue, hours logged, active/completed projects. Filterable by Branch and Designation.
SLA Compliance Overview
Desk > Alpha Assignment Desk > SLA Compliance Overview
Shows all submitted SLAs with their status, deadline, and health (On Track / Overdue / Breached). Filterable by SLA Level and Status.
---
6. HR Performance Integration
Goal Setting
When creating a Goal (HR > Goals), you can now link it to:
Related Project the assignment this goal belongs to
Related Task specific deliverable
Assignment Origination parent origination
Metric Type Task Completion / SLA Compliance / Utilization Rate / Revenue Target / Quality Score
Target Value the KPI target
Actual Value auto-populated (read-only)
Appraisal Metrics
When creating an Appraisal (HR > Performance > Appraisal), the system auto-calculates:
Assignments Completed projects closed by this employee as Engagement Manager
SLA Compliance Rate % of SLAs without breach
Utilization Rate billable hours / available working hours
These fields are read-only and recalculated each time the Appraisal is saved.
---
7. Scheduler Events
Event	Frequency	What it does
`daily_sla_breach_check`	Daily	Checks all Active SLAs; marks breached ones; sends email warnings 24h before
`daily_overdue_task_notification`	Daily	Emails Engagement Manager and assigned users about overdue tasks
`weekly_productivity_report`	Weekly (Mon)	Emails each Engagement Manager a table of their projects, hours logged, and tasks completed
---
8. System Overrides Summary
Hook	DocType	Method	Purpose
`before_insert`	Project	`overrides.project.before_insert`	Gated: only Approved originations can create Projects
`on_update`	Project	`overrides.project.on_update`	Auto-creates SLA on new projects; updates origination status; prevents closure without certificate
`validate`	Task	`overrides.task.validate`	Enforces evidence attachment, review gate approval, client delay logging
`on_update`	Task	`overrides.task.on_update`	Sends overdue notification
`validate`	Timesheet	`overrides.timesheet.validate`	Ensures each timesheet row links to a Project
`validate`	Appraisal	`overrides.appraisal.validate`	Auto-calculates assignments completed, SLA rate, utilization rate
---
9. Troubleshooting
Symptom	Cause	Fix
"Cannot create Project Assignment Origination not approved"	Origination workflow state is not Approved	Go to Origination, complete the Approval workflow
"Evidence attachment required"	Task marked Complete but no evidence	Check Evidence Attached or add an Exception note
"Review Gate approval required"	Task requires review but gate not approved	Create & approve a Review Gate Register for this task
SLA not created	Project saved without Project Type	Set Project Type on the Project; SLA is created on next save
"Cannot close Project Closure Certificate required"	Project status set to Completed but no certificate	Create & submit an Assignment Closure Certificate first
Permission errors on DocTypes	User lacks role assignment	Go to Role Permission Manager or assign the correct role to the user
---
10. Quick Reference: Custom DocTypes
DocType	Key Fields	Submittable	Naming Series
Alpha Assignment Origination	Customer, Service Line, Risk Rating, Lead Branch Manager, Engagement Manager, Proposed Fee	Yes	AOR-.YYYY.-.#####
Alpha Engagement SLA	Project, SLA Level, Alpha Processing Deadline, Engagement Manager, Status	Yes	AATL-SLA-.YYYY.-
Document Request Register	Document Name, Task, Status, Owner, Responsible Person	No	DRR-.YYYY.-
Review Gate Register	Task, Reviewer, Approval Status, Review Comments	Yes	RGR-.YYYY.-
Client Delay Log	Task, Delay Reason, Impact Analysis, Status	No	CDL-.YYYY.-
Client Risk Register	Project, Risk Description, Risk Category, Mitigation Plan	No	CRR-.YYYY.-
Assignment Closure Certificate	Project, Origination, Final Outstanding Fees, Client Confirmation	Yes	ACC-.YYYY.-
