import frappe
from frappe.utils import today


def before_insert(doc, method):
	"""Auto-fill Origination fields from Customer record (central hub)."""
	customer_fields = frappe.db.get_value("Customer", doc.customer, [
		"custom_engagement_manager", "custom_client_owner", "custom_branch_manager",
		"custom_service_line", "custom_risk_rating", "custom_sector",
		"tax_id", "customer_name", "mobile_no", "email_id",
	], as_dict=True)

	if not customer_fields:
		return

	if customer_fields.custom_engagement_manager and not doc.engagement_manager:
		doc.engagement_manager = customer_fields.custom_engagement_manager
	if customer_fields.custom_client_owner and not doc.client_owner:
		doc.client_owner = customer_fields.custom_client_owner
	if customer_fields.custom_branch_manager and not doc.lead_branch_manager:
		doc.lead_branch_manager = customer_fields.custom_branch_manager
	if customer_fields.custom_service_line and not doc.service_line:
		doc.service_line = customer_fields.custom_service_line
	if customer_fields.custom_risk_rating and not doc.risk_rating:
		doc.risk_rating = customer_fields.custom_risk_rating
	if customer_fields.custom_sector and not doc.sector:
		doc.sector = customer_fields.custom_sector
	if customer_fields.tax_id and not doc.tin_reference:
		doc.tin_reference = customer_fields.tax_id
	if customer_fields.customer_name and not doc.client_focal_person:
		doc.client_focal_person = customer_fields.customer_name
	if customer_fields.mobile_no and not doc.contact_number:
		doc.contact_number = customer_fields.mobile_no
	if customer_fields.email_id and not doc.email:
		doc.email = customer_fields.email_id


@frappe.whitelist()
def create_project_from_origination(origination_name):
	"""API endpoint to create Project from Origination (called from JS button)."""
	doc = frappe.get_doc("Alpha Assignment Origination", origination_name)

	if doc.workflow_state != "Approved":
		frappe.throw("Assignment Origination must be approved before creating a Project.")

	if doc.project_created:
		frappe.throw(f"Project already created: {doc.project_reference}")

	existing_project = frappe.db.get_value(
		"Project", {"custom_assignment_origination": doc.name}, "name"
	)
	if existing_project:
		frappe.db.set_value(doc.doctype, doc.name, {
			"project_reference": existing_project,
			"project_created": 1,
		})
		frappe.throw(f"Project already created: {existing_project}")

	return _create_project(doc)


def on_update(doc, method):
	"""When Origination is submitted AND approved, auto-create Project and Document Requests."""
	if doc.workflow_state != "Approved":
		return

	if doc.project_created:
		return

	existing_project = frappe.db.get_value(
		"Project", {"custom_assignment_origination": doc.name}, "name"
	)
	if existing_project:
		frappe.db.set_value(doc.doctype, doc.name, {
			"project_reference": existing_project,
			"project_created": 1,
		})
		return

	if hasattr(doc, "docstatus") and doc.docstatus != 1:
		return

	project_name = _create_project(doc)
	_create_document_requests(doc, project_name)


def _create_project(doc):
	"""Internal: create Project from Origination and link back."""
	expected_end = doc.regulatory_deadline or doc.statutory_deadline

	project_name = _generate_project_name(doc)

	project = frappe.get_doc({
		"doctype": "Project",
		"project_name": project_name,
		"status": "Active",
		"customer": doc.customer,
		"expected_start_date": doc.date_received,
		"expected_end_date": expected_end,
		"custom_assignment_origination": doc.name,
		"custom_service_line": doc.service_line,
		"project_type": doc.service_line,
		"custom_risk_rating": doc.risk_rating,
		"custom_engagement_manager": doc.engagement_manager,
		"custom_branch_manager": doc.lead_branch_manager,
		"custom_client_owner": doc.client_owner,
	})

	project.flags.ignore_permissions = True
	project.insert()
	project.submit()

	doc.project_reference = project.name
	doc.project_created = 1
	doc.acceptance_status = "Approved"
	doc.approval_date = today()
	doc.closure_status = "Open"

	frappe.db.set_value(doc.doctype, doc.name, {
		"project_reference": project.name,
		"project_created": 1,
		"acceptance_status": "Approved",
		"approval_date": today(),
		"closure_status": "Open",
	})

	# Generate tasks from template if one is linked
	_generate_tasks_from_template(doc, project.name)

	frappe.msgprint(
		f"Project {project.name} created successfully.",
		alert=True,
	)

	return project.name


