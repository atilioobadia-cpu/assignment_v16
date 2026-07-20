import frappe
from frappe.utils import today


@frappe.whitelist()
def create_timesheet_from_tasks(employee=None, project=None):
	"""Auto-create a Timesheet pre-populated with assigned tasks that are not completed.
	
	Called from a button on the Timesheet list or via custom button.
	"""
	if not employee:
		user_id = frappe.session.user
		employee = frappe.db.get_value("Employee", {"user_id": user_id}, "name")
		if not employee:
			frappe.throw("No Employee record found for the current user.")

	filters = {
		"status": ["not in", ["Completed", "Cancelled"]],
	}

	if project:
		filters["project"] = project

	# Get tasks assigned to this employee's user
	user_id = frappe.db.get_value("Employee", employee, "user_id")
	if user_id:
		filters["_assign"] = ["like", f"%{user_id}%"]
	else:
		frappe.throw("Employee has no linked User.")

	tasks = frappe.get_all(
		"Task",
		filters=filters,
		fields=["name", "subject", "project", "custom_expected_hours", "expected_time"],
		limit=20,
	)

	if not tasks:
		frappe.msgprint("No pending tasks found to add to timesheet.")
		return

	ts = frappe.new_doc("Timesheet")
	ts.employee = employee
	ts.company = frappe.defaults.get_user_default("company")

	for task in tasks:
		hours = task.custom_expected_hours or 1.0
		ts.append("time_logs", {
			"activity_type": "Client Communication",
			"task": task.name,
			"project": task.project,
			"hours": hours,
			"description": task.subject,
			"from_time": today(),
		})

	ts.flags.ignore_permissions = True
	ts.insert()

	frappe.msgprint(f"Timesheet created with {len(tasks)} task(s).")
	return ts.name
