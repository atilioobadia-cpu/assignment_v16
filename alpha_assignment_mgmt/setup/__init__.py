import frappe
import json
import os


def after_install():
	_cleanup_workflow_state_field()
	"""Set up roles, workflows, templates, dashboards and workspaces after app install."""
	create_roles()
	create_workflow_states()
	_add_phase5_workflow_states()
	create_naming_series()
	create_project_types()
	create_activity_types()
	create_project_templates()
	_create_additional_templates()
	create_customer_fields()
	create_rejection_reason_field()
	_create_performance_feedback_fields()
	_create_assignment_number_cards()
	_create_assignment_dashboard_charts()
	_create_task_number_cards()
	_create_task_dashboard_charts()
	_setup_ceo_workspace()
	_setup_aims_operations_desk()
	_setup_client_owner_workspace()
	_setup_branch_manager_workspace()
	_setup_client_portal_workspace()
	_create_default_items()
	_add_billing_custom_fields()
	_setup_accounts_billing_workspace()
	_setup_technical_review_workspace()
	_create_ceo_api_method()
	_create_phase5_workflows()
	_clear_number_card_currencies()
	_clear_dashboard_chart_currencies()
	_setup_hr_analytics_workspace()
	_add_employee_skill_fields()
	_create_analytics_number_cards()
	_create_analytics_dashboard_charts()
	frappe.db.commit()


def after_migrate():
	_cleanup_workflow_state_field()
	"""Re-sync components after migration."""
	create_workflow_states()
	_add_phase5_workflow_states()
	create_project_templates()
	_create_additional_templates()
	create_customer_fields()
	create_rejection_reason_field()
	_create_task_number_cards()
	_create_task_dashboard_charts()
	_setup_ceo_workspace()
	_setup_aims_operations_desk()
	_setup_client_owner_workspace()
	_setup_branch_manager_workspace()
	_setup_client_portal_workspace()
	_create_default_items()
	_add_billing_custom_fields()
	_setup_accounts_billing_workspace()
	_setup_technical_review_workspace()
	_create_phase5_workflows()
	_clear_number_card_currencies()
	_clear_dashboard_chart_currencies()
	_setup_hr_analytics_workspace()
	_add_employee_skill_fields()
	_create_analytics_number_cards()
	_create_analytics_dashboard_charts()
	frappe.db.commit()


