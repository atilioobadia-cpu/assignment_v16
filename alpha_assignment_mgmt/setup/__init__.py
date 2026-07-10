import frappe
import json


def after_install():
	create_roles()
	create_naming_series()
	create_project_types()
	create_activity_types()
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


def create_dashboard_charts():
	charts = [
		{
			"chart_name": "Assignments by Service Line",
			"chart_type": "Group By",
			"document_type": "Alpha Assignment Origination",
			"group_by_type": "Count",
			"group_by_based_on": "service_line",
			"type": "Bar",
			"filters_json": "[]",
		},
		{
			"chart_name": "Assignments by Status",
			"chart_type": "Group By",
			"document_type": "Alpha Assignment Origination",
			"group_by_type": "Count",
			"group_by_based_on": "acceptance_status",
			"type": "Bar",
			"filters_json": "[]",
		},
		{
			"chart_name": "SLA Health Overview",
			"chart_type": "Group By",
			"document_type": "Alpha Engagement SLA",
			"group_by_type": "Count",
			"group_by_based_on": "status",
			"type": "Donut",
			"filters_json": "[]",
		},
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
	ws_name = "Alpha Assignment Desk"
	if not frappe.db.exists("Workspace", ws_name):
		return

	content = [
		{
			"id": "h1",
			"type": "header",
			"data": {
				"text": '<span class="h4"><b>Alpha Assignment Desk</b></span>',
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
		"Assignments by Service Line",
		"Assignments by Status",
		"SLA Health Overview",
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
	ws_name = "CEO Assignment Dashboard"
	if not frappe.db.exists("Workspace", ws_name):
		return

	content = [
		{
			"id": "h1",
			"type": "header",
			"data": {
				"text": '<span class="h4"><b>CEO Assignment Dashboard</b></span>',
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
		("s1", "New Assignment"), ("s2", "All Assignments"),
		("s3", "Active Projects"), ("s4", "Risk Register"),
		("s5", "Staff Productivity"), ("s6", "Employee Performance"),
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
