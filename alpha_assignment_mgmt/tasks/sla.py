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
		frappe.sendmail(
			recipients=recipients,
			subject=f"SLA Breach: {sla.name}",
			message=(
				f"SLA <b>{sla.name}</b> for Project <b>{sla.project}</b> "
				"has been breached."
			),
		)


def notify_breach_warning(sla, hours_remaining):
	"""Send breach warning notification."""
	recipients = collect_recipients(sla)
	if recipients:
		frappe.sendmail(
			recipients=recipients,
			subject=f"SLA Breach Warning: {sla.name}",
			message=(
				f"SLA <b>{sla.name}</b> for Project <b>{sla.project}</b> "
				f"is approaching breach ({int(hours_remaining)} hours remaining)."
			),
		)


def collect_recipients(sla):
	"""Collect relevant stakeholders for SLA notifications."""
	recipients = []
	if sla.project:
		project = frappe.get_cached_doc("Project", sla.project)
		if project.custom_engagement_manager:
			recipients.append(project.custom_engagement_manager)
	if sla.customer:
		email = frappe.db.get_value("Customer", sla.customer, "email_id")
		if email:
			recipients.append(email)
	return [r for r in recipients if r]
