# AIMS — Complete UI Testing Guide

> Follow every step in order. Each section builds on the previous one.
> Do not skip any step — if a step fails, stop and report the bug before continuing.

---

## PHASE 0: Pre-Test Setup

### 0.1 — Verify Roles Exist
1. Go to **Setup → Role Permission Manager**
2. Confirm these 9 roles appear in the role list:
   - Alpha Partner/Director
   - Alpha Engagement Manager
   - Alpha Branch Manager
   - Alpha Client Owner
   - Alpha Reviewer
   - Alpha Staff
   - Alpha HR Admin
   - Alpha Tax Officer
   - Alpha Managing Director

### 0.2 — Verify Project Types
1. Go to **Setup → Project Type**
2. Confirm 7 types exist: Tax Compliance, TRA Support, Audit Readiness, Monthly Bookkeeping, Accounting Reconstruction, Advisory, ERPNext Implementation

### 0.3 — Verify Activity Types
1. Go to **Setup → Activity Type**
2. Confirm 16 types exist

### 0.4 — Verify Project Templates
1. Go to **AIMS Desk → Alpha Project Template**
2. Confirm 5 templates exist: Tax Compliance Filing, Audit Readiness Support, Monthly Bookkeeping, Accounting Reconstruction, TRA Support
3. Open **Tax Compliance Filing** — confirm it has 10 tasks with correct sequence numbers

### 0.5 — Create Test Customer
1. Go to **Customer → New**
2. Fill in:
   - Customer Name: `Test Client Alpha Ltd`
   - Customer Group: `Commercial`
   - Customer Type: `Company`
3. **Save**

### 0.6 — Create Test Employees (create 3)
1. Go to **Employee → New**
2. Create Employee #1:
   - First Name: `John`
   - Employee Name: `John Mwangaza`
   - Gender: `Male`
   - Date of Birth: `1990-01-15`
   - Date of Joining: `2024-01-01`
   - Designation: `Alpha Tax Officer`
   - Status: `Active`
   - Branch: `Dar es Salaam` (or any existing branch)
3. **Save**
4. Repeat for Employee #2:
   - First Name: `Sarah`
   - Employee Name: `Sarah Kimaro`
   - Designation: `Alpha Engagement Manager`
5. Repeat for Employee #3:
   - First Name: `David`
   - Employee Name: `David Mwakasege`
   - Designation: `Alpha Branch Manager`

### 0.7 — Verify Users Exist
1. Go to **User List**
2. Confirm at least 3 users exist with the above employees linked
3. If not, create users and link them to the employees via the `user_id` field

---

## PHASE 1: Assignment Origination — Create & Submit

### 1.1 — Create Origination (Draft)
1. Go to **AIMS Desk → New Assignment Origination**
2. Fill in the **Assignment Identity** section:
   - Assignment Title: `Tax Filing — Test Client Alpha Ltd FY2025`
   - Date Received: `2026-07-10`
   - Received By: *(your user)*
   - Source of Request: `Client Email`
   - Service Line: `Tax Compliance`
   - Urgency Level: `High`
   - Statutory Deadline: `2026-09-30`
3. Fill in the **Client Identity** section:
   - Customer: `Test Client Alpha Ltd` ← verify it loads
   - Client Focal Person: `James Wambua`
   - Contact Number: `+255712345678`
   - Email: `james@testclient.co.tz`
   - Sector: `Manufacturing`
   - TIN Reference: `123456789`
4. Fill in **Commercial Control**:
   - Proposed Fee: `TZS 5,000,000`
   - Billing Method: `Fixed Fee`
   - Fee Approval Status: `Pending`
   - Scope Limitations: `Tax computation and filing only`
5. Fill in **Risk Control**:
   - Risk Rating: `Medium`
   - Tax Exposure: `Complex multi-source income`
6. Fill in **Team Control**:
   - Lead Branch Manager: *(select a user)*
   - Engagement Manager: *(select a user)*
   - Client Owner: *(select a user)*
   - Preparer Team: `Tax Department`
7. **Save** the document
8. ✅ **Verify:** Document is saved in Draft state, naming series generates `AOR-2026-XXXXX`