def _generate_project_name(doc):
	"""Generate project name: AATL-{year}-{type_code}-{client_code}-{seq}"""
	year = today()[:4]

	type_codes = {
		"Tax Compliance": "TAX",
		"TRA Support": "TRA",
		"Audit Readiness": "AUDREADY",
		"Monthly Bookkeeping": "BOOK",
		"Accounting Reconstruction": "RECON",
		"Advisory": "ADV",
		"ERPNext Implementation": "ERP",
	}
	type_code = type_codes.get(doc.service_line, "GEN")

	# Get client code from customer name (first 5 uppercase chars)
	client_code = "CLIENT"
	if doc.customer:
		customer_name = frappe.db.get_value("Customer", doc.customer, "customer_name") or doc.customer
		client_code = "".join(c for c in customer_name.upper() if c.isalpha())[:5] or "CLIENT"

	# Get next sequence number
	prefix = f"AATL-{year}-{type_code}-{client_code}-"
	existing = frappe.db.sql(
		"""SELECT project_name FROM `tabProject`
		WHERE project_name LIKE %s ORDER BY project_name DESC LIMIT 1""",
		(f"{prefix}%",),
	)
	if existing:
		last_seq = int(existing[0][0].split("-")[-1])
		next_seq = last_seq + 1
	else:
		next_seq = 1

	return f"{prefix}{next_seq:03d}"


def _create_document_requests(doc, project_name):
	"""Auto-create standard Document Request entries when assignment is accepted."""
	# Standard document requests by service line
	standard_docs = {
		"Tax Compliance": [
			"Trial Balance",
			"Draft Financial Statements",
			"Bank Statements",
			"Tax Correspondence",
			"Sales and Purchase Records",
			"Payroll Records",
			"Fixed Asset Register",
		],
		"Audit Readiness": [
			"Trial Balance",
			"Draft Financial Statements",
			"Bank Statements",
			"Bank Reconciliations",
			"Accounts Receivable Schedule",
			"Accounts Payable Schedule",
			"Fixed Asset Register",
			"Tax Returns (Prior Period)",
			"Board Minutes",
			"Management Representation Letter",
		],
		"Monthly Bookkeeping": [
			"Bank Statements",
			"Sales Invoices",
			"Purchase Invoices",
			"Payroll Records",
			"Cash Receipts",
			"Petty Cash Records",
		],
		"Accounting Reconstruction": [
			"Bank Statements",
			"Previous Financial Statements",
			"Tax Returns (Prior Period)",
			"Trial Balance",
			"Supporting Vouchers",
			"Contract Agreements",
		],
		"TRA Support": [
			"TRA Notice",
			"Tax Returns",
			"Supporting Schedules",
			"Bank Statements",
			"Correspondence with TRA",
		],
		"Advisory": [
			"Client Brief/Request",
			"Background Information",
			"Relevant Regulations",
		],
		"ERPNext Implementation": [
			"Current System Data Export",
			"Chart of Accounts",
			"Organizational Structure",
			"Process Documentation",
		],
	}

	docs = standard_docs.get(doc.service_line, [])

	for doc_name in docs:
		drr = frappe.get_doc({
			"doctype": "Document Request Register",
			"document_name": f"{doc.name} - {doc_name}",
			"project": project_name,
			"assignment_origination": doc.name,
			"requested_date": today(),
			"requested_by": doc.client_owner or doc.received_by or frappe.session.user,
			"responsible_person": doc.client_owner,
			"status": "Requested",
		})
		drr.flags.ignore_permissions = True
		drr.insert()

		_notify_document_request(drr)

	frappe.msgprint(
		f"Created {len(docs)} document requests for assignment.",
		alert=True,
	)


