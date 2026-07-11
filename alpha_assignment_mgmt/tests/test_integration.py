"""
AIMS Integration Test Suite
Run: bench --site aims.local execute alpha_assignment_mgmt.tests.test_integration.run_all_tests
"""
import frappe
from frappe.utils import today, add_days

_shared = {}


def _cleanup_test_data():
	"""Remove previous test artifacts so tests can run cleanly."""
	try:
		frappe.db.sql("DELETE FROM `tabClient Risk Register` WHERE customer = 'TEST-AIMS-CLIENT'")
		frappe.db.sql("DELETE FROM `tabClient Delay Log` WHERE task IN (SELECT name FROM `tabTask` WHERE project LIKE 'AATL-2026-TAX-TESTA-%')")
		frappe.db.sql("DELETE FROM `tabReview Gate Register` WHERE project LIKE 'AATL-2026-TAX-TESTA-%'")
		frappe.db.sql("DELETE FROM `tabDocument Request Register` WHERE project LIKE 'AATL-2026-TAX-TESTA-%'")
		frappe.db.sql("DELETE FROM `tabAssignment Closure Certificate` WHERE project LIKE 'AATL-2026-TAX-TESTA-%'")
		frappe.db.sql("DELETE FROM `tabPerformance Feedback` WHERE employee IN (SELECT name FROM `tabEmployee` WHERE user_id = 'test.aims.employee@example.com')")
		frappe.db.sql("DELETE FROM `tabAlpha Engagement SLA` WHERE project LIKE 'AATL-2026-TAX-TESTA-%'")
		frappe.db.sql("DELETE FROM `tabTask` WHERE project LIKE 'AATL-2026-TAX-TESTA-%'")
		frappe.db.sql("DELETE FROM `tabProject` WHERE name LIKE 'AATL-2026-TAX-TESTA-%'")
		frappe.db.sql("DELETE FROM `tabAlpha Assignment Origination` WHERE assignment_title = 'Test Tax Filing Integration'")
		frappe.db.commit()
	except Exception:
		frappe.db.rollback()


def run_all_tests():
	"""Run all integration tests and report results."""
	_cleanup_test_data()
	results = []
	tests = [
		test_01_customer_setup,
		test_02_employee_setup,
		test_03_origination_create,
		test_04_origination_to_project,
		test_05_template_task_generation,
		test_06_sla_creation,
		test_07_document_request_auto_create,
		test_08_review_gate_create,
		test_09_client_delay_log,
		test_10_risk_register,
		test_11_closure_certificate_gates,
		test_12_performance_feedback,
		test_13_timesheet_custom_fields,
	]
	for test_fn in tests:
		name = test_fn.__name__
		try:
			test_fn()
			results.append((name, "PASS", ""))
			print(f"  PASS: {name}")
		except Exception as e:
			results.append((name, "FAIL", str(e)[:200]))
			print(f"  FAIL: {name} -> {e}")

	print("\n" + "=" * 60)
	passed = sum(1 for _, s, _ in results if s == "PASS")
	failed = sum(1 for _, s, _ in results if s == "FAIL")
	print(f"Results: {passed} passed, {failed} failed, {len(results)} total")
	if failed:
		print("\nFailed tests:")
		for name, status, err in results:
			if status == "FAIL":
				print(f"  - {name}: {err}")
	print("=" * 60)
	return results


def _ensure_customer():
	customer_name = "TEST-AIMS-CLIENT"
	if not frappe.db.exists("Customer", customer_name):
		doc = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": customer_name,
			"customer_group": "Commercial",
			"territory": "Tanzania",
			"customer_type": "Company",
		})
		doc.flags.ignore_permissions = True
		doc.insert()
	return customer_name


