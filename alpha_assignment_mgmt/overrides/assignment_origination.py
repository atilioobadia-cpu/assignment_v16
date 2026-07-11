import frappe


@frappe.whitelist()
def create_project_from_origination(origination_name):
	"""API endpoint to create Project from Origination (called from JS button)."""
	doc = frappe.get_doc("Alpha Assignment Origination", origination_name)

	if doc.workflow_state != "Approved":
		frappe.throw("Assignment Origination must be approved before creating a Project.")

	if doc.project_created:
		frappe.throw(f"Project already created: {doc.project_reference}")

	return _create_project(doc)


def on_update(doc, method):
	"""When Origination workflow_state changes to Approved, auto-create Project."""
	if doc.workflow_state != "Approved":
		return

	if doc.project_created:
		return

	_create_project(doc)


def _create_project(doc):
	"""Internal: create Project from Origination and link back."""
	expected_end = doc.regulatory_deadline or doc.statutory_deadline

	project = frappe.get_doc({
		"doctype": "Project",
		"project_name": doc.assignment_title or doc.name,
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

	frappe.db.set_value(doc.doctype, doc.name, {
		"project_reference": project.name,
		"project_created": 1,
		"acceptance_status": "Approved",
		"approval_date": frappe.utils.today(),
		"closure_status": "Open",
	})

	frappe.msgprint(
		f"Project {project.name} created successfully.",
		alert=True,
	)

	return project.name