def create_roles():
	roles = [
		"Alpha Partner/Director",
		"Alpha Engagement Manager",
		"Alpha Branch Manager",
		"Alpha Client Owner",
		"Alpha Reviewer",
		"Alpha Staff",
_insert_workspace_number_cards(ws_name, card_names):
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
		# Clear sidebar links
		frappe.db.sql(
			"DELETE FROM `tabWorkspace Link` WHERE parent = %s AND parenttype = 'Workspace'",
			ws_name,
		)
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
	# No custom blocks - Top 5/Bottom 5 is rendered by public/js/ceo_dashboard.js via app_include_js
	frappe.db.sql(
		"DELETE FROM `tabWorkspace Custom Block` WHERE parent = %s AND parenttype = 'Workspace'",
		ws_name,
	)
	_insert_workspace_shortcuts(ws_name, [
		{"type": "Report", "link_to": "Staff Productivity", "label": "Staff Productivity", "icon": "chart"},
		{"type": "Report", "link_to": "Employee Performance", "label": "Employee Performance", "icon": "chart"},
	])


def _setup_aims_operations_desk():
	ws_name = "AIMS Operations Desk"
	shortcuts = [
		{"type": "DocType", "link_to": "Alpha Assignment Origination", "label": "New Assignment", "icon": "add"},
		{"type": "DocType", "link_to": "Alpha Assignment Origination", "label": "All Assignments", "icon": "list", "doc_view": "list"},
		{"type": "DocType", "link_to": "Alpha Project Template", "label": "Project Templates", "icon": "file"},
		{"type": "DocType", "link_to": "Project", "label": "Active Projects", "icon": "list"},
		{"type": "DocType", "link_to": "Project", "label": "Pending Projects", "icon": "list"},
		{"type": "DocType", "link_to": "Alpha Engagement SLA", "label": "Engagement SLA", "icon": "file"},
		{"type": "DocType", "link_to": "Task", "label": "My Tasks", "icon": "task"},
		{"type": "DocType", "link_to": "Timesheet", "label": "My Timesheets", "icon": "list"},
		{"type": "DocType", "link_to": "Document Request Register", "label": "Document Requests", "icon": "file"},
		{"type": "DocType", "link_to": "Review Gate Register", "label": "Review Queue", "icon": "review"},
		{"type": "DocType", "link_to": "Client Delay Log", "label": "Client Delays", "icon": "warn"},
		{"type": "DocType", "link_to": "Client Risk Register", "label": "Risk Register", "icon": "list"},
		{"type": "DocType", "link_to": "Assignment Closure Certificate", "label": "Closure Certificate", "icon": "file"},
	]

	content = json.dumps([
		{"id": "h1", "type": "header", "data": {"text": "<span class=\"h4\"><b>AIMS Operations Desk</b></span>", "col": 12}},
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
		for i, sc in enumerate(shortcuts)
	])

	if frappe.db.exists("Workspace", ws_name):
		frappe.db.set_value("Workspace", ws_name, "content", content)
		frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s AND parenttype = 'Workspace'", ws_name)
	else:
		frappe.db.sql("""
			INSERT INTO `tabWorkspace`
			(name, label, module, is_hidden, public, content, docstatus, creation, modified, owner, modified_by)
			VALUES (%s, %s, 'Alpha Assignment Management', 0, 1, %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
		""", (ws_name, ws_name, content))

	_insert_workspace_charts(ws_name, ["Employee Performance Trend"])
	_insert_workspace_number_cards(ws_name, ["Active Assignments", "Active Projects", "Tasks Completed", "Tasks Pending"])
	_insert_workspace_shortcuts(ws_name, shortcuts)

	# Also update old "AIMS Desk" workspace if it exists (migration aid)
	if frappe.db.exists("Workspace", "AIMS Desk"):
		frappe.db.set_value("Workspace", "AIMS Desk", "content", content)
		_insert_workspace_charts("AIMS Desk", ["Employee Performance Trend"])
		_insert_workspace_number_cards("AIMS Desk", ["Active Assignments", "Active Projects", "Tasks Completed", "Tasks Pending"])
		_insert_workspace_shortcuts("AIMS Desk", shortcuts)


def _setup_client_owner_workspace():
	ws_name = "Client Owner"
	shortcuts = [
		{"type": "DocType", "link_to": "Alpha Assignment Origination", "label": "My Assignments", "icon": "list", "doc_view": "list"},
		{"type": "DocType", "link_to": "Project", "label": "Active Projects", "icon": "list"},
		{"type": "DocType", "link_to": "Document Request Register", "label": "Document Requests", "icon": "file"},
		{"type": "DocType", "link_to": "Client Delay Log", "label": "Client Delays", "icon": "warn"},
		{"type": "DocType", "link_to": "Client Risk Register", "label": "Risk Register", "icon": "list"},
		{"type": "DocType", "link_to": "Assignment Closure Certificate", "label": "Closure Certificates", "icon": "file"},
		{"type": "DocType", "link_to": "Task", "label": "Task Status", "icon": "task", "doc_view": "list"},
		{"type": "Report", "link_to": "SLA Compliance Overview", "label": "SLA Compliance", "icon": "chart"},
	]
	content = json.dumps([
		{"id": "h1", "type": "header", "data": {"text": "<span class=\"h4\"><b>Client Owner Workspace</b></span>", "col": 12}},
		{"id": "p1", "type": "paragraph", "data": {"text": "Monitor your client assignments, documents, and risks.", "col": 12}},
		{"id": "nc1", "type": "number_card", "data": {"number_card_name": "Active Assignments", "col": 3}},
		{"id": "nc2", "type": "number_card", "data": {"number_card_name": "Active Projects", "col": 3}},
		{"id": "nc3", "type": "number_card", "data": {"number_card_name": "Pending Reviews", "col": 3}},
		{"id": "nc4", "type": "number_card", "data": {"number_card_name": "Tasks Pending", "col": 3}},
		{"id": "sp1", "type": "spacer", "data": {"col": 12}},
		{"id": "sh2", "type": "header", "data": {"text": "<span class=\"h5\"><b>Quick Actions</b></span>", "col": 12}},
	] + [
		{"id": f"s{i+1}", "type": "shortcut", "data": {"shortcut_name": sc["label"], "col": 3}}
		for i, sc in enumerate(shortcuts)
	])

	if frappe.db.exists("Workspace", ws_name):
		frappe.db.set_value("Workspace", ws_name, "content", content)
		frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s AND parenttype = 'Workspace'", ws_name)
	else:
		frappe.db.sql("""
			INSERT INTO `tabWorkspace`
			(name, label, module, is_hidden, public, content, docstatus, creation, modified, owner, modified_by)
			VALUES (%s, %s, 'Alpha Assignment Management', 0, 1, %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
		""", (ws_name, ws_name, content))

	_insert_workspace_number_cards(ws_name, ["Active Assignments", "Active Projects", "Pending Reviews", "Tasks Pending"])
	_insert_workspace_shortcuts(ws_name, shortcuts)


def _setup_branch_manager_workspace():
	ws_name = "Branch Manager"
	shortcuts = [
		{"type": "DocType", "link_to": "Alpha Assignment Origination", "label": "Pending Approvals", "icon": "review", "doc_view": "list"},
		{"type": "DocType", "link_to": "Project", "label": "Branch Projects", "icon": "list"},
		{"type": "DocType", "link_to": "Alpha Engagement SLA", "label": "SLA Overview", "icon": "file"},
		{"type": "DocType", "link_to": "Task", "label": "Team Tasks", "icon": "task", "doc_view": "list"},
		{"type": "DocType", "link_to": "Timesheet", "label": "Team Timesheets", "icon": "list"},
		{"type": "DocType", "link_to": "Review Gate Register", "label": "Review Queue", "icon": "review"},
		{"type": "DocType", "link_to": "Client Delay Log", "label": "Client Delays", "icon": "warn"},
		{"type": "Report", "link_to": "Staff Productivity", "label": "Staff Productivity", "icon": "chart"},
		{"type": "Report", "link_to": "SLA Compliance Overview", "label": "SLA Compliance", "icon": "chart"},
	]
	content = json.dumps([
		{"id": "h1", "type": "header", "data": {"text": "<span class=\"h4\"><b>Branch Manager Dashboard</b></span>", "col": 12}},
		{"id": "p1", "type": "paragraph", "data": {"text": "Oversee branch operations, approvals, and team performance.", "col": 12}},
		{"id": "nc1", "type": "number_card", "data": {"number_card_name": "Active Assignments", "col": 3}},
		{"id": "nc2", "type": "number_card", "data": {"number_card_name": "Active Projects", "col": 3}},
		{"id": "nc3", "type": "number_card", "data": {"number_card_name": "Pending Reviews", "col": 3}},
		{"id": "nc4", "type": "number_card", "data": {"number_card_name": "Tasks Pending", "col": 3}},
		{"id": "c1", "type": "chart", "data": {"chart_name": "Employee Performance Trend", "col": 12}},
		{"id": "sp1", "type": "spacer", "data": {"col": 12}},
		{"id": "sh2", "type": "header", "data": {"text": "<span class=\"h5\"><b>Quick Actions</b></span>", "col": 12}},
	] + [
		{"id": f"s{i+1}", "type": "shortcut", "data": {"shortcut_name": sc["label"], "col": 3}}
		for i, sc in enumerate(shortcuts)
	])

	if frappe.db.exists("Workspace", ws_name):
		frappe.db.set_value("Workspace", ws_name, "content", content)
		frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s AND parenttype = 'Workspace'", ws_name)
	else:
		frappe.db.sql("""
			INSERT INTO `tabWorkspace`
			(name, label, module, is_hidden, public, content, docstatus, creation, modified, owner, modified_by)
			VALUES (%s, %s, 'Alpha Assignment Management', 0, 1, %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
		""", (ws_name, ws_name, content))

	_insert_workspace_charts(ws_name, ["Employee Performance Trend"])
	_insert_workspace_number_cards(ws_name, ["Active Assignments", "Active Projects", "Pending Reviews", "Tasks Pending"])
	_insert_workspace_shortcuts(ws_name, shortcuts)

def _setup_client_portal_workspace():
    ws_name = "Client Portal"
    shortcuts = [
        {"type": "DocType", "link_to": "Project", "label": "My Projects", "icon": "list", "doc_view": "list"},
        {"type": "DocType", "link_to": "Alpha Assignment Origination", "label": "My Assignments", "icon": "list", "doc_view": "list"},
        {"type": "DocType", "link_to": "Document Request Register", "label": "Document Requests", "icon": "file"},
        {"type": "DocType", "link_to": "Assignment Closure Certificate", "label": "Closure Certificates", "icon": "file"},
        {"type": "DocType", "link_to": "Client Delay Log", "label": "Log Delay", "icon": "warn"},
    ]
    content = json.dumps([
        {"id": "h1", "type": "header", "data": {"text": '<span class="h4"><b>Client Portal</b></span>', "col": 12}},
        {"id": "p1", "type": "paragraph", "data": {"text": "View your assignments, projects, and documents.", "col": 12}},
        {"id": "nc1", "type": "number_card", "data": {"number_card_name": "Active Projects", "col": 3}},
        {"id": "nc2", "type": "number_card", "data": {"number_card_name": "Active Clients", "col": 3}},
        {"id": "sp1", "type": "spacer", "data": {"col": 12}},
        {"id": "sh2", "type": "header", "data": {"text": '<span class="h5"><b>Quick Actions</b></span>', "col": 12}},
    ] + [
        {"id": "s" + str(i + 1), "type": "shortcut", "data": {"shortcut_name": sc["label"], "col": 3}}
        for i, sc in enumerate(shortcuts)
    ])

    if frappe.db.exists("Workspace", ws_name):
        frappe.db.set_value("Workspace", ws_name, "content", content)
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s AND parenttype = 'Workspace'", ws_name)
    else:
        frappe.db.sql(
            "INSERT INTO `tabWorkspace` (name, label, module, is_hidden, public, content, docstatus, creation, modified, owner, modified_by) VALUES (%s, %s, 'Alpha Assignment Management', 0, 1, %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')",
            (ws_name, ws_name, content),
	_insert_workspace_number_cards(ws_name, ["Active Staff", "Total Assignments", "Overdue Tasks"])
	_insert_workspace_charts(ws_name, ["Staff Utilization Rate", "Overdue Tasks by Project", "Assignments by Status"])
	_insert_workspace_shortcuts(ws_name, [
		{"type": "Report", "link_to": "Staff Productivity", "label": "Staff Productivity", "icon": "chart"},
		{"type": "Report", "link_to": "Employee Performance", "label": "Employee Performance", "icon": "chart"},
		{"type": "Report", "link_to": "SLA Compliance Overview", "label": "SLA Compliance Overview", "icon": "chart"},
		{"type": "DocType", "link_to": "Performance Feedback", "label": "Performance Feedback", "icon": "list"},
		{"type": "DocType", "link_to": "Appraisal", "label": "Appraisal", "icon": "list"},
	])
        )

    frappe.db.sql(
        "DELETE FROM `tabWorkspace Role` WHERE parent = %s AND parenttype = 'Workspace'",
        ws_name,
    )
    frappe.db.sql(
        "INSERT INTO `tabWorkspace Role` (name, role, parent, parentfield, parenttype, idx, docstatus, creation, modified, owner, modified_by) VALUES (%s, %s, %s, 'roles', 'Workspace', 0, 0, NOW(), NOW(), 'Administrator', 'Administrator')",
        (ws_name + "_role0", "Alpha Client", ws_name),
    )

    _insert_workspace_number_cards(ws_name, ["Active Projects", "Active Clients"])
    _insert_workspace_shortcuts(ws_name, shortcuts)
def _setup_client_portal_workspace():
    ws_name = "Client Portal"
    shortcuts = [
        {"type": "DocType", "link_to": "Project", "label": "My Projects", "icon": "list", "doc_view": "list"},
        {"type": "DocType", "link_to": "Alpha Assignment Origination", "label": "My Assignments", "icon": "list", "doc_view": "list"},
        {"type": "DocType", "link_to": "Document Request Register", "label": "Document Requests", "icon": "file"},
        {"type": "DocType", "link_to": "Assignment Closure Certificate", "label": "Closure Certificates", "icon": "file"},
        {"type": "DocType", "link_to": "Client Delay Log", "label": "Log Delay", "icon": "warn"},
    ]
    content = json.dumps([
        {"id": "h1", "type": "header", "data": {"text": '<span class="h4"><b>Client Portal</b></span>', "col": 12}},
        {"id": "p1", "type": "paragraph", "data": {"text": "View your assignments, projects, and documents.", "col": 12}},
        {"id": "nc1", "type": "number_card", "data": {"number_card_name": "Active Projects", "col": 3}},
        {"id": "nc2", "type": "number_card", "data": {"number_card_name": "Active Clients", "col": 3}},
        {"id": "sp1", "type": "spacer", "data": {"col": 12}},
        {"id": "sh2", "type": "header", "data": {"text": '<span class="h5"><b>Quick Actions</b></span>', "col": 12}},
    ] + [
        {"id": "s" + str(i + 1), "type": "shortcut", "data": {"shortcut_name": sc["label"], "col": 3}}
        for i, sc in enumerate(shortcuts)
    ])

    if frappe.db.exists("Workspace", ws_name):
        frappe.db.set_value("Workspace", ws_name, "content", content)
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s AND parenttype = 'Workspace'", ws_name)
    else:
        frappe.db.sql(
            "INSERT INTO `tabWorkspace` (name, label, module, is_hidden, public, content, docstatus, creation, modified, owner, modified_by) VALUES (%s, %s, 'Alpha Assignment Management', 0, 1, %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')",
            (ws_name, ws_name, content),
        )

    _insert_workspace_number_cards(ws_name, ["Active Projects", "Active Clients"])
    _insert_workspace_shortcuts(ws_name, shortcuts)


def _create_default_items():
    item_code = "AIMS Professional Services"
    if not frappe.db.exists("Item", item_code):
        doc = frappe.new_doc("Item")
        doc.item_code = item_code
        doc.item_name = "AIMS Professional Services"
        doc.item_group = "Services"
        doc.is_stock_item = 0
        doc.description = "Professional services provided by Alpha Associates (T) Limited"
        doc.stock_uom = "Nos"
        doc.flags.ignore_permissions = True
        doc.insert()



def _add_billing_custom_fields():
    fields = [
        {
            "dt": "Sales Order",
            "fieldname": "custom_project",
            "label": "Project",
            "fieldtype": "Link",
            "options": "Project",
            "insert_after": "customer",
            "read_only": 1,
        },
        {
            "dt": "Sales Invoice",
            "fieldname": "custom_project",
            "label": "Project",
            "fieldtype": "Link",
            "options": "Project",
            "insert_after": "customer",
            "read_only": 1,
        },
    ]
    for f in fields:
        if not frappe.db.exists("Custom Field", {"dt": f["dt"], "fieldname": f["fieldname"]}):
            frappe.get_doc({
                "doctype": "Custom Field",
                **f,
            }).insert(ignore_permissions=True)



def _setup_accounts_billing_workspace():
    ws_name = "Accounts & Billing"
    shortcuts = [
        {"type": "DocType", "link_to": "Sales Order", "label": "Sales Orders", "icon": "list", "doc_view": "list"},
        {"type": "DocType", "link_to": "Sales Invoice", "label": "Sales Invoices", "icon": "list", "doc_view": "list"},
        {"type": "DocType", "link_to": "Payment Entry", "label": "Payment Entries", "icon": "list", "doc_view": "list"},
        {"type": "DocType", "link_to": "Project", "label": "Projects", "icon": "list", "doc_view": "list"},
        {"type": "DocType", "link_to": "Alpha Service Contract", "label": "Service Contracts", "icon": "file"},
        {"type": "Report", "link_to": "Project Profitability", "label": "Project Profitability", "icon": "chart"},
        {"type": "Report", "link_to": "Accounts Receivable", "label": "Accounts Receivable", "icon": "chart"},
        {"type": "Report", "link_to": "Accounts Payable", "label": "Accounts Payable", "icon": "chart"},
    ]
    content = json.dumps([
        {"id": "h1", "type": "header", "data": {"text": '<span class="h4"><b>Accounts & Billing</b></span>', "col": 12}},
        {"id": "p1", "type": "paragraph", "data": {"text": "Manage billing, invoicing, and payments.", "col": 12}},
        {"id": "nc1", "type": "number_card", "data": {"number_card_name": "Active Projects", "col": 3}},
        {"id": "nc2", "type": "number_card", "data": {"number_card_name": "Active Clients", "col": 3}},
        {"id": "sp1", "type": "spacer", "data": {"col": 12}},
        {"id": "sh2", "type": "header", "data": {"text": '<span class="h5"><b>Quick Actions</b></span>', "col": 12}},
    ] + [
        {"id": "s" + str(i + 1), "type": "shortcut", "data": {"shortcut_name": sc["label"], "col": 3}}
        for i, sc in enumerate(shortcuts)
    ])

    if frappe.db.exists("Workspace", ws_name):
        frappe.db.set_value("Workspace", ws_name, "content", content)
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s AND parenttype = 'Workspace'", ws_name)
    else:
        frappe.db.sql(
            "INSERT INTO `tabWorkspace` (name, label, module, is_hidden, public, content, docstatus, creation, modified, owner, modified_by) VALUES (%s, %s, 'Alpha Assignment Management', 0, 1, %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')",
            (ws_name, ws_name, content),
        )

    _insert_workspace_number_cards(ws_name, ["Active Projects", "Active Clients"])
    _insert_workspace_shortcuts(ws_name, shortcuts)






def _setup_technical_review_workspace():
	ws_name = "Technical Review"
	shortcuts = [
		{"type": "DocType", "link_to": "Review Gate Register", "label": "Pending Reviews", "icon": "review", "doc_view": "list"},
		{"type": "DocType", "link_to": "Task", "label": "Tasks for Review", "icon": "task", "doc_view": "list"},
	]
	content = json.dumps([
		{"id": "h1", "type": "header", "data": {"text": "<span class=\"h4\"><b>Technical Review Desk</b></span>", "col": 12}},
		{"id": "p1", "type": "paragraph", "data": {"text": "Manage technical reviews, quality control, and reviewer workload.", "col": 12}},
		{"id": "nc1", "type": "number_card", "data": {"number_card_name": "Pending Reviews", "col": 4}},
		{"id": "nc2", "type": "number_card", "data": {"number_card_name": "Tasks Completed", "col": 4}},
		{"id": "nc3", "type": "number_card", "data": {"number_card_name": "Tasks Pending", "col": 4}},
		{"id": "c1", "type": "chart", "data": {"chart_name": "Tasks by Status", "col": 12}},
		{"id": "sp1", "type": "spacer", "data": {"col": 12}},
		{"id": "sh2", "type": "header", "data": {"text": "<span class=\"h5\"><b>Quick Actions</b></span>", "col": 12}},
	] + [
		{"id": f"s{i+1}", "type": "shortcut", "data": {"shortcut_name": sc["label"], "col": 3}}
		for i, sc in enumerate(shortcuts)
	])

	if frappe.db.exists("Workspace", ws_name):
		frappe.db.set_value("Workspace", ws_name, "content", content)
		frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s AND parenttype = 'Workspace'", ws_name)
	else:
		frappe.db.sql("""
			INSERT INTO `tabWorkspace`
			(name, label, module, is_hidden, public, content, docstatus, creation, modified, owner, modified_by)
			VALUES (%s, %s, 'Alpha Assignment Management', 0, 1, %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
		""", (ws_name, ws_name, content))

	_insert_workspace_charts(ws_name, ["Tasks by Status"])
	_insert_workspace_number_cards(ws_name, ["Pending Reviews", "Tasks Completed", "Tasks Pending"])
	_insert_workspace_shortcuts(ws_name, shortcuts)

def _setup_hr_analytics_workspace():
	ws_name = "HR Analytics"
	if frappe.db.exists("Workspace", ws_name):
		return
	content = json.dumps([
		{"id": "h1", "type": "header", "data": {"text": "<span class=\"h4\"><b>HR Analytics</b></span>", "col": 12}},
		{"id": "p1", "type": "paragraph", "data": {"text": "Staff performance, utilization, and skills overview.", "col": 12}},
		{"id": "nc1", "type": "number_card", "data": {"number_card_name": "Active Staff", "col": 4}},
		{"id": "nc2", "type": "number_card", "data": {"number_card_name": "Total Assignments", "col": 4}},
		{"id": "nc3", "type": "number_card", "data": {"number_card_name": "Overdue Tasks", "col": 4}},
		{"id": "c1", "type": "chart", "data": {"chart_name": "Staff Utilization Rate", "col": 6}},
		{"id": "c2", "type": "chart", "data": {"chart_name": "Overdue Tasks by Project", "col": 6}},
		{"id": "c3", "type": "chart", "data": {"chart_name": "Assignments by Status", "col": 12}},
	])
	frappe.db.sql(
		"INSERT INTO `tabWorkspace` (name, label, module, is_hidden, public, content, docstatus, creation, modified, owner, modified_by) VALUES (%s, %s, 'Alpha Assignment Management', 0, 1, %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')",
		(ws_name, ws_name, content),
	)


def _add_employee_skill_fields():
	fields = [
		{
			"doctype": "Custom Field",
			"dt": "Employee",
			"fieldname": "custom_service_lines",
			"label": "Service Lines",
			"fieldtype": "Multi Select",
			"options": "\nTax Compliance\nAudit & Assurance\nBookkeeping\nAccounting Reconstruction\nCompany Secretarial\nPayroll\nBusiness Advisory\nTRA Support\nInternal Audit\nConsultancy\nAdvisory\nERPNext Implementation",
			"insert_after": "custom_utilization_rate_30d",
		},
		{
			"doctype": "Custom Field",
			"dt": "Employee",
			"fieldname": "custom_proficiency_notes",
			"label": "Proficiency Notes",
			"fieldtype": "Small Text",
			"insert_after": "custom_service_lines",
		},
		{
			"doctype": "Custom Field",
			"dt": "Employee",
			"fieldname": "custom_on_leave",
			"label": "On Leave",
			"fieldtype": "Check",
			"read_only": 1,
			"insert_after": "custom_proficiency_notes",
		},
	]
	for field_def in fields:
		if not frappe.db.exists("Custom Field", {"dt": "Employee", "fieldname": field_def["fieldname"]}):
			frappe.get_doc(field_def).insert(ignore_permissions=True)


def _create_analytics_number_cards():
	cards = [
		{
			"name": "Active Staff",
			"label": "Active Staff",
			"type": "Document Type",
			"document_type": "Employee",
			"function": "Count",
			"filters_json": '{"status": "Active"}',
			"show_percentage_change": 0,
		},
		{
			"name": "Total Assignments",
			"label": "Total Assignments",
			"type": "Document Type",
			"document_type": "Project",
			"function": "Count",
			"filters_json": '{"status": "Open"}',
			"show_percentage_change": 0,
		},
		{
			"name": "Overdue Tasks",
			"label": "Overdue Tasks",
			"type": "Document Type",
			"document_type": "Task",
			"function": "Count",
			"filters_json": '{"status": "Overdue"}',
			"show_percentage_change": 0,
		},
	]
	for card_def in cards:
		if not frappe.db.exists("Number Card", card_def["name"]):
			frappe.get_doc({
				"doctype": "Number Card",
				**card_def,
				"is_standard": 1,
				"module": "Alpha Assignment Management",
			}).insert(ignore_permissions=True)


def _create_analytics_dashboard_charts():
	charts = [
		{
			"name": "Staff Utilization Rate",
			"chart_name": "Staff Utilization Rate",
			"type": "Report",
			"report_name": "Employee Performance",
			"timeseries": 0,
			"chart_type": "Bar",
			"is_public": 1,
			"filters_json": '{}',
			"group_by_type": "Count",
			"number_of_groups": 0,
		},
		{
			"name": "Overdue Tasks by Project",
			"chart_name": "Overdue Tasks by Project",
			"type": "Report",
			"report_name": "Staff Productivity",
			"timeseries": 0,
			"chart_type": "Bar",
			"is_public": 1,
			"filters_json": '{"status": "Overdue"}',
			"group_by_type": "Count",
			"number_of_groups": 0,
		},
		{
			"name": "Assignments by Status",
			"chart_name": "Assignments by Status",
			"type": "Report",
			"report_name": "Staff Productivity",
			"timeseries": 0,
			"chart_type": "Percentage",
			"is_public": 1,
			"filters_json": '{}',
			"group_by_type": "Count",
			"number_of_groups": 0,
		},
	]
	for chart_def in charts:
		if not frappe.db.exists("Dashboard Chart", chart_def["name"]):
			frappe.get_doc({
				"doctype": "Dashboard Chart",
				**chart_def,
				"is_standard": 1,
				"module": "Alpha Assignment Management",
			}).insert(ignore_permissions=True)
