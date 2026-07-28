# AIMS End-to-End UI Test Checklist

Login as **Administrator** on `aims.local`. Tick off each step as you go.

---

## 1. Create a Customer (Central Hub)

| # | Action | Expected Result | ✓ |
|---|--------|-----------------|---|
| 1.1 | Open **Customer** list → **+ Add Customer** | New Customer form opens | |
| 1.2 | Enter `Customer Name` = `E2E Test Corp [Your Initials]` | Name appears | |
| 1.3 | Set `Customer Group` = `Commercial` | | |
| 1.4 | Set `Customer Type` = `Company` | | |
| 1.5 | Set `Territory` = `All Territories` | | |
| 1.6 | Fill custom fields section: | — | |
| | `Engagement Manager` = `Administrator` | | |
| | `Client Owner` = `Administrator` | | |
| | `Branch Manager` = `Administrator` | | |
| | `Service Line` = `Tax Compliance` | | |
| | `Risk Rating` = `Medium` | | |
| | `Sector` = `Financial Services` | | |
| | `TIN` = `TIN-UI-99999` | | |
| 1.7 | **Save** | Saved, no errors | |

---

## 2. Create Origination (autofill from Customer)

| # | Action | Expected Result | ✓ |
|---|--------|-----------------|---|
| 2.1 | Open **Alpha Assignment Origination** → **+ Add** | New form opens | |
| 2.2 | Set `Customer` = your customer from step 1 | | |
| 2.3 | Enter `Assignment Title` = `UI Test Tax Filing` | | |
| 2.4 | Set `Service Line` = `Tax Compliance` | | |
| 2.5 | Set `Date Received` = today | | |
| 2.6 | Set `Regulatory Deadline` = 30 days from today | | |
| 2.7 | Set `Received By` = `Administrator` | | |
| 2.8 | **Save** | ✅ Fields auto-filled from Customer: | |
| | | — `Engagement Manager` = Administrator | ☐ |
| | | — `Client Owner` = Administrator | ☐ |
| | | — `Branch Manager` = Administrator | ☐ |
| | | — `Service Line` = Tax Compliance | ☐ |
| | | — `Risk Rating` = Medium | ☐ |
| | | — `Sector` = Financial Services | ☐ |
| | | — `TIN` = TIN-UI-99999 | ☐ |

---

## 3. Submit through Workflow → Project auto-creation

| # | Action | Expected Result | ✓ |
|---|--------|-----------------|---|
| 3.1 | With Origination open, click **Menu > Workflow > Submit** | Status changes to **Submitted** | |
| 3.2 | Click **Menu > Workflow > Send to Review** | Status changes to **Under Review** | |
| 3.3 | Click **Menu > Workflow > Approve** | Status changes to **Approved** | |
| 3.4 | Click **Menu > Workflow > Create Project** | Status changes to **Project Created** | |

Wait a moment, then verify:

| # | Action | Expected Result | ✓ |
|---|--------|-----------------|---|
| 3.5 | Open **Project** list | A new project **PROJ-xxxx** exists | |
| 3.6 | Open the project | Verify: | |
| | | — `Status` = Open | ☐ |
| | | — `Customer` = your customer | ☐ |
| | | — `Assignment Origination` = linked to your Origination | ☐ |

---

## 4. Verify Project contents

| # | Action | Expected Result | ✓ |
|---|--------|-----------------|---|
| 4.1 | In the Project, scroll to **Tasks** table | **10 tasks** listed with sequence numbers | |
| 4.2 | Check a few tasks have `Assign To` populated (e.g. seq 2-9) | Some show user emails | |
| 4.3 | Check a few tasks have `Depends On Tasks` populated | Dependency chains visible | |
| 4.4 | Scroll to **Document Requests** table | Several doc requests listed with responsible persons | |
| 4.5 | Open **Alpha Engagement SLA** list | An SLA record exists for this project with status = `Active` | |

---

## 5. Test Dependency Gate

| # | Action | Expected Result | ✓ |
|---|--------|-----------------|---|
| 5.1 | Open task **seq 2** (the one that depends on seq 1) | | |
| 5.2 | Set `Status` = `In Progress` | | |
| 5.3 | **Save** | ❌ Should FAIL with **ValidationError** — "Cannot start Task ... dependencies are not completed" | |
| 5.4 | Click **Cancel** / close error | | |

---

## 6. Complete seq 1 (unassigned task)

