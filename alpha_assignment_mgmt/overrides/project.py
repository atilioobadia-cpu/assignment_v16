import frappe


def before_insert(doc, method):
	"""Auto-populate Project from linked Assignment Origination."""
	if doc.custom_assignment_origination:
		origination = frappe.get_doc(
			"Alpha Assignment Origination", doc.custom_assignment_origination
		)
		if origination.workflow_state != "Approved":
			frappe.throw(
				f"Cannot create Project. Assignment Origination "
				f"{origination.name} has not been approved yet."
			)

		doc.customer = origination.customer or doc.customer
		doc.custom_service_line = origination.service_line
		doc.project_type = origination.service_line
		doc.custom_branch_manager = origination.lead_branch_manager
		doc.custom_engagement_manager = origination.engagement_manager
		doc.custom_client_owner = doc.custom_client_owner or origination.client_owner
		doc.custom_risk_rating = origination.risk_rating

		if not doc.expected_end_date:
			doc.expected_end_date = (
				origination.regulatory_deadline
				or origination.statutory_deadline
			)


def validate(doc, method):
	"""Validate project fields."""
	pass


def on_update(doc, method):
	"""Create SLA for new projects, update origination, check closure."""
	old_doc = doc.get_doc_before_save()
	is_new = old_doc is None

	if is_new and doc.custom_assignment_origination and not doc.custom_engagement_sla:
		create_sla(doc)

	update_origination_status(doc, is_new)
	check_project_closure(doc)


def create_sla(doc):
	"""Auto-create Engagement SLA when Project Type is set."""
	if not doc.project_type:
		return

	sla_level_map = {
		"Tax Compliance": "SLA A - Urgent Statutory",
		"TRA Support": "SLA A - Urgent Statutory",
		"Audit Readiness": "SLA B - Audit Readiness",
		"Monthly Bookkeeping": "SLA C - Monthly Bookkeeping",
		"Accounting Reconstruction": "SLA D - Reconstruction",
		"Advisory": "SLA E - Advisory/Research/Training",
		"ERPNext Implementation": "SLA E - Advisory/Research/Training",
	}

	origination = None
	if doc.custom_assignment_origination:
		origination = frappe.get_doc(
			"Alpha Assignment Origination", doc.custom_assignment_origination
		)

	deadline = doc.expected_end_date
	if origination:
		deadline = (
			origination.regulatory_deadline
			or origination.statutory_deadline
			or doc.expected_end_date
		)

	if not deadline:
		from frappe.utils import add_days
		deadline = add_days(doc.expected_start_date or frappe.utils.today(), 30)

	sla = frappe.new_doc("Alpha Engagement SLA")
	sla.project = doc.name
	sla.customer = doc.customer
	sla.assignment_origination = doc.custom_assignment_origination
	sla.sla_level = sla_level_map.get(doc.project_type, "SLA C - Monthly Bookkeeping")
	sla.engagement_manager = doc.custom_engagement_manager
	sla.branch_manager = doc.custom_branch_manager
	sla.alpha_processing_deadline = deadline
	sla.client_due_date = deadline
	sla.insert(ignore_permissions=True)
	sla.submit()

	doc.db_set("custom_engagement_sla", sla.name)

	# Back-link SLA to Origination
	if doc.custom_assignment_origination:
		frappe.db.set_value(
			"Alpha Assignment Origination",
			doc.custom_assignment_origination,
			"sla_reference",
			sla.name,
		)


def update_origination_status(doc, is_new):
	"""Update Assignment Origination when Project is created."""
	if is_new and doc.custom_assignment_origination:
		frappe.db.set_value("Alpha Assignment Origination", doc.custom_assignment_origination, {
			"project_created": 1,
			"project_reference": doc.name,
			"workflow_state": "Project Created",
			"acceptance_status": "Approved",
			"closure_status": "In Progress",
		})


def check_project_closure(doc):
	"""Prevent closing Project without Closure Certificate."""
	if doc.status == "Completed" and not doc.custom_closure_certificate:
		frappe.throw(
			"Cannot close Project. Assignment Closure Certificate is required."
		)
