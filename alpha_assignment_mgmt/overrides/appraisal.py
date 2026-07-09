import frappe


def validate(doc, method):
	"""Auto-calculate assignment metrics for the appraisal."""
	if not doc.employee:
		return

	calculate_assignments_completed(doc)
	calculate_sla_compliance(doc)
	calculate_utilization(doc)


def calculate_assignments_completed(doc):
	"""Count completed projects where employee is Engagement Manager."""
	if doc.start_date and doc.end_date:
		completed = frappe.db.count(
			"Project",
			filters={
				"custom_engagement_manager": doc.employee,
				"status": "Completed",
				"modified": ["between", [doc.start_date, doc.end_date]],
			},
		)
	else:
		completed = frappe.db.count(
			"Project",
			filters={
				"custom_engagement_manager": doc.employee,
				"status": "Completed",
			},
		)
	doc.custom_assignments_completed = completed


def calculate_sla_compliance(doc):
	"""Calculate SLA compliance rate for the appraisal period."""
	employee_projects = frappe.get_all(
		"Project",
		filters={"custom_engagement_manager": doc.employee},
		pluck="name",
	)

	if not employee_projects:
		doc.custom_sla_compliance_rate = 100
		return

	filters = {
		"project": ["in", employee_projects],
		"docstatus": 1,
	}

	if doc.start_date and doc.end_date:
		filters["creation"] = ["between", [doc.start_date, doc.end_date]]

	total = frappe.db.count("Alpha Engagement SLA", filters=filters)

	if not total:
		doc.custom_sla_compliance_rate = 100
		return

	breached_filters = {**filters, "status": "Breached"}
	breached = frappe.db.count("Alpha Engagement SLA", filters=breached_filters)

	compliant = total - breached
	doc.custom_sla_compliance_rate = round((compliant / total) * 100, 1)


def calculate_utilization(doc):
	"""Calculate utilization rate from timesheets for the appraisal period."""
	if not doc.start_date or not doc.end_date:
		return

	working_days = frappe.db.count(
		"Attendance",
		filters={
			"employee": doc.employee,
			"status": "Present",
			"attendance_date": ["between", [doc.start_date, doc.end_date]],
		},
	)

	if not working_days:
		doc.custom_utilization_rate = 0
		return

	total_hours = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(tt.hours), 0)
		FROM `tabTimesheet Detail` tt
		JOIN `tabTimesheet` t ON t.name = tt.parent
		WHERE tt.employee = %s
		AND t.start_date >= %s
		AND t.end_date <= %s
		AND t.docstatus = 1
		""",
		(doc.employee, doc.start_date, doc.end_date),
	)[0][0]

	available_hours = working_days * 8
	doc.custom_utilization_rate = (
		round((total_hours / available_hours) * 100, 1) if available_hours > 0 else 0
	)
