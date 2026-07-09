import frappe


def validate(doc, method):
	"""Validate timesheet against assignment rules."""
	check_project_link(doc)


def check_project_link(doc):
	"""Ensure timesheet is linked to a valid project and task."""
	for time_log in doc.time_logs:
		if not time_log.project:
			frappe.throw(
				"Each timesheet row must be linked to a Project."
			)
