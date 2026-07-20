import frappe
import json
from frappe.utils import now_datetime, getdate


def validate(doc, method):
	check_evidence_attachment(doc)
	check_review_gate(doc)
	check_client_delay(doc)
	check_task_dependencies(doc)
	sync_assign_from_custom_assigned_to(doc)


def sync_assign_from_custom_assigned_to(doc):
	"""Sync _assign from custom_assigned_to for notification delivery."""
	if doc.custom_assigned_to and not doc.get("_assign"):
		doc._assign = frappe.as_json([doc.custom_assigned_to])


def on_update(doc, method):
	check_task_overdue(doc)
	notify_blocked_tasks(doc)
	create_notification_log(doc)
	if doc.status == "Completed" and doc.project:
		_check_project_completion(doc.project)


def _check_project_completion(project_name):
	"""Trigger closure cert + PF creation when all project tasks are complete."""
	project = frappe.get_doc("Project", project_name)
	if not project:
		return
	if frappe.db.exists("Assignment Closure Certificate", {"project": project_name}):
		return
	remaining = frappe.db.count(
		"Task",
		filters={"project": project_name, "status": ["not in", ["Completed", "Cancelled"]]},
	)
	if remaining > 0:
		return
	from alpha_assignment_mgmt.overrides.project import _auto_create_closure_certificate
	_auto_create_closure_certificate(project)


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
		assigned = []
		if doc.get("_assign"):
			try:
				assigned = json.loads(doc._assign)
			except (json.JSONDecodeError, TypeError):
				pass
		if user in assigned or user == doc.custom_assigned_to:
			return True

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

			if doc.project:
				project = frappe.get_cached_doc("Project", doc.project)
				delay.customer = project.customer
				delay.escalation_level = "Level 1 - Staff"
				delay.impact = "Medium"
				delay.missing_information = (
					f"Task '{doc.subject}' is waiting for client response. "
					f"Expected completion: {doc.exp_end_date or 'Not set'}."
				)

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
			check_sla_breach(doc)


def check_sla_breach(doc):
	"""Auto-breach Engagement SLA when task is overdue."""
	if not doc.project:
		return

	sla = frappe.db.get_value(
		"Alpha Engagement SLA",
		{"project": doc.project, "docstatus": 1, "status": ["not in", ["Met", "Breached"]]},
		["name", "status"],
		as_dict=True,
	)
	if not sla or sla.name is None:
		return

	breached_count = frappe.db.count(
		"Task",
		filters={
			"project": doc.project,
			"status": ["not in", ["Completed", "Cancelled"]],
			"exp_end_date": ["<", getdate()],
		},
	)

	if breached_count > 0:
		frappe.db.set_value("Alpha Engagement SLA", sla.name, "status", "Breached")
		frappe.db.set_value("Alpha Engagement SLA", sla.name, "actual_end_date", getdate())

		sla_doc = frappe.get_doc("Alpha Engagement SLA", sla.name)
		if sla_doc.project:
			project = frappe.db.get_value(
				"Project", sla_doc.project, "custom_assignment_origination"
			)
			if project:
				frappe.db.set_value(
					"Alpha Assignment Origination", project, "sl_status", "SLA Breached"
				)


def get_assigned_users(doc):
	users = []
	if doc.get("_assign"):
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
		users = get_assigned_users(doc) or ([doc.custom_assigned_to] if doc.custom_assigned_to else [])
		for user_id in users:
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


def notify_blocked_tasks(doc):
	"""When a task is completed, notify assignees of downstream tasks that depend on it."""
	if doc.status != "Completed":
		return

	blocked_tasks = frappe.get_all(
		"Task",
		filters={"custom_depends_on_tasks": ["like", f"%{doc.name}%"], "status": ["!=", "Completed"]},
		fields=["name", "subject", "_assign", "custom_assigned_to"],
	)

	for bt in blocked_tasks:
		users = get_assigned_users_of_task(bt.get("_assign")) or ([bt.custom_assigned_to] if bt.custom_assigned_to else [])
		for user_id in users:
			email = frappe.db.get_value("User", user_id, "email")
			if not email:
				continue
			try:
				frappe.sendmail(
					recipients=[email],
					subject=f"[AIMS] Dependency Completed: {bt.subject}",
					message=(
						f"<h3>Task Dependency Resolved</h3>"
						f"<p>Task <b>{doc.subject}</b> that you were waiting on has been completed.</p>"
						f"<p>You can now start working on <b>{bt.subject}</b>.</p>"
					),
				)
			except Exception:
				pass
			_add_notification_log(user_id, f"Dependency completed: {doc.subject}. You can now start {bt.subject}.", bt.name)


def get_assigned_users_of_task(assign_value):
	if not assign_value:
		return []
	try:
		users = json.loads(assign_value)
		return users if isinstance(users, list) else []
	except (json.JSONDecodeError, TypeError):
		return []


def create_notification_log(doc):
	"""Create in-app notification for task assignment/status changes."""
	subject = None
	users = get_assigned_users_of_task(doc.get("_assign")) or ([doc.custom_assigned_to] if doc.custom_assigned_to else [])
	if doc.status == "Completed":
		subject = f"Task completed: {doc.subject}"
	elif doc.status == "Overdue":
		subject = f"Task overdue: {doc.subject}"
	elif doc.get("_assign"):
		for user_id in users:
			_add_notification_log(user_id, f"You have been assigned task: {doc.subject}", doc.name)

	if subject:
		for user_id in users:
			_add_notification_log(user_id, subject, doc.name)


def _add_notification_log(user_id, subject, document=None):
	"""Insert a Notification Log entry for the user."""
	log = frappe.get_doc({
		"doctype": "Notification Log",
		"subject": subject,
		"email_content": subject,
		"for_user": user_id,
		"type": "Alert",
		"document_type": "Task",
		"document_name": document,
	})
	log.flags.ignore_permissions = True
	log.insert()