def _ensure_employee():
	emp = frappe.db.get_value("Employee", {"user_id": "test.aims.employee@example.com"}, "name")
	if emp:
		return emp
	user_email = "test.aims.employee@example.com"
	if not frappe.db.exists("User", user_email):
		user = frappe.get_doc({
			"doctype": "User",
			"email": user_email,
			"first_name": "Test",
			"last_name": "AIMS Employee",
			"send_welcome_email": 0,
		})
		user.flags.ignore_permissions = True
		user.insert()
		frappe.db.set_value("User", user_email, "user_type", "System User")
	company = frappe.db.get_default("company") or frappe.db.get_single_value("Global Settings", "default_company")
	doc = frappe.get_doc({
		"doctype": "Employee",
		"employee_name": "Test AIMS Employee",
		"first_name": "Test",
		"last_name": "AIMS Employee",
		"gender": "Male",
		"date_of_birth": "1990-01-01",
		"date_of_joining": today(),
		"company": company,
		"user_id": user_email,
		"designation": "Accountant",
		"status": "Active",
	})
	doc.flags.ignore_permissions = True
	doc.insert()
	return doc.name


def test_01_customer_setup():
	cust = _ensure_customer()
	_shared["customer"] = cust
	assert frappe.db.exists("Customer", cust), "Customer not created"


def test_02_employee_setup():
	emp = _ensure_employee()
	_shared["employee"] = emp
	assert frappe.db.exists("Employee", emp), "Employee not created"


def test_03_origination_create():
	cust = _shared["customer"]
	emp = _shared["employee"]

	orig_name = frappe.db.get_value(
		"Alpha Assignment Origination",
		{"assignment_title": "Test Tax Filing Integration"},
		"name",
	)
	if orig_name:
		_shared["origination"] = orig_name
		return

	orig = frappe.get_doc({
		"doctype": "Alpha Assignment Origination",
		"customer": cust,
		"client_name": cust,
		"assignment_title": "Test Tax Filing Integration",
		"assignment_description": "Test Tax Filing for integration test",
		"service_line": "Tax Compliance",
		"date_received": today(),
		"received_by": frappe.session.user,
		"acceptance_status": "Draft",
	})
	orig.flags.ignore_permissions = True
	orig.insert()
	assert orig.name, "Origination not created"
	assert orig.date_received == today(), "date_received not auto-set"
	assert orig.received_by == frappe.session.user, "received_by not auto-set"
	frappe.db.set_value("Alpha Assignment Origination", orig.name, "acceptance_status", "Approved")
	frappe.db.set_value("Alpha Assignment Origination", orig.name, "workflow_state", "Approved")
	frappe.db.commit()
	_shared["origination"] = orig.name


def test_04_origination_to_project():
	orig_name = _shared["origination"]

	project_name = frappe.db.get_value(
		"Project", {"custom_assignment_origination": orig_name}, "name"
	)
	if not project_name:
		result = frappe.call(
			"alpha_assignment_mgmt.overrides.assignment_origination.create_project_from_origination",
			origination_name=orig_name,
		)
		if isinstance(result, dict):
			project_name = result.get("project_name") or result.get("name")
		else:
			project_name = result

	assert project_name, "Project not created from origination"
	project = frappe.get_doc("Project", project_name)
	assert project.customer, "Project missing customer"
	assert project.custom_assignment_origination == orig_name, "Project not linked to origination"
	_shared["project"] = project_name


def test_05_template_task_generation():
	project_name = _shared["project"]
	tasks = frappe.get_all("Task", filters={"project": project_name})
	assert len(tasks) >= 10, f"Expected >= 10 tasks from template, got {len(tasks)}"
	has_review = any(
		frappe.db.get_value("Task", t.name, "custom_requires_review")
		for t in tasks
	)
	assert has_review, "No tasks have requires_review flag"


def test_06_sla_creation():
	project_name = _shared["project"]
	orig_name = _shared["origination"]

	existing = frappe.db.get_value("Alpha Engagement SLA", {"project": project_name}, "name")
	if existing:
		_shared["sla"] = existing
		return

	sla = frappe.get_doc({
		"doctype": "Alpha Engagement SLA",
		"sla_level": "SLA C - Monthly Bookkeeping",
		"project": project_name,
		"assignment_origination": orig_name,
		"client_due_date": add_days(today(), 30),
		"alpha_processing_deadline": add_days(today(), 20),
		"review_deadline": add_days(today(), 25),
		"escalation_date": add_days(today(), 28),
	})
	sla.flags.ignore_permissions = True
	sla.insert()
	frappe.db.commit()
	_shared["sla"] = sla.name

	sla_link = frappe.db.get_value("Project", project_name, "custom_engagement_sla")
	assert sla_link == sla.name, f"SLA not linked to project: expected {sla.name}, got {sla_link}"


