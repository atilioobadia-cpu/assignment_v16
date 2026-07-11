import frappe
from frappe.utils import now_datetime

DEFAULT_THRESHOLD_HOURS = 24


def daily_sla_breach_check():
	"""Daily scheduler: check all active SLAs for impending breach."""
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
		elif hours_remaining <= threshold_hours:
			notify_breach_warning(sla, hours_remaining)


def mark_breached(sla):
	"""Mark SLA as breached and notify."""
	frappe.db.set_value("Alpha Engagement SLA", sla.name, "status", "Breached")
	sla.reload()
	notify_breach(sla)


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
