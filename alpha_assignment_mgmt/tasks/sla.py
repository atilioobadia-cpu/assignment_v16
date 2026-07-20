import frappe
from frappe.utils import now_datetime, getdate, add_days

DEFAULT_THRESHOLD_HOURS = 24


def daily_sla_breach_check():
	"""Daily scheduler: check all active SLAs for impending breach and escalate."""
	threshold_hours = DEFAULT_THRESHOLD_HOURS

	active_slas = frappe.get_all(
		"Alpha Engagement SLA",
		filters={"docstatus": 1, "status": "Active"},
		pluck="name",
	)

	for sla_name in active_slas:
		sla = frappe.get_doc("Alpha Engagement SLA", sla_name)
		if not sla.alpha_processing_deadline:
			continue

		deadline = sla.alpha_processing_deadline
		hours_remaining = (deadline - now_datetime()).total_seconds() / 3600

		if hours_remaining <= 0:
			mark_breached(sla)
			escalate_sla(sla, 1)
		elif hours_remaining <= threshold_hours:
			notify_breach_warning(sla, hours_remaining)


def mark_breached(sla):
	"""Mark SLA as breached and notify."""
	frappe.db.set_value("Alpha Engagement SLA", sla.name, "status", "Breached")
	sla.reload()
	notify_breach(sla)


def escalate_sla(sla, current_level):
	"""Escalate SLA breach through levels: 1=EM, 2=BM, 3=Partner."""
	project = frappe.get_cached_doc("Project", sla.project) if sla.project else None
	if not project:
		return

	level_map = {
		1: {"role": "Alpha Engagement Manager", "user_field": "custom_engagement_manager", "label": "Level 1"},
		2: {"role": "Alpha Branch Manager", "user_field": "custom_branch_manager", "label": "Level 2"},
		3: {"role": "Alpha Partner/Director", "user_field": None, "label": "Level 3"},
	}

	level = level_map.get(current_level)
	if not level:
		return

	user_id = None
	if level["user_field"]:
		user_id = project.get(level["user_field"])
	else:
		partners = frappe.get_all(
			"Has Role",
			filters={"role": "Alpha Partner/Director", "parenttype": "User"},
			fields=["parent"],
			limit=1,
		)
		user_id = partners[0].parent if partners else None

	if not user_id:
		return

	email = frappe.db.get_value("User", user_id, "email")
	if email:
		days_overdue = getdate() - sla.alpha_processing_deadline
		frappe.sendmail(
			recipients=[email],
			subject=f"[AIMS] SLA Escalation {level['label']}: {sla.name}",
			message=(
				f"<div style='font-family: Arial, sans-serif; max-width: 600px;'>"
				f"<h2 style='color: #dc3545;'>SLA Escalation - {level['label']}</h2>"
				f"<p>SLA <b>{sla.name}</b> for project <b>{sla.project}</b> has been breached.</p>"
				f"<p>Days overdue: <b>{days_overdue.days}</b></p>"
				f"<p>This has been escalated to {level['role']}.</p>"
				f"</div>"
			),
		)

	# Check if we need to escalate further (every 3 days)
	if current_level < 3 and days_overdue.days >= current_level * 3:
		escalate_sla(sla, current_level + 1)


def notify_breach(sla):
	"""Send breach notification."""
	recipients = collect_recipients(sla)
	if recipients:
		customer_name = frappe.db.get_value("Customer", sla.customer, "customer_name") or sla.customer or "N/A"
		frappe.sendmail(
			recipients=recipients,
			subject=f"[AIMS] SLA Breached: {sla.name}",
			message=(
				f"<div style='font-family: Arial, sans-serif; max-width: 600px;'>"
				f"<h2 style='color: #dc3545;'>SLA Breach Alert</h2>"
				f"<table style='width: 100%; border-collapse: collapse; margin: 16px 0;'>"
				f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>SLA</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{sla.name}</td></tr>"
				f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>Project</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{sla.project}</td></tr>"
				f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>Client</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{customer_name}</td></tr>"
				f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>SLA Level</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{sla.sla_level}</td></tr>"
				f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>Deadline</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd; color: #dc3545;'><b>{sla.alpha_processing_deadline}</b></td></tr>"
				f"</table>"
				f"<p style='color: #dc3545;'><b>This SLA has been breached. Immediate action required.</b></p>"
				f"<p style='color: #666; font-size: 12px;'>Alpha Assignment Management System</p>"
				f"</div>"
			),
		)


def notify_breach_warning(sla, hours_remaining):
	"""Send breach warning notification."""
	recipients = collect_recipients(sla)
	if recipients:
		customer_name = frappe.db.get_value("Customer", sla.customer, "customer_name") or sla.customer or "N/A"
		frappe.sendmail(
			recipients=recipients,
			subject=f"[AIMS] SLA Breach Warning: {sla.name}",
			message=(
				f"<div style='font-family: Arial, sans-serif; max-width: 600px;'>"
				f"<h2 style='color: #ffc107;'>SLA Breach Warning</h2>"
				f"<table style='width: 100%; border-collapse: collapse; margin: 16px 0;'>"
				f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>SLA</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{sla.name}</td></tr>"
				f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>Project</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{sla.project}</td></tr>"
				f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>Client</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{customer_name}</td></tr>"
				f"<tr><td style='padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;'>Time Remaining</td>"
				f"<td style='padding: 8px; border-bottom: 1px solid #ddd; color: #ffc107;'><b>{int(hours_remaining)} hours</b></td></tr>"
				f"</table>"
				f"<p>Please take action to avoid SLA breach.</p>"
				f"<p style='color: #666; font-size: 12px;'>Alpha Assignment Management System</p>"
				f"</div>"
			),
		)


def collect_recipients(sla):
	"""Collect relevant stakeholders for SLA notifications."""
	recipients = []
	if sla.project:
		project = frappe.get_cached_doc("Project", sla.project)
		if project.custom_engagement_manager:
			email = frappe.db.get_value("User", project.custom_engagement_manager, "email")
			if email:
				recipients.append(email)
		if project.custom_branch_manager:
			email = frappe.db.get_value("User", project.custom_branch_manager, "email")
			if email:
				recipients.append(email)
	return list(set(recipients))
