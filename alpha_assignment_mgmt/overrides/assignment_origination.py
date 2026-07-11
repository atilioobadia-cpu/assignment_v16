import frappe
from frappe.utils import today


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
	"""When Origination is submitted AND approved, auto-create Project and Document Requests."""
	if doc.workflow_state != "Approved":
		return

	if doc.project_created:
		return

	# Only auto-create on actual approval (docstatus=1 for submitted docs)
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

	frappe.db.set_value(doc.doctype, doc.name, {
		"project_reference": project.name,
		"project_created": 1,
		"acceptance_status": "Approved",
		"approval_date": today(),
		"closure_status": "Open",
	})

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
		"""SELECT name FROM `tabProject`
		WHERE name LIKE %s ORDER BY name DESC LIMIT 1""",
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

	frappe.msgprint(
		f"Created {len(docs)} document requests for assignment.",
		alert=True,
	)
