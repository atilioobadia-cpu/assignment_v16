import frappe
from frappe.utils import add_days, today


@frappe.whitelist()
def get_top_bottom(days=30):
	"""Return top 4 contributors and bottom 3 performers."""
	since = add_days(today(), -int(days))

	# Get all active employees with user_id
	employees = frappe.get_all(
		"Employee",
		filters={"status": "Active", "user_id": ["is", "set"]},
		fields=["name", "employee_name", "user_id"],
	)
	if not employees:
		return {"top_contributors": [], "bottom_performers": []}

	results = []
	for emp in employees:
		hours = frappe.db.sql("""
			SELECT COALESCE(SUM(tt.hours), 0)
			FROM `tabTimesheet Detail` tt
			JOIN `tabTimesheet` t ON t.name = tt.parent
			WHERE t.employee = %s AND t.start_date >= %s AND t.docstatus = 1
		""", (emp.name, since))
		hours_logged = float(hours[0][0]) if hours else 0.0

		tasks = frappe.db.sql("""
			SELECT COUNT(DISTINCT tel.parent)
			FROM `tabTask Employee Log` tel
			JOIN `tabTask` task ON task.name = tel.parent
			WHERE tel.employee = %s
			AND task.status = 'Completed'
			AND task.completed_on >= %s
		""", (emp.name, since))
		tasks_completed = int(tasks[0][0]) if tasks else 0

		results.append({
			"employee_name": emp.employee_name,
			"hours_logged": hours_logged,
			"tasks_completed": tasks_completed,
		})

	# Sort by combined score: hours + tasks * 8
	results.sort(key=lambda x: x["hours_logged"] + x["tasks_completed"] * 8, reverse=True)

	return {
		"top_contributors": results[:4],
		"bottom_performers": list(reversed(results[-3:])) if len(results) >= 3 else list(reversed(results)),
	}
