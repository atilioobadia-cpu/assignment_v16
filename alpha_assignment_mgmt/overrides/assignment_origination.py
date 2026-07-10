import frappe


def on_update(doc, method):
	if doc.workflow_state != "Approved":
		return

	if doc.project_created:
		return

	project = frappe.get_doc({
		"doctype": "Project",
		"project_name": doc.assignment_title or doc.name,
		"status": "Active",
		"expected_start_date": doc.date_received,
		"expected_end_date": doc.regulatory_deadline,
		"custom_assignment_origination": doc.name,
		"custom_service_line": doc.service_line,
		"custom_risk_rating": doc.risk_rating,
		"custom_engagement_manager": doc.engagement_manager,
		"custom_branch_manager": doc.lead_branch_manager,
		"custom_client_owner": doc.client_owner,
	})

	project.flags.ignore_permissions = True
	project.insert()

	frappe.db.set_value(doc.doctype, doc.name, "project_reference", project.name)
	frappe.db.set_value(doc.doctype, doc.name, "project_created", 1)
