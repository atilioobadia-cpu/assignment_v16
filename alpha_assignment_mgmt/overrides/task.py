import frappe
import json
from frappe.utils import now_datetime, getdate


def validate(doc, method):
	"""Enforce evidence attachment and review gate rules."""
	check_evidence_attachment(doc)
	check_review_gate(doc)
	check_client_delay(doc)


def on_update(doc, method):
	"""Update SLA status and notify on overdue."""
	check_task_overdue(doc)


def check_evidence_attachment(doc):
	"""Task cannot be completed without evidence or exception."""
	if doc.status == "Completed":
		if not doc.custom_evidence_attachment and not doc.custom_evidence_exception:
			frappe.throw(
				f"Cannot mark Task {doc.name} as Completed. "
				"Evidence attachment or approved exception is required."
			)


def check_review_gate(doc):
	"""High-risk tasks require Review Gate approval before completion."""
	if doc.status == "Completed" and doc.custom_requires_review:
		gate = frappe.db.get_value(
			"Review Gate Register",
			{"task": doc.name, "docstatus": 1},
			"approval_status",
		)
		if gate != "Approved":
			frappe.throw(
				f"Cannot mark Task {doc.name} as Completed. "
				"Review Gate approval is required for this task."
			)


def check_client_delay(doc):
	"""When task status is Waiting for Client, require Client Delay Log."""
	if doc.status == "Waiting for Client":
		if not doc.custom_client_delay_log:
			delay = frappe.new_doc("Client Delay Log")
			delay.task = doc.name
			delay.project = doc.project
			delay.date_requested = now_datetime()
			delay.status = "Open"
			delay.insert(ignore_permissions=True)
			doc.custom_client_delay_log = delay.name


def check_task_overdue(doc):
	"""Notify when task is overdue."""
	if doc.status not in ("Completed", "Cancelled") and doc.exp_end_date:
		deadline = doc.exp_end_date
		if hasattr(deadline, "date"):
			deadline = deadline.date()
		if deadline < getdate():
			send_overdue_notification(doc)


def get_assigned_users(doc):
	"""Extract assigned user IDs from _assign field."""
	users = []
	if doc._assign:
		try:
			users = json.loads(doc._assign)
		except (json.JSONDecodeError, TypeError):
			pass
	return users if isinstance(users, list) else []


def send_overdue_notification(doc):
	"""Send notification for overdue task."""
	if doc.project:
		project = frappe.get_cached_doc("Project", doc.project)
		recipients = []
		if project.custom_engagement_manager:
			email = frappe.db.get_value(
				"User", project.custom_engagement_manager, "email"
			)
			if email:
				recipients.append(email)
		for user_id in get_assigned_users(doc):
			email = frappe.db.get_value("User", user_id, "email")
			if email:
				recipients.append(email)
		if recipients:
			frappe.sendmail(
				recipients=recipients,
				subject=f"Overdue Task: {doc.subject}",
				message=(
					f"Task <b>{doc.subject}</b> in Project <b>{doc.project}</b> "
					f"was due on {doc.exp_end_date} and is now overdue."
				),
			)
