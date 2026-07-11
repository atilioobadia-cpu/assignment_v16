import frappe
import json


def after_install():
	create_roles()
	create_naming_series()
	create_project_types()
	create_activity_types()
	create_project_templates()
	create_dashboard_charts()
	create_number_cards()
	create_ceo_dashboard_charts()
	create_ceo_number_cards()
	update_workspace_with_charts()
	update_ceo_dashboard_with_charts()


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


def create_naming_series():
	series_map = {
		"Alpha Assignment Origination": "AOR-.YYYY.-.#####",
		"Alpha Engagement SLA": "AATL-SLA-.YYYY.-.#####",
	}
	for doctype, series in series_map.items():
		if not frappe.db.get_value(
			"Property Setter",
			{"doc_type": doctype, "property": "naming_series"},
		):
			frappe.get_doc({
				"doctype": "Property Setter",
				"doctype_or_field": "DocType",
				"doc_type": doctype,
				"property": "naming_series",
				"property_type": "Data",
				"value": series,
				"__islocal": 1,
			}).insert(ignore_permissions=True)


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


def create_dashboard_charts():
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


def create_number_cards():
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
			"filters_json": '[["Project","status","=","Active"]]',
		},
		{
			"label": "Pending Reviews",
			"type": "Document Type",
			"document_type": "Review Gate Register",
			"function": "Count",
			"filters_json": '[["Review Gate Register","docstatus","=",0]]',
		},
		{
			"label": "Overdue SLAs",
			"type": "Document Type",
			"document_type": "Alpha Engagement SLA",
			"function": "Count",
			"filters_json": '[["Alpha Engagement SLA","status","=","Breached"]]',
		},
	]
	for card in cards:
		if not frappe.db.exists("Number Card", card["label"]):
			frappe.get_doc({
				"doctype": "Number Card",
				**card,
			}).insert(ignore_permissions=True)


def create_ceo_dashboard_charts():
	charts = [
		{
			"chart_name": "Monthly Assignment Intake",
			"chart_type": "Count",
			"document_type": "Alpha Assignment Origination",
			"based_on": "creation",
			"type": "Bar",
			"timespan": "Last Year",
			"timeseries_based_on": "creation",
			"time_interval": "Monthly",
			"filters_json": "[]",
		},
		{
			"chart_name": "Risk Distribution",
			"chart_type": "Group By",
			"document_type": "Alpha Assignment Origination",
			"group_by_type": "Count",
			"group_by_based_on": "risk_rating",
			"type": "Pie",
			"filters_json": "[]",
		},
		{
			"chart_name": "Client Delays by Impact",
			"chart_type": "Group By",
			"document_type": "Client Delay Log",
			"group_by_type": "Count",
			"group_by_based_on": "impact",
			"type": "Bar",
			"filters_json": "[]",
		},
		{
			"chart_name": "Open Risks by Type",
			"chart_type": "Group By",
			"document_type": "Client Risk Register",
			"group_by_type": "Count",
			"group_by_based_on": "risk_type",
			"type": "Bar",
			"filters_json": '[["Client Risk Register","status","!=","Closed"]]',
		},
	]
	for chart in charts:
		if not frappe.db.exists("Dashboard Chart", chart["chart_name"]):
			frappe.get_doc({
				"doctype": "Dashboard Chart",
				**chart,
			}).insert(ignore_permissions=True)