### 1.2 — Test Service Line → Template Auto-Select
1. Change the **Service Line** dropdown to `Tax Compliance`
2. ✅ **Verify:** A green alert appears: "Template auto-selected: Tax Compliance Filing (10 tasks)"
3. ✅ **Verify:** The `Project Template` field is auto-populated

### 1.3 — Test Customer Auto-Fetch
1. Change the **Customer** to a different customer (create one if needed)
2. ✅ **Verify:** The contact fields (Contact Number, Email) auto-populate if the customer has a linked Contact

### 1.4 — Test Workflow: Submit
1. Click the **Submit** button (workflow action)
2. ✅ **Verify:** Workflow state changes to `Submitted`
3. ✅ **Verify:** The document is now read-only for the Tax Officer role

### 1.5 — Test Workflow: Send to Review
1. Log in as the **Engagement Manager** user (or switch role)
2. Open the same origination
3. Click **Send to Review** (workflow action)
4. ✅ **Verify:** Workflow state changes to `Under Review`

### 1.6 — Test Workflow: Reject
1. Log in as the **Branch Manager** user
2. Open the same origination
3. Click **Reject** (workflow action)
4. ✅ **Verify:** Workflow state changes to `Rejected`

### 1.7 — Test Workflow: Re-submit
1. Log in as the **Tax Officer** user
2. Open the same origination
3. Click **Re-submit** (workflow action)
4. ✅ **Verify:** Workflow state changes back to `Submitted`

### 1.8 — Test Workflow: Send to Review Again
1. Log in as the **Engagement Manager**
2. Click **Send to Review**
3. ✅ **Verify:** State = `Under Review`

### 1.9 — Test Workflow: Approve
1. Log in as the **Branch Manager**
2. Click **Approve**
3. ✅ **Verify:** Workflow state changes to `Approved`

---

## PHASE 2: Project Creation & Template Task Generation

### 2.1 — Test Create Project Button
1. Open the origination (now in `Approved` state)
2. ✅ **Verify:** A **Create Project** button appears in the Actions menu
3. Click **Create Project**
4. Confirm the dialog
5. ✅ **Verify:** A new Project is created and linked to the origination
6. ✅ **Verify:** The origination `project_created` checkbox is checked
7. ✅ **Verify:** The origination `project_reference` field is populated

### 2.2 — Verify Project Fields Auto-Populated
1. Open the newly created Project
2. ✅ **Verify:** Customer is set to `Test Client Alpha Ltd`
3. ✅ **Verify:** `custom_service_line` = `Tax Compliance`
4. ✅ **Verify:** `custom_risk_rating` = `Medium`
5. ✅ **Verify:** `custom_engagement_manager` is set
6. ✅ **Verify:** `custom_branch_manager` is set
7. ✅ **Verify:** `expected_end_date` is set (from statutory deadline)
8. ✅ **Verify:** Project naming follows `AATL-{year}-{type}-{client}-{seq}` pattern

### 2.3 — Verify Template Tasks Generated
1. Go to the **Task** list
2. Filter by Project = the new project
3. ✅ **Verify:** 10 tasks are created (matching Tax Compliance Filing template)
4. ✅ **Verify:** Tasks have correct sequence numbers (1 through 10)
5. ✅ **Verify:** Tasks have correct `custom_depends_on_tasks` values
6. ✅ **Verify:** Tasks have correct `custom_expected_hours`
7. ✅ **Verify:** Tasks have correct `custom_task_sequence`
8. ✅ **Verify:** Tasks have correct `status` (all should be `Open` or `Pending`)

### 2.4 — Verify SLA Auto-Created
1. Go to **AIMS Desk → Engagement SLAs**
2. Filter by Project = the new project
3. ✅ **Verify:** An SLA record exists
4. Open it
5. ✅ **Verify:** `sla_level` is set (should be auto-determined)
6. ✅ **Verify:** `alpha_processing_deadline` is set
7. ✅ **Verify:** `status` = `Active`
8. ✅ **Verify:** `customer` = `Test Client Alpha Ltd`
9. ✅ **Verify:** `engagement_manager` and `branch_manager` are populated

### 2.5 — Verify Origination Status Updated
1. Go back to the origination
2. ✅ **Verify:** Workflow state is now `Project Created`
3. ✅ **Verify:** `sla_reference` is populated

---

## PHASE 3: Task Execution & Evidence

