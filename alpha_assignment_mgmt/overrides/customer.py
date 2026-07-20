import frappe


def on_update(doc, method):
	"""Sync Customer field changes to related open Originations."""
	if not frappe.db.exists("DocType", "Alpha Assignment Origination"):
		return

	open_originals = frappe.get_all(
		"Alpha Assignment Origination",
		filters={"customer": doc.name, "project_created": 0},
		pluck="name",
	)

	for o in open_originals:
		orig = frappe.get_doc("Alpha Assignment Origination", o)
		changed = False

		if doc.custom_engagement_manager and orig.engagement_manager != doc.custom_engagement_manager:
			orig.engagement_manager = doc.custom_engagement_manager
			changed = True
		if doc.custom_client_owner and orig.client_owner != doc.custom_client_owner:
			orig.client_owner = doc.custom_client_owner
			changed = True
		if doc.custom_branch_manager and orig.lead_branch_manager != doc.custom_branch_manager:
			orig.lead_branch_manager = doc.custom_branch_manager
			changed = True
		if doc.custom_service_line and orig.service_line != doc.custom_service_line:
			orig.service_line = doc.custom_service_line
			changed = True
		if doc.custom_risk_rating and orig.risk_rating != doc.custom_risk_rating:
			orig.risk_rating = doc.custom_risk_rating
			changed = True
		if doc.custom_sector and orig.sector != doc.custom_sector:
			orig.sector = doc.custom_sector
			changed = True
		if doc.tax_id and orig.tin_reference != doc.tax_id:
			orig.tin_reference = doc.tax_id
			changed = True
		if doc.customer_name and orig.client_focal_person != doc.customer_name:
			orig.client_focal_person = doc.customer_name
			changed = True

		if changed:
			orig.flags.ignore_permissions = True
			orig.flags.ignore_validate = True
			orig.db_update()
