import frappe
import json
import os


def after_install():
	_cleanup_workflow_state_field()
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
	_setup_client_portal_workspace()
	_create_default_items()
	_add_billing_custom_fields()
	_setup_accounts_billing_workspace()
	_setup_technical_review_workspace()
	_create_ceo_api_method()
	_create_phase5_workflows()
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
		"Alpha HR Admin",
		"Alpha Tax Officer",
		"Alpha Managing Director",
		"Alpha Client",
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
		{"state": "Partner Review", "doc_status": "1", "allow_edit": "Alpha Partner/Director"},
		{"state": "Approved", "doc_status": "1", "allow_edit": "Alpha Managing Director"},
		{"state": "Rejected", "doc_status": "1", "allow_edit": "System Manager"},
		{"state": "Project Created", "doc_status": "1", "allow_edit": "Alpha Engagement Manager"},
		{"state": "Closed", "doc_status": "1", "allow_edit": "System Manager"},
		{"state": "CC - Draft", "doc_status": "0", "allow_edit": "Alpha Engagement Manager"},
		{"state": "CC - Review", "doc_status": "1", "allow_edit": "Alpha Branch Manager"},
		{"state": "CC - Approved", "doc_status": "1", "allow_edit": "Alpha Partner/Director"},
		{"state": "CC - Rejected", "doc_status": "1", "allow_edit": "Alpha Partner/Director"},
		{"state": "CC - Closed", "doc_status": "1", "allow_edit": "System Manager"},
	]
	for state in states:
		if not frappe.db.exists("Workflow State", state["state"]):
			frappe.get_doc({
				"doctype": "Workflow State",
				"workflow_state_name": state["state"],
			}).insert(ignore_permissions=True)


def _add_phase5_workflow_states():
    states = [
        {"state": "RG - Pending Review", "doc_status": "0", "allow_edit": "Alpha Reviewer"},
        {"state": "RG - Approved", "doc_status": "1", "allow_edit": "Alpha Reviewer"},
        {"state": "RG - Returned", "doc_status": "1", "allow_edit": "Alpha Reviewer"},
        {"state": "RG - Escalated", "doc_status": "1", "allow_edit": "System Manager"},
        {"state": "PF - Draft", "doc_status": "0", "allow_edit": "Alpha Staff"},
        {"state": "PF - Submitted", "doc_status": "1", "allow_edit": "Alpha Reviewer"},
        {"state": "PF - Acknowledged", "doc_status": "1", "allow_edit": "Alpha Engagement Manager"},
    ]
    for s in states:
        if not frappe.db.exists("Workflow State", s["state"]):
            frappe.get_doc({
                "doctype": "Workflow State",
                "workflow_state_name": s["state"],
            }).insert(ignore_permissions=True)



