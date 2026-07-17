import frappe
import json
import os


def after_install():
	"""Set up roles, workflows, templates, dashboards and workspaces after app install."""
	create_roles()
	create_workflow_states()
	create_naming_series()
	create_project_types()
	create_activity_types()
	create_project_templates()
	_create_assignment_number_cards()
	_create_assignment_dashboard_charts()
	_create_task_number_cards()
	_create_task_dashboard_charts()
	_create_custom_html_block()
	_setup_ceo_workspace()
	_setup_aims_desk_workspace()
	_create_ceo_api_method()
	_clear_number_card_currencies()
	frappe.db.commit()


def after_migrate():
	"""Re-sync components after migration."""
	create_workflow_states()
	create_project_templates()
	_create_task_number_cards()
	_create_task_dashboard_charts()
	_create_custom_html_block()
	_setup_ceo_workspace()
	_setup_aims_desk_workspace()
	_clear_number_card_currencies()
	frappe.db.commit()


def create_roles():
	roles = [
		"Alpha Partner/Director",
		"Alpha Engagement Manager",
		"Alpha Branch Manager",
		"Alpha Client Owner",
		"Alpha Reviewer",
		"Alpha Staff",
		"Alpha HR Admin",
		"Alpha Tax Officer",
		"Alpha Managing Director",
	]
	for role in roles:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role}).insert(
				ignore_permissions=True
			)


def create_workflow_states():
	"""Create Workflow State records used by the Alpha Assignment Origination Workflow."""
	states = [
		{"state": "Draft", "doc_status": "0", "allow_edit": "Alpha Tax Officer"},
		{"state": "Submitted", "doc_status": "1", "allow_edit": "Alpha Engagement Manager"},
		{"state": "Under Review", "doc_status": "1", "allow_edit": "Alpha Branch Manager"},
		{"state": "Approved", "doc_status": "1", "allow_edit": "Alpha Managing Director"},
		{"state": "Rejected", "doc_status": "1", "allow_edit": "System Manager"},
		{"state": "Project Created", "doc_status": "1", "allow_edit": "Alpha Engagement Manager"},
		{"state": "Closed", "doc_status": "1", "allow_edit": "System Manager"},
	]
	for state in states:
		if not frappe.db.exists("Workflow State", state["state"]):
			frappe.get_doc({
				"doctype": "Workflow State",
				"workflow_state_name": state["state"],
			}).insert(ignore_permissions=True)


def create_naming_series():
	"""Set naming series via Property Setter."""
	series_map = {
		"Alpha Assignment Origination": "AOR-.YYYY.-.#####",
		"Alpha Engagement SLA": "AATL-SLA-.YYYY.-.#####",
	}
	for doctype, series in series_map.items():
		try:
			exists = frappe.db.get_value(
				"Property Setter",
				{"doc_type": doctype, "property": "naming_series"},
			)
			if not exists:
				frappe.get_doc({
					"doctype": "Property Setter",
					"doctype_or_field": "DocType",
					"doc_type": doctype,
					"property": "naming_series",
					"property_type": "Data",
					"value": series,
					"__islocal": 1,
				}).insert(ignore_permissions=True)
		except Exception:
			pass


def create_project_types():
	project_types = [
		"Tax Compliance",
		"TRA Support",
		"Audit Readiness",
		"Monthly Bookkeeping",
		"Accounting Reconstruction",
		"Advisory",
		"ERPNext Implementation",
	]
	for name in project_types:
		if not frappe.db.exists("Project Type", name):
			frappe.get_doc({"doctype": "Project Type", "project_type": name}).insert(
				ignore_permissions=True
			)


def create_activity_types():
	activity_types = [
		"Tax Preparation",
		"Tax Review",
		"Tax Filing",
		"Audit Fieldwork",
		"Audit Review",
		"Bookkeeping Entry",
		"Bookkeeping Review",
		"Reconciliation",
		"Advisory Call",
		"Advisory Report",
		"ERPNext Setup",
		"ERPNext Training",
		"Client Communication",
		"Internal Meeting",
		"Training/CPD",
		"Administrative",
	]
	for name in activity_types:
		if not frappe.db.exists("Activity Type", name):
			frappe.get_doc({"doctype": "Activity Type", "activity_type": name}).insert(
				ignore_permissions=True
			)


def create_project_templates():
	"""Create standard project templates from the requirements document."""
	templates = _get_template_definitions()
	for tmpl_def in templates:
		if frappe.db.exists("Alpha Project Template", tmpl_def["template_name"]):
			continue
		doc = frappe.get_doc({
			"doctype": "Alpha Project Template",
			"template_name": tmpl_def["template_name"],
			"project_type": tmpl_def["project_type"],
			"service_line": tmpl_def.get("service_line", ""),
			"description": tmpl_def.get("description", ""),
			"is_active": 1,
			"tasks": tmpl_def["tasks"],
		})
		doc.flags.ignore_permissions = True
		doc.insert()