| # | Action | Expected Result | ✓ |
|---|--------|-----------------|---|
| 6.1 | Open task **seq 1** ("Receive trial balance...") | | |
| 6.2 | Set `Status` = `Completed` | | |
| 6.3 | Set `Evidence Attachment` = `/assets/test/evidence.pdf` | | |
| 6.4 | **Save** | ✅ Task saved as Completed | |

---

## 7. Complete seq 2 (assigned task) + check notifications

| # | Action | Expected Result | ✓ |
|---|--------|-----------------|---|
| 7.1 | Open task **seq 2** ("Confirm tax period...") | | |
| 7.2 | Set `Status` = `Completed` | | |
| 7.3 | Set `Evidence Attachment` = `/assets/test/evidence.pdf` | | |
| 7.4 | **Save** | ✅ Task saved as Completed | |
| 7.5 | Open **Notification Log** list | You should see: | |
| | | — "Task completed: Confirm tax period..." for avilla | ☐ |
| | | (Optional: dependency notification for downstream tasks) | ☐ |

---

## 8. Complete remaining tasks with Review Gates

Tasks seq **3, 4, 5, 6** require a Review Gate approval before completion.

For each of these tasks (**seq 3, 4, 5, 6**):

| # | Action | Expected Result | ✓ |
|---|--------|-----------------|---|
| 8.1 | Try setting `Status` = `Completed` and **Save** | ❌ Should fail — "Review Gate approval is required" | |
| 8.2 | Open **Review Gate Register** → **+ Add** | | |
| 8.3 | Set `Task` = the task name | | |
| 8.4 | Set `Project` = the project | | |
| 8.5 | Set `Approval Status` = `Approved` | | |
| 8.6 | Set `Reviewed By` = `Administrator` | | |
| 8.7 | Set `Reviewer` = `Administrator` | | |
| 8.8 | **Save** → **Submit** | ✅ Review Gate is Approved | |
| 8.9 | Back in the task, set `Status` = `Completed`, add `Evidence Attachment`, **Save** | ✅ Task completes | |

Tasks **seq 7, 8, 9, 10** do NOT require a review gate:

| # | Action | Expected Result | ✓ |
|---|--------|-----------------|---|
| 8.10 | For each: set `Status` = `Completed`, add `Evidence Attachment`, **Save** | ✅ Task completes | |

---

## 9. Verify Closure Certificate + Performance Feedback

After the last task is completed:

| # | Action | Expected Result | ✓ |
|---|--------|-----------------|---|
| 9.1 | Open **Assignment Closure Certificate** list | A new Certificate exists for this project | |
| 9.2 | Open **Performance Feedback** list | A Feedback record exists for this project | |
| 9.3 | Open the **Project** again | Scroll to `Closure Certificate` field — should be linked | |
| 9.4 | Set Project `Status` = `Completed` | | |
| 9.5 | **Save** | ✅ Project closed | |

---

## 10. Test Customer sync to Open Originations

| # | Action | Expected Result | ✓ |
|---|--------|-----------------|---|
| 10.1 | Open **Alpha Assignment Origination** → **+ Add** | New Origination (no project yet) | |
| 10.2 | Fill with same Customer, title = "Sync Test" | | |
| 10.3 | **Save** (do NOT submit through workflow) | | |
| 10.4 | Go back to your **Customer** | | |
| 10.5 | Change `Risk Rating` to `Critical`, `Sector` to `Telecom` | | |
| 10.6 | **Save** | | |
| 10.7 | Open the open Origination (Sync Test) | | |
| 10.8 | Reload / check fields | ✅ `Risk Rating` updated to Critical, `Sector` updated to Telecom | |

---

## Summary Checklist

| # | Feature | Status |
|---|---------|--------|
| 1 | Customer created with all custom fields | ☐ |
| 2 | Origination autofills from Customer | ☐ |
| 3 | Workflow: Draft → Submitted → Under Review → Approved → Project Created | ☐ |
| 4 | Project auto-created with Tasks, SLA, Doc Requests | ☐ |
| 5 | Dependency gate blocks incomplete deps | ☐ |
| 6 | Task completion + Notification Log | ☐ |
| 7 | Review Gate approval required for flagged tasks | ☐ |
| 8 | Closure Certificate auto-created on last task completion | ☐ |
| 9 | Performance Feedback auto-created for assigned users | ☐ |
| 10 | Customer changes sync to open Originations | ☐ |