def create_naming_series():
	"""Set naming series via Property Setter."""
	series_map = {
		"Alpha Assignment Origination": "AOR-.YYYY.-.#####",
		"Alpha Engagement SLA": "AATL-SLA-.YYYY.-.#####",
		"Alpha Service Contract": "ASC-.YYYY.-.#####",
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


def _create_phase5_workflows():
    workflows = [
        {
            "workflow_name": "Review Gate Workflow",
            "document_type": "Review Gate Register",
            "is_active": 1,
            "override_status": 0,
            "states": [
                {"state": "RG - Pending Review", "doc_status": "0", "allow_edit": "Alpha Reviewer"},
                {"state": "RG - Approved", "doc_status": "1", "allow_edit": "Alpha Partner/Director"},
                {"state": "RG - Returned", "doc_status": "1", "allow_edit": "Alpha Reviewer"},
                {"state": "RG - Escalated", "doc_status": "1", "allow_edit": "System Manager"},
            ],
            "transitions": [
                {"state": "RG - Pending Review", "action": "Approve", "next_state": "RG - Approved", "allowed": "Alpha Reviewer", "allow_self_approval": 1},
                {"state": "RG - Pending Review", "action": "Return for Correction", "next_state": "RG - Returned", "allowed": "Alpha Reviewer", "allow_self_approval": 1},
                {"state": "RG - Pending Review", "action": "Escalate", "next_state": "RG - Escalated", "allowed": "Alpha Reviewer", "allow_self_approval": 1},
                {"state": "RG - Returned", "action": "Resubmit", "next_state": "RG - Pending Review", "allowed": "Alpha Staff", "allow_self_approval": 1},
            ],
        },
        {
            "workflow_name": "Performance Feedback Workflow",
            "document_type": "Performance Feedback",
            "is_active": 1,
            "override_status": 0,
            "states": [
                {"state": "PF - Draft", "doc_status": "0", "allow_edit": "Alpha Staff"},
                {"state": "PF - Submitted", "doc_status": "1", "allow_edit": "Alpha Reviewer"},
                {"state": "PF - Acknowledged", "doc_status": "1", "allow_edit": "Alpha Engagement Manager"},
            ],
            "transitions": [
                {"state": "PF - Draft", "action": "Submit", "next_state": "PF - Submitted", "allowed": "Alpha Staff", "allow_self_approval": 1},
                {"state": "PF - Submitted", "action": "Acknowledge", "next_state": "PF - Acknowledged", "allowed": "Alpha Engagement Manager", "allow_self_approval": 1},
                {"state": "PF - Submitted", "action": "Return to Draft", "next_state": "PF - Draft", "allowed": "Alpha Reviewer", "allow_self_approval": 1},
            ],
        },
    ]

    for wf in workflows:
        name = wf["workflow_name"]
        if frappe.db.exists("Workflow", name):
            continue

        doc = frappe.new_doc("Workflow")
        doc.workflow_name = name
        doc.document_type = wf["document_type"]
        doc.is_active = wf["is_active"]
        doc.override_status = wf["override_status"]

        for state in wf["states"]:
            doc.append("states", {
                "state": state["state"],
                "doc_status": int(state["doc_status"]),
                "allow_edit": state["allow_edit"],
            })

        for transition in wf["transitions"]:
            doc.append("transitions", transition)

        doc.flags.ignore_permissions = True
        doc.insert()



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


def create_customer_fields():
	"""Add assignment-related custom fields to Customer (central hub)."""
	fields = [
		{"fieldname": "custom_engagement_manager", "label": "Engagement Manager", "fieldtype": "Link", "options": "User", "insert_after": "customer_details"},
		{"fieldname": "custom_client_owner", "label": "Client Owner", "fieldtype": "Link", "options": "User", "insert_after": "custom_engagement_manager"},
		{"fieldname": "custom_branch_manager", "label": "Branch Manager", "fieldtype": "Link", "options": "User", "insert_after": "custom_client_owner"},
		{"fieldname": "custom_service_line", "label": "Default Service Line", "fieldtype": "Link", "options": "Project Type", "insert_after": "custom_branch_manager"},
		{"fieldname": "custom_risk_rating", "label": "Default Risk Rating", "fieldtype": "Select", "options": "Low\nMedium\nHigh\nCritical", "insert_after": "custom_service_line"},
		{"fieldname": "custom_sector", "label": "Sector", "fieldtype": "Data", "insert_after": "custom_risk_rating"},
		{"fieldname": "custom_tin", "label": "TIN", "fieldtype": "Data", "insert_after": "custom_sector"},
		{"fieldname": "custom_service_category", "label": "Service Category", "fieldtype": "Select", "options": "Tax\nAudit\nBookkeeping\nAdvisory\nERPNext\nTRA Support", "insert_after": "custom_tin"},
		{"fieldname": "custom_pricing_model", "label": "Pricing Model", "fieldtype": "Select", "options": "Fixed Fee\nTime Based\nMilestone\nRetainer", "insert_after": "custom_service_category"},
		{"fieldname": "custom_contract_status", "label": "Contract Status", "fieldtype": "Select", "options": "Draft\nActive\nExpiring\nExpired\nTerminated", "insert_after": "custom_pricing_model"},
		{"fieldname": "custom_collection_status", "label": "Collection Status", "fieldtype": "Select", "options": "Current\nOverdue 30\nOverdue 60\nOverdue 90+\nWritten Off", "insert_after": "custom_contract_status"},
		{"fieldname": "custom_portal_user", "label": "Portal User", "fieldtype": "Link", "options": "User", "insert_after": "custom_collection_status"},
		{"fieldname": "custom_accountant", "label": "Accountant", "fieldtype": "Link", "options": "User", "insert_after": "custom_portal_user"},
		{"fieldname": "custom_tax_officer", "label": "Tax Officer", "fieldtype": "Link", "options": "User", "insert_after": "custom_accountant"},
		{"fieldname": "custom_reviewer", "label": "Reviewer", "fieldtype": "Link", "options": "User", "insert_after": "custom_tax_officer"},
		{"fieldname": "custom_kyc_completed", "label": "KYC Completed", "fieldtype": "Check", "insert_after": "custom_reviewer"},
		{"fieldname": "custom_kyc_date", "label": "KYC Date", "fieldtype": "Date", "insert_after": "custom_kyc_completed"},
		{"fieldname": "custom_onboarding_date", "label": "Onboarding Date", "fieldtype": "Date", "insert_after": "custom_kyc_date"},
	]
	for f in fields:
		if not frappe.db.exists("Custom Field", {"dt": "Customer", "fieldname": f["fieldname"]}):
			frappe.get_doc({
				"doctype": "Custom Field",
				"dt": "Customer",
				**f,
			}).insert(ignore_permissions=True)


def create_rejection_reason_field():
	"""Add custom_rejection_reason to Alpha Assignment Origination."""
	if not frappe.db.exists("Custom Field", {"dt": "Alpha Assignment Origination", "fieldname": "custom_rejection_reason"}):
		frappe.get_doc({
			"doctype": "Custom Field",
			"dt": "Alpha Assignment Origination",
			"fieldname": "custom_rejection_reason",
			"label": "Rejection Reason",
			"fieldtype": "Small Text",
			"insert_after": "acceptance_status",
			"mandatory_depends_on": "eval:doc.workflow_state == 'Rejected'",
		}).insert(ignore_permissions=True)

	# Add custom_assigned_to on Task for tracking assigned user
	if not frappe.db.exists("Custom Field", {"dt": "Task", "fieldname": "custom_assigned_to"}):
		frappe.get_doc({
			"doctype": "Custom Field",
			"dt": "Task",
			"fieldname": "custom_assigned_to",
			"label": "Assigned To (User)",
			"fieldtype": "Link",
			"options": "User",
			"insert_after": "custom_evidence_exception",
		}).insert(ignore_permissions=True)


def _create_additional_templates():
    templates = [
        {
            "template_name": "Advisory Engagement",
            "project_type": "Advisory",
            "service_line": "Advisory",
            "description": "Standard task sequence for advisory and consulting engagements",
            "tasks": [
                {"task_subject": "Engagement confirmation and scope definition", "sequence": 1, "expected_hours": 1, "requires_review": 0, "default_owner_role": "Alpha Engagement Manager", "expected_output": "Approved scope, objectives and timeline"},
                {"task_subject": "Client briefing and data collection", "sequence": 2, "expected_hours": 2, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "1", "expected_output": "Client briefing notes and data request"},
                {"task_subject": "Research and analysis", "sequence": 3, "expected_hours": 4, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "2", "expected_output": "Research findings and analysis report"},
                {"task_subject": "Draft advisory report", "sequence": 4, "expected_hours": 3, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "3", "expected_output": "Draft advisory report with findings"},
                {"task_subject": "Technical review of advisory report", "sequence": 5, "expected_hours": 2, "requires_review": 1, "default_owner_role": "Alpha Reviewer", "depends_on": "4", "expected_output": "Review clearance and sign-off"},
                {"task_subject": "Client presentation and discussion", "sequence": 6, "expected_hours": 2, "requires_review": 0, "default_owner_role": "Alpha Engagement Manager", "depends_on": "5", "expected_output": "Client presentation delivered"},
                {"task_subject": "Final report and recommendations", "sequence": 7, "expected_hours": 2, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "6", "expected_output": "Final advisory report issued"},
                {"task_subject": "Assignment closure", "sequence": 8, "expected_hours": 0.5, "requires_review": 0, "default_owner_role": "Alpha Engagement Manager", "depends_on": "7", "expected_output": "Closure certificate submitted"},
            ],
        },
        {
            "template_name": "ERPNext Implementation",
            "project_type": "ERPNext Implementation",
            "service_line": "ERPNext Implementation",
            "description": "Standard task sequence for ERPNext implementation engagements",
            "tasks": [
                {"task_subject": "Requirements gathering and scoping", "sequence": 1, "expected_hours": 4, "requires_review": 0, "default_owner_role": "Alpha Engagement Manager", "expected_output": "Requirements document and scope statement"},
                {"task_subject": "System setup and configuration", "sequence": 2, "expected_hours": 8, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "1", "expected_output": "Configured ERPNext instance"},
                {"task_subject": "Chart of accounts and master data setup", "sequence": 3, "expected_hours": 4, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "2", "expected_output": "COA and master data approved"},
                {"task_subject": "Data migration from legacy system", "sequence": 4, "expected_hours": 8, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "3", "expected_output": "Data migration complete with validation"},
                {"task_subject": "User training and documentation", "sequence": 5, "expected_hours": 4, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "4", "expected_output": "Training delivered and user guide provided"},
                {"task_subject": "User acceptance testing", "sequence": 6, "expected_hours": 4, "requires_review": 0, "default_owner_role": "Alpha Engagement Manager", "depends_on": "5", "expected_output": "UAT sign-off obtained"},
                {"task_subject": "Go-live and production deployment", "sequence": 7, "expected_hours": 4, "requires_review": 1, "default_owner_role": "Alpha Staff", "depends_on": "6", "expected_output": "System live in production"},
                {"task_subject": "Post go-live support", "sequence": 8, "expected_hours": 4, "requires_review": 0, "default_owner_role": "Alpha Staff", "depends_on": "7", "expected_output": "Support period completed"},
                {"task_subject": "Assignment closure", "sequence": 9, "expected_hours": 0.5, "requires_review": 0, "default_owner_role": "Alpha Engagement Manager", "depends_on": "8", "expected_output": "Closure certificate submitted"},
            ],
        },
    ]
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



def _create_performance_feedback_fields():
	"""Add custom_user field to Performance Feedback."""
	if not frappe.db.exists("Custom Field", {"dt": "Performance Feedback", "fieldname": "custom_user"}):
		frappe.get_doc({
			"doctype": "Custom Field",
			"dt": "Performance Feedback",
			"fieldname": "custom_user",
			"label": "User",
			"fieldtype": "Link",
			"options": "User",
			"insert_after": "employee",
		}).insert(ignore_permissions=True)


def create_project_templates():
	_create_additional_templates()
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
			"currency": "",
		},
		{
			"label": "Active Projects",
			"type": "Document Type",
			"document_type": "Project",
			"function": "Count",
			"filters_json": '[["Project","status","=","Completed"]]',
			"currency": "",
		},
		{
			"label": "Pending Reviews",
			"type": "Document Type",
			"document_type": "Review Gate Register",
			"function": "Count",
			"filters_json": '[["Review Gate Register","docstatus","=",0]]',
			"currency": "",
		},
		{
			"label": "Pending Projects",
			"type": "Document Type",
			"document_type": "Project",
			"function": "Count",
			"filters_json": '[["Project","status","=","Open"]]',
			"currency": "",
		},
		{
			"label": "Active Staff",
			"type": "Document Type",
			"document_type": "Employee",
			"function": "Count",
			"filters_json": '[["Employee","status","=","Active"]]',
			"currency": "",
		},
		{
			"label": "Active Clients",
			"type": "Document Type",
			"document_type": "Customer",
			"function": "Count",
			"filters_json": '[["Customer","disabled","=",0]]',
			"currency": "",
		},
	]
	for card in cards:
		if not frappe.db.exists("Number Card", card["label"]):
			frappe.get_doc({
				"doctype": "Number Card",
				**card,
			}).insert(ignore_permissions=True)
		else:
			frappe.db.set_value("Number Card", card["label"], {"is_public": 1, "currency": ""})


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
	"""Clear currency on all count-based Number Cards via direct SQL.

	Workspace sync and fixture import may set currency to company default (TZS).
	We run this AFTER all setup to override that default.
	"""
	frappe.db.sql("""
		UPDATE `tabNumber Card`
		SET currency = ''
		WHERE name IN (
			'Tasks Completed', 'Tasks Pending',
			'Active Staff', 'Active Clients',
			'Active Assignments', 'Active Projects',
			'Pending Reviews', 'Pending Projects'
		)
		AND currency != ''
	""")


