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

app_include_css = ["/assets/alpha_assignment_mgmt/css/theme.css"]
app_include_js = [
	"/assets/alpha_assignment_mgmt/js/project.js",
	"/assets/alpha_assignment_mgmt/js/task.js",
	"/assets/alpha_assignment_mgmt/js/ceo_dashboard.js",
]
app_include_css = [
	"/assets/alpha_assignment_mgmt/css/workspace.css",
]

scheduler_events = {
	"daily": [
		"alpha_assignment_mgmt.tasks.sla.daily_sla_breach_check",
		"alpha_assignment_mgmt.tasks.notifications.daily_overdue_task_notification",
		"alpha_assignment_mgmt.tasks.performance.daily_performance_computation",
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
		"on_submit": "alpha_assignment_mgmt.overrides.appraisal.on_submit",
	},
	"Alpha Assignment Origination": {
		"on_update": "alpha_assignment_mgmt.overrides.assignment_origination.on_update",
	},
}

permission_query_conditions = {
	"Task": "alpha_assignment_mgmt.overrides.task.get_permission_query_conditions"
}

has_permission = {
	"Task": "alpha_assignment_mgmt.overrides.task.has_permission"
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
				"Appraisal",
				"Employee",
				"Timesheet Detail"
			]]
		]
	},
	{
		"doctype": "Report",
		"filters": [
			["name", "in", ["Employee Performance", "Staff Productivity"]]
		]
	},
	{
		"doctype": "Number Card",
		"filters": [
			["name", "in", ["Tasks Completed", "Tasks Pending"]]
		]
	},
	{
		"doctype": "Dashboard Chart",
		"filters": [
			["name", "in", [
				"Employee Performance Trend",
				"Tasks by Status",
				"Tasks Completed Over Time",
				"Open Tasks by Project",
				"Task Priority Distribution",
			]]
		]
	},
]
