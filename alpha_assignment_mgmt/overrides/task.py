import frappe
import json
from frappe.utils import now_datetime, getdate


def validate(doc, method):
	check_evidence_attachment(doc)
	check_review_gate(doc)
	check_client_delay(doc)
	check_task_dependencies(doc)


def on_update(doc, method):
	check_task_overdue(doc)


def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user

	roles = frappe.get_roles(user)
	user_like = frappe.db.escape(f'%"{user}"%')

	if "System Manager" in roles or "Alpha Partner/Director" in roles:
		return ""

	if "Alpha Engagement Manager" in roles:
		return f"""(`tabTask`.`project` IN (
			SELECT `tabProject`.`name` FROM `tabProject`
			WHERE `tabProject`.`custom_engagement_manager` = %(user)s
		) OR `tabTask`.`_assign` LIKE {user_like}
		  OR `tabTask`.`owner` = %(user)s)"""

	if "Alpha Branch Manager" in roles:
		return f"""(`tabTask`.`project` IN (
			SELECT `tabProject`.`name` FROM `tabProject`
			WHERE `tabProject`.`custom_branch_manager` = %(user)s
		) OR `tabTask`.`_assign` LIKE {user_like}
		  OR `tabTask`.`owner` = %(user)s)"""

	if "Alpha Staff" in roles or "Alpha Reviewer" in roles:
		return f"""(`tabTask`.`_assign` LIKE {user_like}
			OR `tabTask`.`owner` = %(user)s)"""

	if "Alpha Client Owner" in roles:
		return f"""(`tabTask`.`project` IN (
			SELECT `tabProject`.`name` FROM `tabProject`
			WHERE `tabProject`.`custom_client_owner` = %(user)s
		) OR `tabTask`.`_assign` LIKE {user_like}
		  OR `tabTask`.`owner` = %(user)s)"""

	return ""


def has_permission(doc, ptype, user):
	roles = frappe.get_roles(user)

	if "System Manager" in roles or "Alpha Partner/Director" in roles:
		return True

	if "Alpha Engagement Manager" in roles or "Alpha Branch Manager" in roles:
		return True

	if "Alpha Staff" in roles or "Alpha Reviewer" in roles:
		if doc.owner == user:
			return True
		if doc._assign:
			try:
				assigned = json.loads(doc._assign)
				if user in assigned:
					return True
			except (json.JSONDecodeError, TypeError):
				pass

	if "Alpha Client Owner" in roles:
		if doc.project:
			owner = frappe.db.get_value("Project", doc.project, "custom_client_owner")
			if owner == user:
				return True

	return False


def check_evidence_attachment(doc):
	if doc.status == "Completed":
		if not doc.custom_evidence_attachment and not doc.custom_evidence_exception:
			frappe.throw(
				f"Cannot mark Task {doc.name} as Completed. "
				"Evidence attachment or approved exception is required."
			)


def check_review_gate(doc):
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
	if doc.status == "Waiting for Client":
		if not doc.custom_client_delay_log:
			delay = frappe.new_doc("Client Delay Log")
			delay.task = doc.name
			delay.project = doc.project
			delay.date_requested = now_datetime()
			delay.status = "Open"
			delay.insert(ignore_permissions=True)
			doc.custom_client_delay_log = delay.name


def check_task_dependencies(doc):
	"""Prevent starting a task if its dependencies are not completed."""
	if doc.status not in ("In Progress", "Completed"):
		return

	if not doc.custom_depends_on_tasks:
		return

	dep_names = [d.strip() for d in doc.custom_depends_on_tasks.split(",") if d.strip()]
	if not dep_names:
		return

	incomplete = []
	for dep_name in dep_names:
		dep_status = frappe.db.get_value("Task", dep_name, "status")
		if dep_status not in ("Completed", "Cancelled"):
			incomplete.append(f"{dep_name} ({dep_status or 'not found'})")

	if incomplete:
		frappe.throw(
			f"Cannot start Task {doc.name}. The following dependencies are not completed: "
			+ ", ".join(incomplete)
		)


def check_task_overdue(doc):
	if doc.status not in ("Completed", "Cancelled") and doc.exp_end_date:
		deadline = doc.exp_end_date
		if hasattr(deadline, "date"):
			deadline = deadline.date()
		if deadline < getdate():
			send_overdue_notification(doc)


def get_assigned_users(doc):
	users = []
	if doc._assign:
		try:
			users = json.loads(doc._assign)
		except (json.JSONDecodeError, TypeError):
			pass
	return users if isinstance(users, list) else []


def send_overdue_notification(doc):
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
					f"<h3>Task Overdue Alert</h3>"
					f"<p>Task <b>{doc.subject}</b> in Project <b>{doc.project}</b> "
					f"was due on <b>{doc.exp_end_date}</b> and is now overdue.</p>"
					f"<p>Please take immediate action.</p>"
				),
			)