def _notify_document_request(drr):
	"""Auto-email the responsible person about the document request."""
	if not drr.responsible_person:
		return
	email = frappe.db.get_value("User", drr.responsible_person, "email")
	if not email:
		return
	frappe.sendmail(
		recipients=[email],
		subject=f"[AIMS] Document Request: {drr.document_name}",
		message=(
			f"<div style='font-family: Arial, sans-serif; max-width: 600px;'>"
			f"<h3>Document Request</h3>"
			f"<p>A document request has been created for project <b>{drr.project}</b>.</p>"
			f"<p><b>Document:</b> {drr.document_name}</p>"
			f"<p>Please upload the requested document at your earliest convenience.</p>"
			f"</div>"
		),
	)


def _generate_tasks_from_template(doc, project_name):
	"""Generate Project Tasks from Alpha Project Template."""
	# Use template from form field, otherwise auto-detect by service line
	template_name = None
	if hasattr(doc, "custom_project_template") and doc.custom_project_template:
		template_name = doc.custom_project_template
	elif doc.service_line:
		template_name = frappe.db.get_value(
			"Alpha Project Template",
			{"project_type": doc.service_line, "is_active": 1},
			"name",
		)

	if not template_name:
		return

	template = frappe.get_doc("Alpha Project Template", template_name)

	if not template.tasks:
		return

	role_to_user_map = _get_role_user_map()

	seq_to_task = {}

	for tmpl_task in template.tasks:
		assigned_user = None
		if tmpl_task.default_owner_role:
			assigned_user = role_to_user_map.get(tmpl_task.default_owner_role)

		task_doc = frappe.get_doc({
			"doctype": "Task",
			"project": project_name,
			"subject": tmpl_task.task_subject,
			"status": "Open",
			"custom_task_sequence": tmpl_task.sequence,
			"custom_expected_hours": tmpl_task.expected_hours,
			"custom_requires_review": tmpl_task.requires_review or 0,
		})

		if tmpl_task.expected_output:
			task_doc.description = tmpl_task.expected_output

		if assigned_user:
			task_doc._assign = frappe.as_json([assigned_user])
			task_doc.custom_assigned_to = assigned_user

		task_doc.flags.ignore_permissions = True
		task_doc.insert()

		seq_to_task[tmpl_task.sequence] = task_doc.name

	# Now set dependency strings (task names instead of sequence numbers)
	for tmpl_task in template.tasks:
		if tmpl_task.depends_on and tmpl_task.sequence in seq_to_task:
			dep_seqs = [s.strip() for s in str(tmpl_task.depends_on).split(",") if s.strip()]
			dep_task_names = [seq_to_task[int(s)] for s in dep_seqs if int(s) in seq_to_task]
			if dep_task_names:
				frappe.db.set_value(
					"Task",
					seq_to_task[tmpl_task.sequence],
					"custom_depends_on_tasks",
					",".join(dep_task_names),
				)

	# Update origination
	frappe.db.set_value(doc.doctype, doc.name, "task_template_applied", template_name)

	frappe.msgprint(
		f"Generated {len(template.tasks)} tasks from template: {template_name}",
		alert=True,
	)


def _get_role_user_map():
	"""Build a map of role -> first active user with that role."""
	roles = [
		"Alpha Engagement Manager",
		"Alpha Branch Manager",
		"Alpha Client Owner",
		"Alpha Reviewer",
		"Alpha Staff",
		"Alpha Tax Officer",
		"Alpha Partner/Director",
		"Alpha Managing Director",
	]
	role_user_map = {}
	for role in roles:
		users = frappe.get_all(
			"Has Role",
			filters={"role": role, "parenttype": "User"},
			fields=["parent"],
			limit=1,
		)
		if users:
			user_email = users[0].parent
			if frappe.db.get_value("User", user_email, "enabled"):
				role_user_map[role] = user_email
	return role_user_map