def test_07_document_request_auto_create():
	project_name = _shared["project"]
	reqs = frappe.get_all("Document Request Register", filters={"project": project_name})
	assert len(reqs) >= 1, "Document Requests not auto-created from service lines"


def test_08_review_gate_create():
	project_name = _shared["project"]
	tasks = frappe.get_all(
		"Task",
		filters={"project": project_name, "custom_requires_review": 1},
		limit=1,
	)
	if not tasks:
		return

	existing = frappe.db.get_value(
		"Review Gate Register", {"task": tasks[0].name}, "name"
	)
	if existing:
		return

	gate = frappe.get_doc({
		"doctype": "Review Gate Register",
		"task": tasks[0].name,
		"project": project_name,
		"reviewer": frappe.session.user,
		"review_date": today(),
		"approval_status": "Pending",
	})
	gate.flags.ignore_permissions = True
	gate.insert()
	assert gate.name, "Review Gate not created"


def test_09_client_delay_log():
	project_name = _shared["project"]
	tasks = frappe.get_all(
		"Task",
		filters={"project": project_name, "status": ["not in", ["Completed", "Cancelled"]]},
		limit=1,
	)
	if not tasks:
		return

	task_name = tasks[0].name
	frappe.db.set_value("Task", task_name, "status", "Waiting for Client")
	frappe.db.commit()
	delay = frappe.db.get_value("Client Delay Log", {"task": task_name}, "name")
	assert delay, "Client Delay Log not auto-created when task set to Waiting for Client"

	frappe.db.set_value("Task", task_name, "status", "Open")
	frappe.db.commit()


def test_10_risk_register():
	project_name = _shared["project"]
	cust = _shared["customer"]
	risk = frappe.get_doc({
		"doctype": "Client Risk Register",
		"project": project_name,
		"customer": cust,
		"risk_type": "Financial",
		"risk_description": "Test risk for integration",
		"likelihood": "Medium",
		"impact": "Medium",
		"status": "Open",
	})
	risk.flags.ignore_permissions = True
	risk.insert()
	assert risk.name, "Risk Register not created"


def test_11_closure_certificate_gates():
	project_name = _shared["project"]
	orig_name = _shared["origination"]
	user_id = frappe.db.get_value("Employee", _shared["employee"], "user_id")

	cert = frappe.get_doc({
		"doctype": "Assignment Closure Certificate",
		"project": project_name,
		"assignment_origination": orig_name,
		"prepared_by": user_id or frappe.session.user,
		"status": "Draft",
		"all_tasks_complete": 0,
	})
	cert.flags.ignore_permissions = True
	cert.insert()

	cert.status = "Approved"
	threw = False
	try:
		cert.validate()
	except frappe.ValidationError:
		threw = True
	assert threw, "Closure gate should block incomplete project"


def test_12_performance_feedback():
	emp = _shared["employee"]
	fb = frappe.get_doc({
		"doctype": "Performance Feedback",
		"employee": emp,
		"feedback_from": frappe.db.get_value("Employee", emp, "employee_name") or "Test Employee",
		"feedback_type": "Reviewer Feedback",
		"feedback_date": today(),
		"rating": "Good",
		"strengths": "Strong technical skills",
		"improvements": "Communication",
		"status": "Draft",
	})
	fb.flags.ignore_permissions = True
	fb.insert()
	assert fb.name, "Performance Feedback not created"


def test_13_timesheet_custom_fields():
	meta = frappe.get_meta("Timesheet Detail")
	fieldnames = [f.fieldname for f in meta.fields]
	for f in ["custom_is_billable", "custom_output_note", "custom_evidence_reference", "custom_client_delay_flag"]:
		assert f in fieldnames, f"Timesheet Detail missing field: {f}"
