import json
import frappe
from frappe.utils import today, add_days, now_datetime


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
				customer_name = frappe.db.get_value("Customer", project.customer, "customer_name") or project.customer or "N/A"
				frappe.sendmail(
					recipients=list(recipients),
					subject=f"[AIMS] Overdue Task: {task.subject}",
					message=(
						f"<div style='font-family: Arial, sans-serif; max-width: 600px;'>"
						f"<h2 style='color: #dc3545;'>Task Overdue Alert</h2>"
						f"<table style='width: 100%; border-collapse: collapse; margin: 16px 0;'>"
						f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>Task</td>"
						f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{task.subject}</td></tr>"
						f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>Project</td>"
						f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{task.project}</td></tr>"
						f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>Client</td>"
						f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{customer_name}</td></tr>"
						f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>Due Date</td>"
						f"<td style='padding: 8px; border-bottom: 1px solid #ddd; color: #dc3545;'><b>{task.exp_end_date}</b></td></tr>"
						f"</table>"
						f"<p>Please take immediate action to resolve this overdue task.</p>"
						f"<p style='color: #666; font-size: 12px;'>Alpha Assignment Management System</p>"
						f"</div>"
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
			filters={"custom_engagement_manager": manager, "status": "Active"},
			pluck="name",
		)

		if not projects:
			continue

		report_lines = []
		total_hours_week = 0
		total_tasks_week = 0

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

			total_hours_week += total_hours
			total_tasks_week += task_count

			customer = frappe.db.get_value("Project", project_name, "customer") or "N/A"
			customer_name = frappe.db.get_value("Customer", customer, "customer_name") or customer

			report_lines.append(
				f"<tr>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{project_name}</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{customer_name}</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd; text-align: center;'>{total_hours:.1f}</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd; text-align: center;'>{task_count}</td>"
				f"</tr>"
			)

		if report_lines:
			table = (
				"<div style='font-family: Arial, sans-serif; max-width: 700px;'>"
				"<h2 style='color: #2563eb;'>Weekly Productivity Report</h2>"
				"<p>Here is your team's performance summary for the past week.</p>"
				"<table style='width: 100%; border-collapse: collapse; margin: 16px 0;'>"
				"<tr style='background-color: #f8f9fa;'>"
				"<th style='padding: 8px; text-align: left; border-bottom: 2px solid #ddd;'>Project</th>"
				"<th style='padding: 8px; text-align: left; border-bottom: 2px solid #ddd;'>Client</th>"
				"<th style='padding: 8px; text-align: center; border-bottom: 2px solid #ddd;'>Hours</th>"
				"<th style='padding: 8px; text-align: center; border-bottom: 2px solid #ddd;'>Tasks Done</th>"
				"</tr>"
				+ "".join(report_lines)
				+ f"</table>"
				f"<div style='margin-top: 16px; padding: 12px; background-color: #f8f9fa; border-radius: 4px;'>"
				f"<b>Weekly Totals:</b> {total_hours_week:.1f} hours | {total_tasks_week} tasks completed"
				f"</div>"
				f"<p style='color: #666; font-size: 12px;'>Alpha Assignment Management System</p>"
				f"</div>"
			)
			frappe.sendmail(
				recipients=[manager],
				subject=f"[AIMS] Weekly Productivity Report ({today()})",
				message=table,
			)