### 3.1 — Open a Task and Verify Fields
1. Go to **Task** list, filter by the project
2. Open the first task (sequence 1)
3. ✅ **Verify:** `custom_requires_review` is set (if template has it)
4. ✅ **Verify:** `custom_depends_on_tasks` shows dependency sequence numbers
5. ✅ **Verify:** `custom_expected_hours` is populated
6. ✅ **Verify:** `custom_task_sequence` shows the sequence number

### 3.2 — Test Task Dependency Enforcement
1. Open task #2 (which depends on task #1)
2. Try to set status to `Working`
3. ✅ **Verify:** If task #1 is not `Completed`, task #2 cannot progress (error or warning)

### 3.3 — Complete Task #1 Without Evidence
1. Open task #1
2. Set status to `Completed`
3. Try to save
4. ✅ **Verify:** Error message: task cannot be completed without evidence attachment or evidence exception

### 3.4 — Complete Task #1 With Evidence Exception
1. Open task #1
2. Set `custom_evidence_exception` = `Client provided verbal confirmation`
3. Set status to `Completed`
4. **Save**
5. ✅ **Verify:** Task saves successfully

### 3.5 — Complete Task #2 With Evidence Attached
1. Open task #2
2. Check `custom_evidence_attachment` = checked
3. Set status to `Completed`
4. **Save**
5. ✅ **Verify:** Task saves successfully

### 3.6 — Complete All Remaining Tasks
1. Mark all remaining tasks as `Completed` (use evidence attachment or exception)
2. ✅ **Verify:** All tasks are now `Completed`

---

## PHASE 4: Review Gate Register

### 4.1 — Create Review Gate for a Task
1. Go to **AIMS Desk → Review Queue → New**
2. Fill in:
   - Task: *(select a task with requires_review enabled)*
   - Reviewer: *(select a user)*
   - Review Date: `2026-07-11`
   - Review Comments: `Looks good, minor formatting issues`
3. ✅ **Verify:** Project field auto-populates from task
4. ✅ **Verify:** Preparer field auto-populates from task owner
5. **Save**

### 4.2 — Test Approve Review Gate
1. Click **Approve** (custom button on refresh)
2. ✅ **Verify:** `approval_status` changes to `Approved`
3. ✅ **Verify:** `review_date` is set to today

### 4.3 — Test Return for Correction
1. Create another Review Gate for a different task
2. Click **Return** (custom button)
3. Enter a return reason in the dialog
4. **Submit**
5. ✅ **Verify:** `approval_status` = `Returned`
6. ✅ **Verify:** `correction_notes` is populated

### 4.4 — Test Task Blocked by Pending Review
1. Try to complete a task that has `custom_requires_review` checked
2. Do NOT create a Review Gate for it
3. ✅ **Verify:** Task cannot be completed (error about missing review gate)

---

## PHASE 5: Document Request Register

### 5.1 — Verify Auto-Created Document Requests
1. Go to **AIMS Desk → Document Requests**
2. Filter by Project = the test project
3. ✅ **Verify:** Document Request records were auto-created (from service line)

### 5.2 — Create Manual Document Request
1. Go to **Document Request Register → New**
2. Fill in:
   - Document Name: `Test — Client Representation Letter`
   - Project: *(select the test project)*
   - Requested Date: `2026-07-10`
3. ✅ **Verify:** Assignment Origination auto-populates
4. **Save**

### 5.3 — Test Status Transitions
1. Open the document request
2. ✅ **Verify:** Default status is `Requested`
3. Change status to `Received`
4. Set Received Date = `2026-07-11`
5. **Save**
6. ✅ **Verify:** Document saves successfully

---

## PHASE 6: Client Delay Log

### 6.1 — Test Auto-Creation
1. Open a task that is not completed
2. Change its status to `Waiting for Client` (or equivalent)
3. **Save**
4. Go to **AIMS Desk → Client Delays**
5. ✅ **Verify:** A Client Delay Log was auto-created for that task
6. Open it
7. ✅ **Verify:** `project` is linked
8. ✅ **Verify:** `customer` is populated
9. ✅ **Verify:** `date_requested` is set to today
10. ✅ **Verify:** `status` = `Open`

### 6.2 — Test Escalation
1. Open the delay log
2. Click **Escalate** (custom button)
3. ✅ **Verify:** `escalation_level` increases by one level

