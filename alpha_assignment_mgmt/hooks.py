app_name = "alpha_assignment_mgmt"
app_title = "Alpha Assignment Management"
app_publisher = "Alpha Associates (T) Limited"
app_description = "Professional service assignment management framework for Alpha Associates"
app_email = "info@alphaassociates.co.tz"
app_icon = "octicon octicon-checklist"
app_color = "#2563EB"

required_apps = ["frappe/erpnext", "frappe/hrms"]

after_install = "alpha_assignment_mgmt.setup.after_install"
after_migrate = "alpha_assignment_mgmt.setup.after_migrate"

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
			["dt", "in", [
				"Project",
				"Task",
				"Goal",
				"Appraisal"
			]]
		]
	},
]