def _get_template_definitions():
	return [
		{
			"template_name": "Tax Compliance Filing",
			"project_type": "Tax Compliance",
			"service_line": "Tax Compliance",
			"description": "Standard task sequence for tax return filing per Appendix B",
			"tasks": [
				{"task_subject": "Receive trial balance, draft financial statements and tax records", "sequence": 1, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Engagement Manager", "expected_output": "Engagement Manager confirms completeness"},
				{"task_subject": "Confirm tax period, IDRAS deadline and extension status", "sequence": 2, "expected_hours": 0.5, "requires_review": 0, "default_owner_role": "Alpha Tax Officer", "depends_on": "1", "expected_output": "Tax Officer and Reviewer confirm"},
				{"task_subject": "Review revenue, expenses and disallowable items", "sequence": 3, "expected_hours": 4, "requires_review": 1, "default_owner_role": "Alpha Tax Officer", "depends_on": "2", "expected_output": "Tax Reviewer checks computation basis"},
				{"task_subject": "Review capital allowances and fixed asset additions/disposals", "sequence": 4, "expected_hours": 3, "requires_review": 1, "default_owner_role": "Alpha Tax Officer", "depends_on": "2", "expected_output": "Reviewer approves asset schedule"},
				{"task_subject": "Review WHT, PAYE, SDL, VAT and other statutory exposure", "sequence": 5, "expected_hours": 3, "requires_review": 1, "default_owner_role": "Alpha Tax Officer", "depends_on": "2", "expected_output": "Tax Reviewer checks reconciliation"},
				{"task_subject": "Prepare income tax computation", "sequence": 6, "expected_hours": 4, "requires_review": 1, "default_owner_role": "Alpha Tax Officer", "depends_on": "3,4,5", "expected_output": "Internal tax review mandatory"},
				{"task_subject": "Obtain client approval and management representation", "sequence": 7, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "6", "expected_output": "Client approval required before filing"},
				{"task_subject": "File through IDRAS and save filing evidence", "sequence": 8, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Tax Officer", "depends_on": "7", "expected_output": "Filing evidence attached"},
				{"task_subject": "Prepare payment advice or filing confirmation note", "sequence": 9, "expected_hours": 0.5, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "8", "expected_output": "Engagement Manager signs off"},
				{"task_subject": "Close assignment and update client tax calendar", "sequence": 10, "expected_hours": 0.5, "requires_review": 0, "default_owner_role": "Alpha Engagement Manager", "depends_on": "9", "expected_output": "Closure certificate submitted"},
			],
		},
		{
			"template_name": "Audit Readiness Support",
			"project_type": "Audit Readiness",
			"service_line": "Audit & Assurance",
			"description": "Standard 16-task sequence for audit readiness and management pack per Appendix B",
			"tasks": [
				{"task_subject": "Engagement confirmation and kickoff", "sequence": 1, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Engagement Manager", "expected_output": "Approved scope, team and deadline"},
				{"task_subject": "Document request issued (PBC list)", "sequence": 2, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "1", "expected_output": "PBC/document request register"},
				{"task_subject": "Data Inventory Register completed", "sequence": 3, "expected_hours": 2, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "2", "expected_output": "DIR by department and evidence status"},
				{"task_subject": "Opening balance review", "sequence": 4, "expected_hours": 3, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "3", "expected_output": "Opening balance validation schedule"},
				{"task_subject": "Bank reconciliation", "sequence": 5, "expected_hours": 4, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "3", "expected_output": "Bank reconciliation and unreconciled items"},
				{"task_subject": "Sales and revenue validation", "sequence": 6, "expected_hours": 3, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "3", "expected_output": "Revenue support and sales reconciliation"},
				{"task_subject": "Purchases, suppliers and liabilities review", "sequence": 7, "expected_hours": 3, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "3", "expected_output": "Supplier schedule and liability classification"},
				{"task_subject": "Fixed assets and depreciation review", "sequence": 8, "expected_hours": 2, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "3", "expected_output": "Asset register and depreciation workings"},
				{"task_subject": "Tax schedules review", "sequence": 9, "expected_hours": 2, "requires_review": 1, "default_owner_role": "Alpha Tax Officer", "depends_on": "3", "expected_output": "VAT, PAYE, WHT, SDL, income tax support"},
				{"task_subject": "Adjusting journals", "sequence": 10, "expected_hours": 2, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "4,5,6,7,8,9", "expected_output": "AJE register and supporting evidence"},
				{"task_subject": "Draft management accounts", "sequence": 11, "expected_hours": 4, "requires_review": 1, "default_owner_role": "Alpha Engagement Manager", "depends_on": "10", "expected_output": "Draft financial statements and notes"},
				{"task_subject": "Technical review", "sequence": 12, "expected_hours": 3, "requires_review": 1, "default_owner_role": "Alpha Reviewer", "depends_on": "11", "expected_output": "Review comments and clearance"},
				{"task_subject": "Client query clearance", "sequence": 13, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "12", "expected_output": "Client responses and representation points"},
				{"task_subject": "Auditor handover pack", "sequence": 14, "expected_hours": 2, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "12,13", "expected_output": "Audit-ready schedules and evidence index"},
				{"task_subject": "Tax return support", "sequence": 15, "expected_hours": 2, "requires_review": 1, "default_owner_role": "Alpha Tax Officer", "depends_on": "10", "expected_output": "Tax computation and filing pack"},
				{"task_subject": "Assignment closure", "sequence": 16, "expected_hours": 0.5, "requires_review": 0, "default_owner_role": "Alpha Engagement Manager", "depends_on": "14,15", "expected_output": "Closure certificate and archive confirmation"},
			],
		},
		{
			"template_name": "Monthly Bookkeeping",
			"project_type": "Monthly Bookkeeping",
			"service_line": "Bookkeeping",
			"description": "Standard 10-task sequence for monthly bookkeeping per Appendix C",
			"tasks": [
				{"task_subject": "Monthly document request issued", "sequence": 1, "expected_hours": 0.5, "requires_review": 0, "default_owner_role": "Alpha Staff", "expected_output": "PBC checklist sent"},
				{"task_subject": "Documents received and indexed", "sequence": 2, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "1", "expected_output": "Document Request Register updated"},
				{"task_subject": "Bank, sales, purchases and payroll records checked", "sequence": 3, "expected_hours": 2, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "2", "expected_output": "Posting readiness status"},
				{"task_subject": "ERPNext posting completed using approved accounts and cost centres", "sequence": 4, "expected_hours": 4, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "3", "expected_output": "Posting log and references"},
				{"task_subject": "Bank, tax, receivable and payable reconciliations prepared", "sequence": 5, "expected_hours": 3, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "4", "expected_output": "Reconciliation pack"},
				{"task_subject": "Reviewer checks postings and reconciliations", "sequence": 6, "expected_hours": 2, "requires_review": 1, "default_owner_role": "Alpha Reviewer", "depends_on": "5", "expected_output": "Review Gate cleared"},
				{"task_subject": "Monthly close pack prepared", "sequence": 7, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "6", "expected_output": "Client monthly report"},
				{"task_subject": "Tax readiness and filing support prepared", "sequence": 8, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Tax Officer", "depends_on": "4", "expected_output": "VAT/PAYE/WHT support where applicable"},
				{"task_subject": "Client queries issued and followed up", "sequence": 9, "expected_hours": 0.5, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "6", "expected_output": "Client Delay Log if unresolved"},
				{"task_subject": "Monthly assignment closed and billed", "sequence": 10, "expected_hours": 0.5, "requires_review": 0, "default_owner_role": "Alpha Engagement Manager", "depends_on": "7,8", "expected_output": "Closure and invoice status"},
			],
		},
		{
			"template_name": "Accounting Reconstruction",
			"project_type": "Accounting Reconstruction",
			"service_line": "Accounting Reconstruction",
			"description": "Standard task sequence for historical accounting reconstruction",
			"tasks": [
				{"task_subject": "Engagement confirmation and scope definition", "sequence": 1, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Engagement Manager", "expected_output": "Approved scope, period and team"},
				{"task_subject": "Document request issued for historical records", "sequence": 2, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "1", "expected_output": "PBC register for reconstruction period"},
				{"task_subject": "Source documents received and indexed", "sequence": 3, "expected_hours": 2, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "2", "expected_output": "Document Register updated"},
				{"task_subject": "Opening balances established and validated", "sequence": 4, "expected_hours": 3, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "3", "expected_output": "Opening balance schedule"},
				{"task_subject": "Bank statements reconciled for reconstruction period", "sequence": 5, "expected_hours": 4, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "3", "expected_output": "Bank reconciliation for each period"},
				{"task_subject": "Sales and revenue reconstructed from source documents", "sequence": 6, "expected_hours": 4, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "3,4", "expected_output": "Revenue reconstruction schedule"},
				{"task_subject": "Purchases and expenses reconstructed", "sequence": 7, "expected_hours": 4, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "3,4", "expected_output": "Expense reconstruction schedule"},
				{"task_subject": "Fixed assets and depreciation recomputed", "sequence": 8, "expected_hours": 3, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "3,4", "expected_output": "Asset register and depreciation workings"},
				{"task_subject": "Tax computations reconstructed", "sequence": 9, "expected_hours": 3, "requires_review": 1, "default_owner_role": "Alpha Tax Officer", "depends_on": "6,7,8", "expected_output": "Tax computation per period"},
				{"task_subject": "Financial statements drafted for each period", "sequence": 10, "expected_hours": 4, "requires_review": 1, "default_owner_role": "Alpha Engagement Manager", "depends_on": "5,6,7,8,9", "expected_output": "Draft financial statements per period"},
				{"task_subject": "Technical review of reconstructed statements", "sequence": 11, "expected_hours": 3, "requires_review": 1, "default_owner_role": "Alpha Reviewer", "depends_on": "10", "expected_output": "Review comments and clearance"},
				{"task_subject": "Assignment closure", "sequence": 12, "expected_hours": 0.5, "requires_review": 0, "default_owner_role": "Alpha Engagement Manager", "depends_on": "11", "expected_output": "Closure certificate submitted"},
			],
		},
		{
			"template_name": "TRA Support",
			"project_type": "TRA Support",
			"service_line": "TRA Support",
			"description": "Task sequence for TRA notice and audit support",
			"tasks": [
				{"task_subject": "Receive and review TRA notice", "sequence": 1, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Tax Officer", "expected_output": "Notice details documented"},
				{"task_subject": "Gather supporting documents from client", "sequence": 2, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "1", "expected_output": "Document Register updated"},
				{"task_subject": "Review tax computations for queried period", "sequence": 3, "expected_hours": 3, "requires_review": 1, "default_owner_role": "Alpha Tax Officer", "depends_on": "2", "expected_output": "Review notes and findings"},
				{"task_subject": "Prepare response and supporting schedules", "sequence": 4, "expected_hours": 3, "requires_review": 1, "default_owner_role": "Alpha Tax Officer", "depends_on": "3", "expected_output": "Draft response with schedules"},
				{"task_subject": "Technical review of response", "sequence": 5, "expected_hours": 2, "requires_review": 1, "default_owner_role": "Alpha Reviewer", "depends_on": "4", "expected_output": "Review clearance"},
				{"task_subject": "File response with TRA and save evidence", "sequence": 6, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Tax Officer", "depends_on": "5", "expected_output": "Filing evidence attached"},
				{"task_subject": "Assignment closure", "sequence": 7, "expected_hours": 0.5, "requires_review": 0, "default_owner_role": "Alpha Engagement Manager", "depends_on": "6", "expected_output": "Closure certificate submitted"},
			],
		},
	]


# ── Assignment-related charts & cards (AIMS Desk originals) ──────────────

def _create_assignment_dashboard_charts():
	charts = [
		{
			"chart_name": "Assignments Trend (Last 12 Months)",
			"chart_type": "Count",
			"document_type": "Alpha Assignment Origination",
			"based_on": "creation",
			"type": "Line",
			"timespan": "Last Year",
			"timeseries_based_on": "creation",
			"time_interval": "Monthly",
			"filters_json": "[]",
		},
	]
	for chart in charts:
		if not frappe.db.exists("Dashboard Chart", chart["chart_name"]):
			frappe.get_doc({
				"doctype": "Dashboard Chart",
				**chart,
			}).insert(ignore_permissions=True)


def _create_assignment_number_cards():
	cards = [
		{
			"label": "Active Assignments",
			"type": "Document Type",
			"document_type": "Alpha Assignment Origination",
			"function": "Count",
			"filters_json": '[]',
		},
		{
			"label": "Active Projects",
			"type": "Document Type",
			"document_type": "Project",
			"function": "Count",
			"filters_json": '[["Project","status","=","Completed"]]',
		},
		{
			"label": "Pending Reviews",
			"type": "Document Type",
			"document_type": "Review Gate Register",
			"function": "Count",
			"filters_json": '[["Review Gate Register","docstatus","=",0]]',
		},
		{
			"label": "Pending Projects",
			"type": "Document Type",
			"document_type": "Project",
			"function": "Count",
			"filters_json": '[["Project","status","=","Open"]]',
		},
		{
			"label": "Active Staff",
			"type": "Document Type",
			"document_type": "Employee",
			"function": "Count",
			"filters_json": '[["Employee","status","=","Active"]]',
		},
		{
			"label": "Active Clients",
			"type": "Document Type",
			"document_type": "Customer",
			"function": "Count",
			"filters_json": '[["Customer","disabled","=",0]]',
		},
	]
	for card in cards:
		if not frappe.db.exists("Number Card", card["label"]):
			frappe.get_doc({
				"doctype": "Number Card",
				**card,
			}).insert(ignore_permissions=True)
		else:
			frappe.db.set_value("Number Card", card["label"], {"is_public": 1})


# ── Task-performance cards & charts (CEO dashboard) ─────────────────────

def _create_task_number_cards():
	cards = [
		{
			"label": "Tasks Completed",
			"filters": '[["Task","status","=","Completed"]]',
			"color": "#28a745",
		},
		{
			"label": "Tasks Pending",
			"filters": '[["Task","status","in",["Open","Working","Overdue"]]]',
			"color": "#ff6b6b",
		},
	]
	for c in cards:
		if frappe.db.exists("Number Card", c["label"]):
			frappe.db.set_value("Number Card", c["label"], {
				"document_type": "Task",
				"function": "Count",
				"type": "Document Type",
				"is_standard": 0,
				"is_public": 1,
				"filters_json": c["filters"],
				"show_percentage_stats": 1,
				"stats_time_interval": "Daily",
				"color": c["color"],
				"currency": "",
				"module": "Alpha Assignment Management",
			})
		else:
			doc = frappe.get_doc({
				"doctype": "Number Card",
				"label": c["label"],
				"document_type": "Task",
				"function": "Count",
				"type": "Document Type",
				"is_public": 1,
				"is_standard": 0,
				"module": "Alpha Assignment Management",
				"filters_json": c["filters"],
				"show_percentage_stats": 1,
				"stats_time_interval": "Daily",
				"color": c["color"],
				"currency": "",
			})
			doc.insert(ignore_permissions=True)

	# Also clear currency on Active Staff / Active Clients so they show numbers not TZS
	for name in ["Active Staff", "Active Clients"]:
		if frappe.db.exists("Number Card", name):
			frappe.db.set_value("Number Card", name, {"currency": ""})


def _clear_number_card_currencies():
	"""Clear currency on all count-based Number Cards that should show whole numbers, not TZS.

	Workspace sync creates Number Cards with the company's default currency (TZS).
	We need to run this AFTER workspace sync to override that default.
	"""
	count_cards = [
		"Tasks Completed", "Tasks Pending",
		"Active Staff", "Active Clients",
		"Active Assignments", "Active Projects",
	]
	for name in count_cards:
		if frappe.db.exists("Number Card", name):
			frappe.db.set_value("Number Card", name, {"currency": ""})


def _create_task_dashboard_charts():
	charts = [
		{
			"name": "Employee Performance Trend",
			"chart_type": "Count",
			"document_type": "Task",
			"based_on": "completed_on",
			"type": "Line",
			"filters": '[["Task","status","=","Completed"]]',
			"timeseries": 1,
			"time_interval": "Monthly",
			"custom_options": json.dumps({"colors": ["#5e64ff"]}),
		},
		{
			"name": "Tasks by Status",
			"chart_type": "Group By",
			"document_type": "Task",
			"group_by_based_on": "status",
			"type": "Pie",
			"filters": "[]",
			"custom_options": json.dumps({"colors": ["#5e64ff", "#28a745", "#ff6b6b", "#ffa726", "#42a5f5"]}),
		},
		{
			"name": "Tasks Completed Over Time",
			"chart_type": "Count",
			"document_type": "Task",
			"based_on": "completed_on",
			"type": "Bar",
			"filters": '[["Task","status","=","Completed"]]',
			"timeseries": 1,
			"time_interval": "Monthly",
			"custom_options": json.dumps({"colors": ["#28a745"]}),
		},
		{
			"name": "Open Tasks by Project",
			"chart_type": "Group By",
			"document_type": "Task",
			"group_by_based_on": "project",
			"type": "Bar",
			"filters": '[["Task","status","in",["Open","Working","Overdue"]]]',
			"custom_options": json.dumps({"colors": ["#ffa726", "#5e64ff", "#ff6b6b", "#28a745"]}),
		},
		{
			"name": "Task Priority Distribution",
			"chart_type": "Group By",
			"document_type": "Task",
			"group_by_based_on": "priority",
			"type": "Bar",
			"filters": "[]",
			"custom_options": json.dumps({"colors": ["#ff6b6b", "#ffa726", "#5e64ff", "#28a745"]}),
		},
	]

	for ch in charts:
		if frappe.db.exists("Dashboard Chart", ch["name"]):
			vals = {
				"chart_type": ch["chart_type"],
				"document_type": ch["document_type"],
				"type": ch["type"],
				"filters_json": ch["filters"],
				"custom_options": ch.get("custom_options"),
				"is_standard": 0,
				"is_public": 1,
				"module": "Alpha Assignment Management",
				"timeseries": ch.get("timeseries", 0),
				"chart_name": ch["name"],
			}
			if ch.get("based_on"):
				vals["based_on"] = ch["based_on"]
			if ch.get("group_by_based_on"):
				vals["group_by_based_on"] = ch["group_by_based_on"]
			if ch.get("time_interval"):
				vals["time_interval"] = ch["time_interval"]
			frappe.db.set_value("Dashboard Chart", ch["name"], vals)
		else:
			doc = frappe.new_doc("Dashboard Chart")
			for k, v in ch.items():
				if k == "filters":
					k = "filters_json"
				setattr(doc, k, v)
			doc.chart_name = ch["name"]
			doc.is_standard = 0
			doc.is_public = 1
			doc.module = "Alpha Assignment Management"
			doc.insert(ignore_permissions=True)


# ── Custom HTML Block ────────────────────────────────────────────────────

def _create_custom_html_block():
	html = """<div id="ceo-top-bottom" style="padding: 10px;">
<h5 style="margin-bottom: 15px;"><b>Employee Task Performance</b></h5>
<div class="row">
    <div class="col-md-6">
        <div style="border-left: 4px solid #28a745; padding: 15px; background: #f8f9fa; border-radius: 4px;">
            <h6 style="color: #28a745; font-weight: bold; margin-bottom: 10px;">Top 5 - Most Completed Tasks</h6>
            <div id="top-5-list"><p class="text-muted">Loading...</p></div>
        </div>
    </div>
    <div class="col-md-6">
        <div style="border-left: 4px solid #dc3545; padding: 15px; background: #f8f9fa; border-radius: 4px;">
            <h6 style="color: #dc3545; font-weight: bold; margin-bottom: 10px;">Bottom 5 - Needs Attention</h6>
            <p style="font-size:11px;color:#999;margin-bottom:8px;">Employees with fewer completed tasks</p>
            <div id="bottom-5-list"><p class="text-muted">Loading...</p></div>
        </div>
    </div>
</div>
</div>"""

	script = """frappe.ready(function() {
    var topList = root_element.querySelector('#top-5-list');
    var bottomList = root_element.querySelector('#bottom-5-list');

    frappe.call({
        method: 'alpha_assignment_mgmt.alpha_assignment_management.api.ceo_dashboard.get_ceo_top_bottom',
        callback: function(r) {
            if (!r.message) return;
            var data = r.message;
            renderList(topList, data.top5, true);
            renderList(bottomList, data.bottom5, false);
        },
        error: function() {
            if (topList) topList.innerHTML = '<p class="text-muted">Error loading data</p>';
            if (bottomList) bottomList.innerHTML = '<p class="text-muted">Error loading data</p>';
        }
    });

    function renderList(container, items, isTop) {
        if (!container) return;
        if (!items || !items.length) {
            container.innerHTML = '<p class="text-muted">No data</p>';
            return;
        }
        var html = '<table class="table table-sm table-borderless mb-0">';
        html += '<tr style="font-weight:bold;color:#666;font-size:12px;"><td style="width:30px">#</td><td>Employee</td><td style="width:80px;text-align:center;">Completed</td><td style="width:80px;text-align:center;">Pending</td></tr>';
        items.forEach(function(item, i) {
            var rank = i + 1;
            var medal = '';
            if (isTop && rank === 1) medal = ' \\ud83e\\udd47';
            else if (isTop && rank === 2) medal = ' \\ud83e\\udd48';
            else if (isTop && rank === 3) medal = ' \\ud83e\\udd49';
            var completedBadge = item.completed > 0
                ? '<span class="badge" style="background:#28a745;color:#fff;font-size:12px;">' + item.completed + '</span>'
                : '<span class="badge" style="background:#6c757d;color:#fff;font-size:12px;">0</span>';
            var pendingBadge = item.pending > 0
                ? '<span class="badge" style="background:#dc3545;color:#fff;font-size:12px;">' + item.pending + '</span>'
                : '<span class="badge" style="background:#28a745;color:#fff;font-size:12px;">0</span>';
            html += '<tr><td><b>' + rank + '</b></td><td>' + item.name + medal + '</td><td style="text-align:center;">' + completedBadge + '</td><td style="text-align:center;">' + pendingBadge + '</td></tr>';
        });
        html += '</table>';
        container.innerHTML = html;
    }
});"""

	block_name = "CEO Top Bottom Employees"
	if frappe.db.exists("Custom HTML Block", block_name):
		frappe.db.set_value("Custom HTML Block", block_name, {
			"html": html, "script": script, "private": 0,
		})
	else:
		doc = frappe.new_doc("Custom HTML Block")
		doc.name = block_name
		doc.html = html
		doc.script = script
		doc.private = 0
		doc.insert(ignore_permissions=True)


# ── CEO API method ───────────────────────────────────────────────────────

def _create_ceo_api_method():
	"""Ensure the CEO dashboard API method file exists."""
	api_dir = os.path.join(
		os.path.dirname(__file__),
		"alpha_assignment_management",
		"api",
	)
	os.makedirs(api_dir, exist_ok=True)

	init_file = os.path.join(api_dir, "__init__.py")
	if not os.path.exists(init_file):
		with open(init_file, "w") as f:
			f.write("")

	api_file = os.path.join(api_dir, "ceo_dashboard.py")
	if not os.path.exists(api_file):
		with open(api_file, "w") as f:
			f.write("""import frappe


@frappe.whitelist()
def get_ceo_top_bottom():
    employees = frappe.get_all(
        "Employee",
        filters={"status": "Active", "user_id": ["is", "set"]},
        fields=["name", "employee_name", "user_id"],
    )
    if not employees:
        return {"top5": [], "bottom5": []}

    results = []
    for emp in employees:
        uid = emp.user_id
        completed = frappe.db.sql(\"\\"\\"\"\"
            SELECT COUNT(DISTINCT t.name)
            FROM tabTask t
            WHERE t.status = 'Completed'
            AND (JSON_CONTAINS(t._assign, %s) OR t.owner = %s)
        \"\"\\"\\"\"\", (frappe.json.dumps(uid), uid))[0][0]

        pending = frappe.db.sql(\"\\"\\"\"\"
            SELECT COUNT(DISTINCT t.name)
            FROM tabTask t
            WHERE t.status IN ('Open', 'Working', 'Overdue')
            AND (JSON_CONTAINS(t._assign, %s) OR t.owner = %s)
        \"\"\\"\\"\"\", (frappe.json.dumps(uid), uid))[0][0]

        results.append({
            "name": emp.employee_name or emp.name,
            "completed": completed,
            "pending": pending,
        })

    results.sort(key=lambda x: x["completed"], reverse=True)
    return {
        "top5": results[:5],
        "bottom5": list(reversed(results[-5:])) if len(results) >= 5 else list(reversed(results)),
    }
""")


# ── Workspace setup ──────────────────────────────────────────────────────

def _insert_workspace_charts(ws_name, chart_names):
	frappe.db.sql(
		"DELETE FROM `tabWorkspace Chart` WHERE parent = %s AND parenttype = 'Workspace'",
		ws_name,
	)
	for idx, cname in enumerate(chart_names):
		if frappe.db.exists("Dashboard Chart", cname):
			frappe.db.sql("""
				INSERT INTO `tabWorkspace Chart`
				(name, chart_name, label, parent, parentfield, parenttype, idx, docstatus, creation, modified, owner, modified_by)
				VALUES (%s, %s, %s, %s, 'charts', 'Workspace', %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
			""", (f"{ws_name}_c{idx}", cname, cname, ws_name, idx))


def _insert_workspace_number_cards(ws_name, card_names):
	frappe.db.sql(
		"DELETE FROM `tabWorkspace Number Card` WHERE parent = %s AND parenttype = 'Workspace'",
		ws_name,
	)
	for idx, cname in enumerate(card_names):
		if frappe.db.exists("Number Card", cname):
			frappe.db.sql("""
				INSERT INTO `tabWorkspace Number Card`
				(name, number_card_name, label, parent, parentfield, parenttype, idx, docstatus, creation, modified, owner, modified_by)
				VALUES (%s, %s, %s, %s, 'number_cards', 'Workspace', %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
			""", (f"{ws_name}_nc{idx}", cname, cname, ws_name, idx))


def _insert_workspace_custom_blocks(ws_name, block_names):
	frappe.db.sql(
		"DELETE FROM `tabWorkspace Custom Block` WHERE parent = %s AND parenttype = 'Workspace'",
		ws_name,
	)
	for idx, bname in enumerate(block_names):
		if frappe.db.exists("Custom HTML Block", bname):
			frappe.db.sql("""
				INSERT INTO `tabWorkspace Custom Block`
				(name, custom_block_name, label, parent, parentfield, parenttype, idx, docstatus, creation, modified, owner, modified_by)
				VALUES (%s, %s, %s, %s, 'custom_blocks', 'Workspace', %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
			""", (f"{ws_name}_cb{idx}", bname, bname, ws_name, idx))


def _insert_workspace_shortcuts(ws_name, shortcuts):
	"""Insert shortcut entries into tabWorkspace Shortcut.

	shortcuts: list of dicts with keys: type, link_to, label, icon, doc_view (optional)
	"""
	frappe.db.sql(
		"DELETE FROM `tabWorkspace Shortcut` WHERE parent = %s AND parenttype = 'Workspace'",
		ws_name,
	)
	for idx, sc in enumerate(shortcuts):
		frappe.db.sql("""
			INSERT INTO `tabWorkspace Shortcut`
			(name, type, link_to, url, doc_view, kanban_board, label, icon,
			 restrict_to_domain, report_ref_doctype, stats_filter, color, format,
			 parent, parentfield, parenttype, idx, docstatus, creation, modified, owner, modified_by)
			VALUES (%s, %s, %s, NULL, %s, NULL, %s, %s, NULL, NULL, NULL, NULL, NULL,
			 %s, 'shortcuts', 'Workspace', %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
		""", (
			f"{ws_name}_sc{idx}", sc["type"], sc["link_to"],
			sc.get("doc_view"), sc["label"], sc.get("icon", "link"),
			ws_name, idx,
		))


def _setup_ceo_workspace():
	ws_name = "CEO"
	ceo_content = json.dumps([
		{"id": "h1", "type": "header", "data": {"text": "<span class=\"h4\"><b>CEO Dashboard</b></span>", "col": 12}},
		{"id": "p1", "type": "paragraph", "data": {"text": "Overview of employee task completion and project productivity.", "col": 12}},
		{"id": "nc1", "type": "number_card", "data": {"number_card_name": "Tasks Completed", "col": 3}},
		{"id": "nc2", "type": "number_card", "data": {"number_card_name": "Tasks Pending", "col": 3}},
		{"id": "nc3", "type": "number_card", "data": {"number_card_name": "Active Staff", "col": 3}},
		{"id": "nc4", "type": "number_card", "data": {"number_card_name": "Active Clients", "col": 3}},
		{"id": "cb1", "type": "custom_block", "data": {"custom_block_name": "CEO Top Bottom Employees", "col": 12}},
		{"id": "c1", "type": "chart", "data": {"chart_name": "Employee Performance Trend", "col": 12}},
		{"id": "c2", "type": "chart", "data": {"chart_name": "Tasks by Status", "col": 6}},
		{"id": "c3", "type": "chart", "data": {"chart_name": "Tasks Completed Over Time", "col": 6}},
		{"id": "c4", "type": "chart", "data": {"chart_name": "Open Tasks by Project", "col": 6}},
		{"id": "c5", "type": "chart", "data": {"chart_name": "Task Priority Distribution", "col": 6}},
		{"id": "sp1", "type": "spacer", "data": {"col": 12}},
		{"id": "sh2", "type": "header", "data": {"text": "<span class=\"h5\"><b>Quick Actions</b></span>", "col": 12}},
		{"id": "s1", "type": "shortcut", "data": {"shortcut_name": "Staff Productivity", "col": 3}},
		{"id": "s2", "type": "shortcut", "data": {"shortcut_name": "Employee Performance", "col": 3}},
	])

	if frappe.db.exists("Workspace", ws_name):
		frappe.db.set_value("Workspace", ws_name, "content", ceo_content)
	else:
		frappe.db.sql("""
			INSERT INTO `tabWorkspace`
			(name, label, module, is_hidden, public, content, docstatus, creation, modified, owner, modified_by)
			VALUES (%s, %s, 'Alpha Assignment Management', 0, 1, %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
		""", (ws_name, ws_name, ceo_content))

	_insert_workspace_charts(ws_name, [
		"Employee Performance Trend", "Tasks by Status", "Tasks Completed Over Time",
		"Open Tasks by Project", "Task Priority Distribution",
	])
	_insert_workspace_number_cards(ws_name, [
		"Tasks Completed", "Tasks Pending", "Active Staff", "Active Clients",
	])
	_insert_workspace_custom_blocks(ws_name, ["CEO Top Bottom Employees"])
	_insert_workspace_shortcuts(ws_name, [
		{"type": "Report", "link_to": "Staff Productivity", "label": "Staff Productivity", "icon": "chart"},
		{"type": "Report", "link_to": "Employee Performance", "label": "Employee Performance", "icon": "chart"},
	])


def _setup_aims_desk_workspace():
	ws_name = "AIMS Desk"
	aims_shortcuts = [
		{"type": "DocType", "link_to": "Alpha Assignment Origination", "label": "New Assignment Origination", "icon": "add"},
		{"type": "DocType", "link_to": "Alpha Assignment Origination", "label": "All Assignments", "icon": "list", "doc_view": "list"},
		{"type": "DocType", "link_to": "Task", "label": "My Tasks", "icon": "task"},
		{"type": "Report", "link_to": "Staff Productivity", "label": "Staff Productivity", "icon": "chart"},
		{"type": "DocType", "link_to": "Document Request Register", "label": "Document Requests", "icon": "file"},
		{"type": "DocType", "link_to": "Review Gate Register", "label": "Review Queue", "icon": "review"},
		{"type": "DocType", "link_to": "Client Delay Log", "label": "Client Delays", "icon": "warn"},
		{"type": "DocType", "link_to": "Client Risk Register", "label": "Risk Register", "icon": "list"},
	]

	aims_content = json.dumps([
		{"id": "h1", "type": "header", "data": {"text": "<span class=\"h4\"><b>AIMS Desk</b></span>", "col": 12}},
		{"id": "p1", "type": "paragraph", "data": {"text": "Manage client assignments from origination to closure.", "col": 12}},
		{"id": "nc1", "type": "number_card", "data": {"number_card_name": "Active Assignments", "col": 3}},
		{"id": "nc2", "type": "number_card", "data": {"number_card_name": "Active Projects", "col": 3}},
		{"id": "nc3", "type": "number_card", "data": {"number_card_name": "Tasks Completed", "col": 3}},
		{"id": "nc4", "type": "number_card", "data": {"number_card_name": "Tasks Pending", "col": 3}},
		{"id": "c1", "type": "chart", "data": {"chart_name": "Employee Performance Trend", "col": 12}},
		{"id": "sp1", "type": "spacer", "data": {"col": 12}},
		{"id": "sh2", "type": "header", "data": {"text": "<span class=\"h5\"><b>Quick Actions</b></span>", "col": 12}},
	] + [
		{"id": f"s{i+1}", "type": "shortcut", "data": {"shortcut_name": sc["label"], "col": 3}}
		for i, sc in enumerate(aims_shortcuts)
	])

	if frappe.db.exists("Workspace", ws_name):
		frappe.db.set_value("Workspace", ws_name, "content", aims_content)
	else:
		frappe.db.sql("""
			INSERT INTO `tabWorkspace`
			(name, label, module, is_hidden, public, content, docstatus, creation, modified, owner, modified_by)
			VALUES (%s, %s, 'Alpha Assignment Management', 0, 1, %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
		""", (ws_name, ws_name, aims_content))

	_insert_workspace_charts(ws_name, ["Employee Performance Trend"])
	_insert_workspace_number_cards(ws_name, [
		"Active Assignments", "Active Projects", "Tasks Completed", "Tasks Pending",
	])
	_insert_workspace_shortcuts(ws_name, aims_shortcuts)
