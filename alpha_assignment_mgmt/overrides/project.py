import frappe


def before_insert(doc, method):
	"""Ensure Assignment Origination is approved before Project creation."""
	if doc.custom_assignment_origination:
		origination = frappe.get_doc(
			"Alpha Assignment Origination", doc.custom_assignment_origination
		)
		if origination.workflow_state != "Approved":
			frappe.throw(
				f"Cannot create Project. Assignment Origination "
				f"{origination.name} has not been approved yet."
			)
		doc.custom_service_line = origination.service_line
		doc.custom_branch_manager = origination.lead_branch_manager
		doc.custom_engagement_manager = origination.engagement_manager
		doc.custom_client_owner = origination.client_owner
		doc.custom_risk_rating = origination.risk_rating


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

	sla = frappe.new_doc("Alpha Engagement SLA")
	sla.project = doc.name
	sla.customer = doc.customer
	sla.assignment_origination = doc.custom_assignment_origination
	sla.sla_level = sla_level_map.get(doc.project_type, "SLA C - Monthly Bookkeeping")
	sla.engagement_manager = doc.custom_engagement_manager
	sla.branch_manager = doc.custom_branch_manager
	sla.alpha_processing_deadline = doc.expected_start_date
	sla.insert(ignore_permissions=True)
	sla.submit()

	doc.db_set("custom_engagement_sla", sla.name)


def update_origination_status(doc, is_new):
	"""Update Assignment Origination when Project is created."""
	if is_new and doc.custom_assignment_origination:
		frappe.db.set_value("Alpha Assignment Origination", doc.custom_assignment_origination, {
			"project_created": 1,
			"project_reference": doc.name,
			"workflow_state": "Project Created",
		})


def check_project_closure(doc):
	"""Prevent closing Project without Closure Certificate."""
	if doc.status == "Completed" and not doc.custom_closure_certificate:
		frappe.throw(
			"Cannot close Project. Assignment Closure Certificate is required."
		)