def create_ceo_number_cards():
	cards = [
		{
			"label": "Total Assignments YTD",
			"type": "Document Type",
			"document_type": "Alpha Assignment Origination",
			"function": "Count",
			"filters_json": '[]',
		},
		{
			"label": "Open Risks",
			"type": "Document Type",
			"document_type": "Client Risk Register",
			"function": "Count",
			"filters_json": '[["Client Risk Register","status","!=","Closed"]]',
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


def _insert_workspace_charts(ws_name, chart_names):
	frappe.db.delete("Workspace Chart", {"parent": ws_name, "parenttype": "Workspace"})
	for cname in chart_names:
		if frappe.db.exists("Dashboard Chart", cname):
			frappe.db.sql("""
				INSERT INTO `tabWorkspace Chart`
				(name, creation, modified, owner, modified_by, parent, parenttype,
				 parentfield, chart_name, label)
				VALUES (%s, NOW(), NOW(), 'Administrator', 'Administrator', %s,
				        'Workspace', 'charts', %s, %s)
			""", (frappe.generate_hash(length=10), ws_name, cname, cname))


def _insert_workspace_number_cards(ws_name, card_names):
	frappe.db.delete("Workspace Number Card", {"parent": ws_name, "parenttype": "Workspace"})
	for cname in card_names:
		if frappe.db.exists("Number Card", cname):
			frappe.db.sql("""
				INSERT INTO `tabWorkspace Number Card`
				(name, creation, modified, owner, modified_by, parent, parenttype,
				 parentfield, number_card_name, label)
				VALUES (%s, NOW(), NOW(), 'Administrator', 'Administrator', %s,
				        'Workspace', 'number_cards', %s, %s)
			""", (frappe.generate_hash(length=10), ws_name, cname, cname))


def update_workspace_with_charts():
	ws_name = "AIMS Desk"
	if not frappe.db.exists("Workspace", ws_name):
		return

	content = [
		{
			"id": "h1",
			"type": "header",
			"data": {
				"text": '<span class="h4"><b>AIMS Desk</b></span>',
				"col": 12
			}
		},
		{
			"id": "p1",
			"type": "paragraph",
			"data": {
				"text": "Manage client assignments from origination to closure. Track SLAs, reviews, document requests, and team productivity.",
				"col": 12
			}
		},
	]

	card_names = ["Active Assignments", "Active Projects", "Pending Reviews", "Overdue SLAs"]
	card_items = []
	for i, cname in enumerate(card_names):
		if frappe.db.exists("Number Card", cname):
			card_items.append({
				"id": f"nc{i+1}", "type": "number_card",
				"data": {"number_card_name": cname, "col": 3}
			})

	chart_names = [
		"Assignments Trend (Last 12 Months)",
	]
	chart_items = []
	for i, cname in enumerate(chart_names):
		if frappe.db.exists("Dashboard Chart", cname):
			chart_items.append({
				"id": f"c{i+1}", "type": "chart",
				"data": {"chart_name": cname, "col": 4}
			})

	content += card_items + chart_items

	content += [
		{"id": "sp1", "type": "spacer", "data": {"col": 12}},
		{
			"id": "sh2",
			"type": "header",
			"data": {
				"text": '<span class="h5"><b>Quick Actions</b></span>',
				"col": 12
			}
		},
	]

	shortcuts = [
		("s1", "New Assignment Origination"), ("s2", "All Assignments"),
		("s3", "Active Projects"), ("s4", "Engagement SLAs"),
		("s5", "Review Queue"), ("s6", "Document Requests"),
		("s7", "Closure Certificates"), ("s8", "Client Delays"),
		("s9", "My Tasks"), ("s10", "My Timesheets"),
		("s11", "Staff Productivity"), ("s12", "SLA Compliance"),
	]
	for sid, sname in shortcuts:
		content.append({
			"id": sid, "type": "shortcut",
			"data": {"shortcut_name": sname, "col": 3}
		})

	frappe.db.set_value("Workspace", ws_name, "content", json.dumps(content))
	_insert_workspace_charts(ws_name, chart_names)
	_insert_workspace_number_cards(ws_name, card_names)


def update_ceo_dashboard_with_charts():
	ws_name = "CEO"
	if not frappe.db.exists("Workspace", ws_name):
		return

	content = [
		{
			"id": "h1",
			"type": "header",
			"data": {
				"text": '<span class="h4"><b>CEO</b></span>',
				"col": 12
			}
		},
		{
			"id": "p1",
			"type": "paragraph",
			"data": {
				"text": "High-level overview of firm performance, risk exposure, and staff productivity.",
				"col": 12
			}
		},
	]

	card_names = ["Total Assignments YTD", "Open Risks", "Active Staff", "Active Clients"]
	card_items = []
	for i, cname in enumerate(card_names):
		if frappe.db.exists("Number Card", cname):
			card_items.append({
				"id": f"nc{i+1}", "type": "number_card",
				"data": {"number_card_name": cname, "col": 3}
			})

	chart_names = [
		"Monthly Assignment Intake",
		"Risk Distribution",
		"Client Delays by Impact",
		"Open Risks by Type",
	]
	chart_items = []
	for i, cname in enumerate(chart_names):
		if frappe.db.exists("Dashboard Chart", cname):
			chart_items.append({
				"id": f"c{i+1}", "type": "chart",
				"data": {"chart_name": cname, "col": 4}
			})

	content += card_items + chart_items

	content += [
		{"id": "sp1", "type": "spacer", "data": {"col": 12}},
		{
			"id": "sh2",
			"type": "header",
			"data": {
				"text": '<span class="h5"><b>CEO Quick Actions</b></span>',
				"col": 12
			}
		},
	]

	shortcuts = [
		("s1", "Staff Productivity"), ("s2", "Employee Performance"),
	]
	for sid, sname in shortcuts:
		content.append({
			"id": sid, "type": "shortcut",
			"data": {"shortcut_name": sname, "col": 3}
		})

	frappe.db.set_value("Workspace", ws_name, "content", json.dumps(content))
	_insert_workspace_charts(ws_name, chart_names)
	_insert_workspace_number_cards(ws_name, card_names)


def after_migrate():
	update_workspace_with_charts()
	update_ceo_dashboard_with_charts()
	create_project_templates()
