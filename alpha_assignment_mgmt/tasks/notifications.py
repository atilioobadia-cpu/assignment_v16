import json
import frappe
from frappe.utils import today, now_datetime
from frappe.utils.data import getdate


def daily_overdue_task_notification():
	"""Daily scheduler: notify managers and assigned users of overdue tasks."""
	overdue_tasks = frappe.get_all(
		"Task",
		filters={
			"status": ["not in", ["Completed", "Cancelled"]],
			"exp_end_date": ["<", today()],
		},
		fields=["name", "subject", "project", "exp_end_date", "_assign"],
	)

	for task in overdue_tasks:
		if task.project:
			project = frappe.get_cached_doc("Project", task.project)
			recipients = set()
			if project.custom_engagement_manager:
				email = frappe.db.get_value(
					"User", project.custom_engagement_manager, "email"
				)
				if email:
					recipients.add(email)
			for user_id in _get_assigned_users(task._assign):
				email = frappe.db.get_value("User", user_id, "email")
				if email:
					recipients.add(email)
			if recipients:
				frappe.sendmail(
					recipients=list(recipients),
					subject=f"Overdue Task: {task.subject}",
					message=(
						f"Task <b>{task.subject}</b> in Project <b>{task.project}</b> "
						f"was due on {task.exp_end_date}."
					),
				)


def _get_assigned_users(assign_value):
	"""Parse _assign JSON string to get list of user IDs."""
	if not assign_value:
		return []
	try:
		users = json.loads(assign_value)
		return users if isinstance(users, list) else []
	except (json.JSONDecodeError, TypeError):
		return []


def weekly_productivity_report():
	"""Weekly scheduler: email productivity report to managers."""
	if today().weekday() != 0:
		return

	managers = frappe.get_all(
		"User",
		filters=[
			["Has Role", "role", "=", "Alpha Engagement Manager"],
			["enabled", "=", 1],
		],
		pluck="name",
	)

	for manager in managers:
		projects = frappe.get_all(
			"Project",
			filters={"custom_engagement_manager": manager},
			pluck="name",
		)

		if not projects:
			continue

		report_lines = []
		for project_name in projects:
			total_hours = frappe.db.sql(
				"""
				SELECT COALESCE(SUM(tt.hours), 0)
				FROM `tabTimesheet Detail` tt
				JOIN `tabTimesheet` t ON t.name = tt.parent
				WHERE tt.project = %s
				AND t.docstatus = 1
				AND t.start_date >= %s
				AND t.start_date < %s
				""",
				(project_name, add_days(today(), -7), today()),
			)[0][0]

			task_count = frappe.db.count(
				"Task",
				{
					"project": project_name,
					"status": "Completed",
					"modified": [">=", add_days(today(), -7)],
				},
			)

			report_lines.append(
				f"<tr><td>{project_name}</td><td>{total_hours:.1f}</td>"
				f"<td>{task_count}</td></tr>"
			)

		if report_lines:
			table = (
				"<table border='1' cellpadding='5'>"
				"<tr><th>Project</th><th>Hours Logged</th><th>Tasks Completed</th></tr>"
				+ "".join(report_lines)
				+ "</table>"
			)
			frappe.sendmail(
				recipients=[manager],
				subject=f"Weekly Productivity Report ({today()})",
				message=table,
			)


def add_days(date, days):
	"""Add days to a date string."""
	from datetime import timedelta
	if isinstance(date, str):
		date = getdate(date)
	return (date + timedelta(days=days)).isoformat()