### 6.3 — Test Mark Resolved
1. Click **Mark Resolved**
2. ✅ **Verify:** `status` = `Resolved`
3. ✅ **Verify:** `resolved_date` = today

### 6.4 — Test BM Override
1. Create a new delay log (manually or via task status change)
2. Click **BM Override - Approve Delay**
3. Confirm the dialog
4. ✅ **Verify:** `status` = `Closed`
5. ✅ **Verify:** `resolved_date` = today
6. ✅ **Verify:** Notes field has "Branch Manager override approval"
7. ✅ **Verify:** The linked task status changes (if it was blocked)

---

## PHASE 7: Risk Register

### 7.1 — Create Risk Register
1. Go to **AIMS Desk → Risk Register → New**
2. Fill in:
   - Project: *(select the test project)*
   - Customer: `Test Client Alpha Ltd`
   - Risk Type: `Tax Exposure`
   - Risk Rating: `High`
   - Root Cause: `Multiple income sources not fully disclosed`
   - Mitigation: `Request additional schedules from client`
   - Owner: *(select a user)*
3. **Save**

### 7.2 — Test Auto-Fetch from Project
1. ✅ **Verify:** Customer auto-populated from project
2. ✅ **Verify:** Assignment Origination auto-populated

### 7.3 — Test Risk Type Validation
1. Try to set Risk Type to `Financial`
2. ✅ **Verify:** Error message — valid options are: Tax Exposure, Audit Exposure, Litigation, Regulatory, Confidentiality, Scope Creep, Resource Constraint, Client Credit, Other

---

## PHASE 8: Timesheet & Billing

### 8.1 — Create Timesheet
1. Go to **Timesheet → New**
2. Select Employee: `John Mwangaza`
3. Add a row:
   - Project: *(select the test project)*
   - Activity Type: `Tax Preparation`
   - Hours: `4`
4. ✅ **Verify:** `custom_is_billable` is checked by default
5. Fill in `custom_output_note`: `Reviewed revenue schedules`
6. **Save**
7. **Submit**
8. ✅ **Verify:** Submission succeeds (project link validated)

### 8.2 — Test Timesheet Without Project
1. Create a new Timesheet
2. Add a row WITHOUT setting Project
3. Try to save
4. ✅ **Verify:** Error — every timesheet row must be linked to a Project

### 8.3 — Test Billing Fields on Project
1. Open the test project
2. Scroll to **Billing** section
3. ✅ **Verify:** `custom_billing_status` field exists
4. Set it to `Partially Billed`
5. **Save**
6. ✅ **Verify:** Billing status saved

---

## PHASE 9: Closure Certificate

### 9.1 — Create Closure Certificate
1. Go to **AIMS Desk → Closure Certificates → New**
2. Select Project: *(select the test project)*
3. ✅ **Verify:** Assignment Origination auto-populates
4. ✅ **Verify:** Customer auto-populates
5. ✅ **Verify:** Prepared By auto-populates

### 9.2 — Test Re-Check Tasks
1. Click **Re-Check Tasks** (custom button)
2. ✅ **Verify:** If all tasks are complete, `all_tasks_complete` is checked
3. ✅ **Verify:** If tasks are incomplete, a warning message appears listing them

### 9.3 — Test Closure Gate
1. Try to set Status = `Approved` with incomplete checklist items
2. **Save**
3. ✅ **Verify:** Error — cannot approve with incomplete checklist items

### 9.4 — Complete Checklist and Approve
1. Check all 6 boxes:
   - All Tasks Complete
   - All Timesheets Submitted
   - Evidence Archived
   - Client Deliverables Issued
   - Billing Complete
   - Client Sign-off Obtained
2. Set Approved By = *(select a user)*
3. Set Approval Date = `2026-07-11`
4. Set Status = `Approved`
5. **Save**
6. ✅ **Verify:** Document saves successfully

### 9.5 — Test Project Closure
1. Open the test Project
2. Set Status = `Completed`
3. **Save**
4. ✅ **Verify:** If Closure Certificate is linked, project saves successfully
5. ✅ **Verify:** Without Closure Certificate, project cannot be set to Completed

