import frappe
from frappe.utils import today, getdate, date_diff, add_months


def validate(doc, method):
	"""Auto-calculate assignment metrics for the appraisal."""
	if not doc.employee:
		return

	calculate_assignments_completed(doc)
	calculate_sla_compliance(doc)
	calculate_utilization(doc)


def on_submit(doc, method):
	"""Auto-create HR Goals from template when appraisal is submitted."""
	create_goals_from_template(doc)


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


def create_goals_from_template(doc):
	"""Create HR Goals based on employee role template."""
	employee = frappe.get_doc("Employee", doc.employee)
	designation = employee.designation or ""

	role_templates = {
		"Alpha Tax Officer": [
			{"goal_name": "Complete all assigned tax returns accurately and on time", "weight": 30},
			{"goal_name": "Maintain 100% SLA compliance on all assigned engagements", "weight": 25},
			{"goal_name": "Document all outputs with proper evidence references", "weight": 15},
			{"goal_name": "Proactively flag client delays within 2 business days", "weight": 10},
			{"goal_name": "Complete at least 2 CPE hours per month", "weight": 10},
			{"goal_name": "Achieve positive feedback from Engagement Manager on 90%+ tasks", "weight": 10},
		],
		"Alpha Reviewer": [
			{"goal_name": "Review all assigned tasks within SLA deadlines", "weight": 25},
			{"goal_name": "Maintain review quality: < 2% rejection rate by Partner", "weight": 25},
			{"goal_name": "Provide constructive feedback on all reviewed tasks", "weight": 15},
			{"goal_name": "Mentor at least 2 Tax Officers during the period", "weight": 15},
			{"goal_name": "Complete all assigned engagements on time", "weight": 10},
			{"goal_name": "Achieve positive client feedback", "weight": 10},
		],
		"Alpha Engagement Manager": [
			{"goal_name": "Deliver all assigned projects within budget and timeline", "weight": 25},
			{"goal_name": "Maintain 95%+ SLA compliance across all engagements", "weight": 20},
			{"goal_name": "Achieve 90%+ client satisfaction ratings", "weight": 15},
			{"goal_name": "Properly document all origination, SLA, and closure requirements", "weight": 15},
			{"goal_name": "Resolve at least 80% of client delays before SLA breach", "weight": 10},
			{"goal_name": "Ensure all staff tasks have owner, deadline, deliverable, and review gate", "weight": 15},
		],
		"Alpha Branch Manager": [
			{"goal_name": "Achieve branch-level utilization rate above 80%", "weight": 20},
			{"goal_name": "Maintain branch-level SLA compliance above 90%", "weight": 20},
			{"goal_name": "Ensure all branch assignments have proper origination docs", "weight": 15},
			{"goal_name": "Reduce client delays by 20% compared to previous period", "weight": 15},
			{"goal_name": "Complete all staff appraisals within scheduled dates", "weight": 15},
			{"goal_name": "Achieve branch revenue targets within 10% variance", "weight": 15},
		],
		"Alpha Partner/Director": [
			{"goal_name": "Achieve firm-wide revenue targets", "weight": 20},
			{"goal_name": "Maintain firm-wide SLA compliance above 92%", "weight": 20},
			{"goal_name": "Ensure all engagements have signed acceptance", "weight": 15},
			{"goal_name": "Drive business development: secure at least 3 new clients", "weight": 15},
			{"goal_name": "Oversee all Closure Certificates are issued on time", "weight": 15},
			{"goal_name": "Maintain professional development of all staff", "weight": 15},
		],
	}

	goals = role_templates.get(designation, role_templates.get("Alpha Tax Officer"))

	if not doc.start_date or not doc.end_date:
		return

	period_days = date_diff(doc.end_date, doc.start_date)
	mid_date = add_months(doc.start_date, period_days // 60) if period_days > 30 else add_months(doc.start_date, 1)

	for goal_data in goals:
		goal = frappe.get_doc({
			"doctype": "Goal",
			"goal_name": goal_data["goal_name"],
			"employee": doc.employee,
			"kpi": "Assignment Quality",
			"start_date": doc.start_date,
			"expected_date": mid_date,
			"status": "Pending",
			"weight": goal_data["weight"],
			"parent_goal": None,
		})
		goal.insert(ignore_permissions=True)
		frappe.db.set_value("Goal", goal.name, "appraisal", doc.name)
