import frappe
import json


def after_install():
	create_roles()
	create_naming_series()
	create_project_types()
	create_activity_types()
	create_dashboard_charts()
	create_number_cards()
	update_workspace_with_charts()


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
			"type": "Donut",
		},
		{
			"chart_name": "Assignments by Status",
			"chart_type": "Group By",
			"document_type": "Alpha Assignment Origination",
			"group_by_type": "Count",
			"group_by_based_on": "acceptance_status",
			"type": "Donut",
		},
		{
			"chart_name": "SLA Health Overview",
			"chart_type": "Group By",
			"document_type": "Alpha Engagement SLA",
			"group_by_type": "Count",
			"group_by_based_on": "status",
			"type": "Donut",
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


def update_workspace_with_charts():
	ws_name = "Alpha Assignment Desk"
	if not frappe.db.exists("Workspace", ws_name):
		return

	ws = frappe.get_doc("Workspace", ws_name)

	ws.charts = []
	for name in ["Assignments by Service Line", "Assignments by Status", "SLA Health Overview"]:
		if frappe.db.exists("Dashboard Chart", name):
			ws.append("charts", {"chart_name": name, "label": name})

	ws.number_cards = []
	for name in ["Active Assignments", "Active Projects", "Pending Reviews", "Overdue SLAs"]:
		if frappe.db.exists("Number Card", name):
			ws.append("number_cards", {"number_card_name": name, "label": name})

	content = json.loads(ws.content)

	card_ids = ["nc1", "nc2", "nc3", "nc4"]
	card_names = ["Active Assignments", "Active Projects", "Pending Reviews", "Overdue SLAs"]
	card_content = []
	for cid, cname in zip(card_ids, card_names):
		if frappe.db.exists("Number Card", cname):
			card_content.append({
				"id": cid, "type": "number_card",
				"data": {"number_card_name": cname, "col": 3}
			})

	chart_ids = ["c1", "c2", "c3"]
	chart_names = ["Assignments by Service Line", "Assignments by Status", "SLA Health Overview"]
	chart_content = []
	for cid, cname in zip(chart_ids, chart_names):
		if frappe.db.exists("Dashboard Chart", cname):
			chart_content.append({
				"id": cid, "type": "chart",
				"data": {"chart_name": cname, "col": 4}
			})

	spacer = {"id": "sp1", "type": "spacer", "data": {"col": 12}}

	insert_at = 2
	if card_content:
		content[insert_at:insert_at] = card_content
		content.insert(insert_at + len(card_content), spacer)
	if chart_content:
		content[insert_at + len(card_content) + 1:insert_at + len(card_content) + 1] = chart_content

	ws.content = json.dumps(content)
	ws.save(ignore_permissions=True)
