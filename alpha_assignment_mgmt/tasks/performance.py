import frappe
from frappe.utils import today, add_days

"""
Daily scheduled job to compute employee performance metrics.

Metrics computed per employee:
- hours_logged_30d: total billable hours in last 30 days
- tasks_completed_30d: tasks marked Completed in last 30 days
- active_assignments: count of active projects as Engagement Manager
- sla_compliance_rate: percentage of non-breached SLAs
- utilization_rate_30d: (hours_logged / available_hours) * 100
"""


def daily_performance_computation():
	"""Compute and store performance metrics for all active employees."""
	employees = frappe.get_all(
		"Employee",
		filters={"status": "Active", "user_id": ["is", "set"]},
		fields=["name", "user_id", "employee_name"],
	)

	for emp in employees:
		compute_employee_metrics(emp)


def compute_employee_metrics(emp):
	"""Compute all performance metrics for a single employee."""
	thirty_days_ago = add_days(today(), -30)

	hours_logged = get_hours_logged(emp, thirty_days_ago)
	tasks_completed = get_tasks_completed(emp, thirty_days_ago)
	active_assignments = get_active_assignments(emp)
	sla_rate = get_sla_compliance_rate(emp)
	utilization = get_utilization_rate(emp, thirty_days_ago)

	store_metrics(emp.name, {
		"custom_hours_logged_30d": hours_logged,
		"custom_tasks_completed_30d": tasks_completed,
		"custom_active_assignments": active_assignments,
		"custom_sla_compliance_rate": sla_rate,
		"custom_utilization_rate_30d": utilization,
	})

	return {
		"employee": emp.employee_name,
		"hours_logged": hours_logged,
		"tasks_completed": tasks_completed,
		"active_assignments": active_assignments,
		"sla_compliance": sla_rate,
		"utilization": utilization,
	}


def get_hours_logged(emp, since):
	"""Total billable hours logged in timesheets since date."""
	result = frappe.db.sql("""
		SELECT COALESCE(SUM(tt.hours), 0)
		FROM `tabTimesheet Detail` tt
		JOIN `tabTimesheet` t ON t.name = tt.parent
		WHERE t.employee = %s
		AND t.start_date >= %s
		AND t.docstatus = 1
	""", (emp.name, since))
	return float(result[0][0]) if result else 0.0


def get_tasks_completed(emp, since):
	"""Count tasks completed since date via Task Employee Log."""
	result = frappe.db.sql("""
		SELECT COUNT(DISTINCT tel.parent)
		FROM `tabTask Employee Log` tel
		JOIN `tabTask` task ON task.name = tel.parent
		WHERE tel.employee = %s
		AND task.status = 'Completed'
		AND task.completed_on >= %s
	""", (emp.name, since))
	return int(result[0][0]) if result else 0


def get_active_assignments(emp):
	"""Count active projects where employee is Engagement Manager."""
	return frappe.db.count(
		"Project",
		filters={
			"custom_engagement_manager": emp.user_id,
			"status": ["!=", "Completed"],
		},
	)


def get_sla_compliance_rate(emp):
	"""Percentage of non-breached SLAs for the employee's projects."""
	projects = frappe.get_all(
		"Project",
		filters={"custom_engagement_manager": emp.user_id},
		pluck="name",
	)
	if not projects:
		return 100.0

	total = frappe.db.count(
		"Alpha Engagement SLA",
		filters={"project": ["in", projects], "docstatus": 1},
	)
	if not total:
		return 100.0

	breached = frappe.db.count(
		"Alpha Engagement SLA",
		filters={"project": ["in", projects], "status": "Breached", "docstatus": 1},
	)
	return round(((total - breached) / total) * 100, 1)


def get_utilization_rate(emp, since):
	"""Utilization rate: hours logged / (working days * 8) * 100."""
	working_days = frappe.db.count(
		"Attendance",
		filters={
			"employee": emp.name,
			"status": "Present",
			"attendance_date": [">=", since],
		},
	)
	if not working_days:
		return 0.0
	available_hours = working_days * 8
	hours_logged = get_hours_logged(emp, since)
	return round((hours_logged / available_hours) * 100, 1) if available_hours > 0 else 0.0


def store_metrics(employee, metrics):
	"""Store computed metrics as custom fields on Employee."""
	for field, value in metrics.items():
		frappe.db.set_value("Employee", employee, field, value, update_modified=False)
