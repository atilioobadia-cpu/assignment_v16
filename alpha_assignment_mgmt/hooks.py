app_name = "alpha_assignment_mgmt"
app_title = "Alpha Assignment Management"
app_publisher = "Alpha Associates (T) Limited"
app_description = "Professional service assignment management framework for Alpha Associates"
app_email = "info@alphaassociates.co.tz"
app_icon = "octicon octicon-checklist"
app_color = "#2563EB"
app_license = "gpl-3.0"

required_apps = ["frappe/erpnext", "frappe/hrms"]

after_install = "alpha_assignment_mgmt.setup.after_install"

scheduler_events = {
	"daily": [
		"alpha_assignment_mgmt.tasks.sla.daily_sla_breach_check",
		"alpha_assignment_mgmt.tasks.notifications.daily_overdue_task_notification",
	],
	"weekly": [
		"alpha_assignment_mgmt.tasks.notifications.weekly_productivity_report",
	],
}

doc_events = {
	"Project": {
		"before_insert": "alpha_assignment_mgmt.overrides.project.before_insert",
		"validate": "alpha_assignment_mgmt.overrides.project.validate",
		"on_update": "alpha_assignment_mgmt.overrides.project.on_update",
	},
	"Task": {
		"validate": "alpha_assignment_mgmt.overrides.task.validate",
		"on_update": "alpha_assignment_mgmt.overrides.task.on_update",
	},
	"Timesheet": {
		"validate": "alpha_assignment_mgmt.overrides.timesheet.validate",
	},
	"Appraisal": {
		"validate": "alpha_assignment_mgmt.overrides.appraisal.validate",
	},
}

fixtures = [
	{
		"doctype": "Workflow",
		"filters": [
			["name", "=", "Alpha Assignment Origination Workflow"]
		]
	},
	{
		"doctype": "Custom Field",
		"filters": [
			["fieldname", "in", [
				"custom_assignment_origination",
				"custom_engagement_sla",
				"custom_branch_manager",
				"custom_engagement_manager",
				"custom_client_owner",
				"custom_risk_rating",
				"custom_service_line",
				"custom_closure_certificate",
				"custom_requires_review",
				"custom_evidence_attachment",
				"custom_evidence_exception",
				"custom_review_gate",
				"custom_client_delay_log",
				"custom_related_project",
				"custom_related_task",
				"custom_metric_type",
				"custom_target_value",
				"custom_actual_value",
				"custom_assignments_completed",
				"custom_sla_compliance_rate",
				"custom_utilization_rate"
			]]
		]
	},
	{
		"doctype": "Project Type",
		"filters": [
			["name", "in", [
				"Tax Compliance",
				"Audit Readiness",
				"Accounting Reconstruction",
				"Monthly Bookkeeping",
				"TRA Support",
				"ERPNext Implementation",
				"Advisory"
			]]
		]
	},
]