def _clear_dashboard_chart_currencies():
	"""Clear currency on all Dashboard Charts that should show plain numbers, not currency."""
	frappe.db.sql("""
		UPDATE `tabDashboard Chart`
		SET currency = ''
		WHERE module = 'Alpha Assignment Management'
		AND currency != ''
	""")


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
				"currency": "",
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
			doc.currency = ""
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

def _cleanup_workflow_state_field():
	"""Remove custom workflow_state field if it exists (now a standard field in JSON)."""
	if frappe.db.exists("Custom Field", {"dt": "Assignment Closure Certificate", "fieldname": "workflow_state"}):
		frappe.delete_doc("Custom Field", "Assignment Closure Certificate-workflow_state")
		frappe.db.commit()


def _create_ceo_api_method():
	_create_phase5_workflows()
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
		{"type": "DocType", "link_to": "Performance Feedback", "label": "Performance", "icon": "list"},
		{"type": "Report", "link_to": "SLA Compliance Overview", "label": "SLA Compliance", "icon": "chart"},
		{"type": "Report", "link_to": "Staff Productivity", "label": "Staff Productivity", "icon": "chart"},
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
		{"type": "DocType", "link_to": "Performance Feedback", "label": "Feedback", "icon": "list"},
		{"type": "DocType", "link_to": "Document Request Register", "label": "Document Checks", "icon": "file"},
		{"type": "Report", "link_to": "Staff Productivity", "label": "Productivity", "icon": "chart"},
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
	_insert_workspace_number_cards(ws_name, ["Active Staff", "Total Assignments", "Overdue Tasks"])
	_insert_workspace_charts(ws_name, ["Staff Utilization Rate", "Overdue Tasks by Project", "Assignments by Status"])
	_insert_workspace_shortcuts(ws_name, [
		{"type": "Report", "link_to": "Staff Productivity", "label": "Staff Productivity", "icon": "chart"},
		{"type": "Report", "link_to": "Employee Performance", "label": "Employee Performance", "icon": "chart"},
		{"type": "Report", "link_to": "SLA Compliance Overview", "label": "SLA Compliance Overview", "icon": "chart"},
		{"type": "DocType", "link_to": "Performance Feedback", "label": "Performance Feedback", "icon": "list"},
		{"type": "DocType", "link_to": "Appraisal", "label": "Appraisal", "icon": "list"},
	])


def _add_employee_skill_fields():
	fields = [
		{
			"doctype": "Custom Field",
			"dt": "Employee",
			"fieldname": "custom_service_lines",
			"label": "Service Lines",
			"fieldtype": "Small Text",
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
		if not frappe.db.exists("Number Card", card_def["label"]):
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
		if not frappe.db.exists("Dashboard Chart", chart_def["chart_name"]):
			frappe.get_doc({
				"doctype": "Dashboard Chart",
				**chart_def,
				"is_standard": 1,
				"module": "Alpha Assignment Management",
			}).insert(ignore_permissions=True)