### 9.6 — Test Workflow: Close Assignment
1. Go back to the origination (state = `Project Created`)
2. Log in as **Managing Director** role
3. Click **Close Assignment**
4. ✅ **Verify:** Workflow state changes to `Closed`

---

## PHASE 10: Performance Feedback

### 10.1 — Create Feedback
1. Go to **Performance Feedback → New**
2. Fill in:
   - Employee: `John Mwangaza` (Alpha Tax Officer)
   - Project: *(select the test project)*
   - Feedback Type: `Reviewer Feedback`
   - Feedback From: `Sarah Kimaro`
   - Their Role: `Alpha Engagement Manager`
   - Rating: `Good`
   - Strengths: `Thorough tax computations`
   - Improvements: `Faster turnaround on revisions`
   - Recommendations: `Attend CPE on transfer pricing`
3. ✅ **Verify:** Employee auto-fetches `employee_name` into `feedback_from` if linked
4. **Save**

### 10.2 — Test Acknowledge
1. Click **Acknowledge** (custom button)
2. ✅ **Verify:** `status` = `Acknowledged`
3. ✅ **Verify:** `acknowledged_by` = current user
4. ✅ **Verify:** `acknowledged_date` = today

---

## PHASE 11: Dashboards

### 11.1 — AIMS Desk
1. Go to **AIMS Desk**
2. ✅ **Verify:** 4 number cards display (Active Assignments, Active Projects, Pending Reviews, Overdue SLAs)
3. ✅ **Verify:** Assignments Trend chart renders as full-width
4. ✅ **Verify:** 13 shortcuts appear in this order:
   1. New Assignment Origination
   2. All Assignments
   3. Active Projects
   4. Engagement SLAs
   5. My Tasks
   6. My Timesheets
   7. Document Requests
   8. Review Queue
   9. Client Delays
   10. Risk Register
   11. Closure Certificates
   12. SLA Compliance
   13. Staff Productivity

### 11.2 — CEO Dashboard
1. Go to **CEO Dashboard**
2. ✅ **Verify:** 4 number cards display (Total Assignments YTD, Open Risks, Active Staff, Active Clients)
3. ✅ **Verify:** Monthly Assignment Intake renders as full-width bar chart
4. ✅ **Verify:** Risk Distribution, Client Delays by Impact, Open Risks by Type render as 3 equal-width charts
5. ✅ **Verify:** 2 shortcuts: Staff Productivity, Employee Performance

---

## PHASE 12: Reports

### 12.1 — Staff Productivity Report
1. Go to **AIMS Desk → Staff Productivity**
2. ✅ **Verify:** Report renders with Employee ID, Name, Designation, Branch, Hours Logged, Active Projects, Completed Projects

### 12.2 — SLA Compliance Report
1. Go to **AIMS Desk → SLA Compliance**
2. ✅ **Verify:** Report shows all submitted SLAs with status, deadline, and health indicator

### 12.3 — Employee Performance Report
1. Go to **Reports → Employee Performance**
2. ✅ **Verify:** Report shows computed metrics (hours, tasks, utilization, SLA rate)

---

## PHASE 13: Project Navigation (JS)

### 13.1 — Origination Navigation
1. Open the origination
2. ✅ **Verify:** "Open Project" button appears (if project is linked)
3. Click it
4. ✅ **Verify:** Navigates to the correct Project form

### 13.2 — Project Navigation
1. Open the test Project
2. ✅ **Verify:** "Open Origination" button appears
3. ✅ **Verify:** "Open SLA" button appears
4. ✅ **Verify:** "Open Closure Certificate" button appears (if linked)
5. Click each — verify correct navigation

### 13.3 — Task Navigation
1. Open a task
2. ✅ **Verify:** "Open Project" button appears
3. ✅ **Verify:** "Open Review Gate" button appears (if linked)
4. ✅ **Verify:** "Open Delay Log" button appears (if linked)

---

## PHASE 14: Edge Cases & Error Handling

### 14.1 — Duplicate Origination Title
1. Create an origination with the same title as before
2. ✅ **Verify:** System allows it (titles are not unique by design, naming_series is)

### 14.2 — Submit with Missing Required Fields
1. Create a new origination
2. Leave `Assignment Title` blank
3. Try to save
4. ✅ **Verify:** Error — field is required

