import frappe
from frappe.utils import today, getdate


def daily_delay_escalation_check():
	"""Escalate Client Delay Logs based on duration thresholds.

	Level 1 - Branch Manager: day 0-7
	Level 2 - Partner/Director: day 8-15
	Level 3 - Director/CFO: day 16+
	"""
	delays = frappe.get_all(
		"Client Delay Log",
		filters={
			"docstatus": 0,
			"status": ["!=", "Resolved"],
		},
		fields=["name", "project", "escalation_level", "date_requested", "customer"],
	)

	for delay in delays:
		if not delay.date_requested:
			continue

		days_open = (getdate() - delay.date_requested).days

		new_level = None
		if days_open >= 16:
			new_level = "Level 3 - Director/CFO"
		elif days_open >= 8:
			new_level = "Level 2 - Partner/Director"
		elif days_open >= 4:
			new_level = "Level 1 - Branch Manager"

		if new_level and new_level != delay.escalation_level:
			frappe.db.set_value("Client Delay Log", delay.name, "escalation_level", new_level)
			_notify_escalation(delay, new_level)


def _notify_escalation(delay, level):
	"""Notify the escalated party about the delay."""
	if not delay.project:
		return

	project = frappe.get_cached_doc("Project", delay.project)
	user_id = None
	role = None

	if "Branch Manager" in level:
		user_id = project.custom_branch_manager
		role = "Branch Manager"
	elif "Partner/Director" in level:
		role_users = frappe.get_all(
			"Has Role",
			filters={"role": "Alpha Partner/Director", "parenttype": "User"},
			fields=["parent"],
			limit=1,
		)
		user_id = role_users[0].parent if role_users else None
		role = "Partner/Director"
	elif "Director/CFO" in level:
		role_users = frappe.get_all(
			"Has Role",
			filters={"role": "Director/CFO", "parenttype": "User"},
			fields=["parent"],
			limit=1,
		)
		user_id = role_users[0].parent if role_users else None
		role = "Director/CFO"
	else:
		return

	if not user_id:
		return

	email = frappe.db.get_value("User", user_id, "email")
	if email:
		customer_name = frappe.db.get_value("Customer", delay.customer, "customer_name") or delay.customer
		frappe.sendmail(
			recipients=[email],
			subject=f"[AIMS] Client Delay Escalated to {role}: {delay.name}",
			message=(
				f"<div style='font-family: Arial, sans-serif; max-width: 600px;'>"
				f"<h2 style='color: #dc3545;'>Client Delay Escalation</h2>"
				f"<p>A client delay has been escalated to <b>{role}</b>.</p>"
				f"<table style='width: 100%; border-collapse: collapse; margin: 16px 0;'>"
				f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>Project</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{delay.project}</td></tr>"
				f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>Customer</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{customer_name}</td></tr>"
				f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>Escalation Level</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{level}</td></tr>"
				f"</table>"
				f"<p>Immediate intervention is required.</p>"
				f"<p style='color: #666; font-size: 12px;'>Alpha Assignment Management System</p>"
				f"</div>"
			),
		)