### 14.3 — Create Project from Non-Approved Origination
1. Create an origination in Draft state
2. Try to run `create_project_from_origination` API
3. ✅ **Verify:** Error — only Approved originations can create Projects

### 14.4 — SLA Breach Test
1. Open the test SLA
2. Set `alpha_processing_deadline` to yesterday's date
3. **Save**
4. ✅ **Verify:** Status changes to `Breached` (from the validate hook)

### 14.5 — Task Completion Without Review Gate
1. Find a task with `custom_requires_review` = checked
2. Ensure NO Review Gate Register is linked
3. Try to set status = `Completed`
4. ✅ **Verify:** Error — review gate required

### 14.6 — Closure Certificate with Incomplete Tasks
1. Create a new Closure Certificate for a project with incomplete tasks
2. Click **Re-Check Tasks**
3. ✅ **Verify:** Warning message lists incomplete tasks
4. ✅ **Verify:** `all_tasks_complete` = unchecked

---

## PHASE 15: Permissions

### 15.1 — Staff View Restriction
1. Log in as a **Staff** user
2. Go to **Task** list
3. ✅ **Verify:** Only tasks assigned to or owned by the user are visible

### 15.2 — Engagement Manager View
1. Log in as **Engagement Manager**
2. Go to **Task** list
3. ✅ **Verify:** All tasks for their projects are visible

### 15.3 — Branch Manager View
1. Log in as **Branch Manager**
2. Go to **Task** list
3. ✅ **Verify:** All tasks for their branch's projects are visible

### 15.4 — Role Restriction on Origination
1. Log in as **Alpha Staff**
2. Try to edit a Submitted origination
3. ✅ **Verify:** Cannot edit (read-only)

---

## PHASE 16: Scheduler (Manual Trigger)

### 16.1 — Test SLA Breach Check
1. Run: `bench --site aims.local execute alpha_assignment_mgmt.tasks.sla.daily_sla_breach_check`
2. ✅ **Verify:** No errors
3. ✅ **Verify:** If an SLA has passed its deadline, status is set to `Breached`

### 16.2 — Test Overdue Task Notification
1. Run: `bench --site aims.local execute alpha_assignment_mgmt.tasks.notifications.daily_overdue_task_notification`
2. ✅ **Verify:** No errors
3. ✅ **Verify:** If overdue tasks exist, emails are queued in Email Queue

### 16.3 — Test Performance Computation
1. Run: `bench --site aims.local execute alpha_assignment_mgmt.tasks.performance.daily_performance_computation`
2. ✅ **Verify:** Employee custom fields are populated with computed metrics

---

## PHASE 17: Cleanup

1. Delete all test records created during this test:
   - Closure Certificates
   - Risk Registers
   - Delay Logs
   - Document Requests
   - Review Gates
   - Timesheets
   - Performance Feedback
   - Tasks
   - Projects
   - SLAs
   - Origination
   - Customers (test ones)
2. ✅ **Verify:** No orphan records remain

---

## Bug Report Template

For any failure found, record:

```
Phase: [number]
Step: [number]
Expected: [what should happen]
Actual: [what happened]
Screenshot: [if applicable]
```

---

## Sign-Off Checklist

- [ ] Phase 0: Setup — All 15 checks pass
- [ ] Phase 1: Origination — 9 steps pass
- [ ] Phase 2: Project Creation — 5 checks pass
- [ ] Phase 3: Task Execution — 6 steps pass
- [ ] Phase 4: Review Gate — 4 steps pass
- [ ] Phase 5: Document Request — 3 steps pass
- [ ] Phase 6: Client Delay — 4 steps pass
- [ ] Phase 7: Risk Register — 3 steps pass
- [ ] Phase 8: Timesheet & Billing — 3 steps pass
- [ ] Phase 9: Closure Certificate — 6 steps pass
- [ ] Phase 10: Performance Feedback — 2 steps pass
- [ ] Phase 11: Dashboards — 2 checks pass
- [ ] Phase 12: Reports — 3 checks pass
- [ ] Phase 13: Navigation — 3 checks pass
- [ ] Phase 14: Edge Cases — 6 checks pass
- [ ] Phase 15: Permissions — 4 checks pass
- [ ] Phase 16: Scheduler — 3 checks pass
- [ ] Phase 17: Cleanup — verified clean
