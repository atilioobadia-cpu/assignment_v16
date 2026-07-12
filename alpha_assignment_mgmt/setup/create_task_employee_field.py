import frappe


def execute():
	frappe.reload_doctype("Task", force=True)
	if not frappe.db.exists("Custom Field", {"dt": "Task", "fieldname": "custom_task_employee_log"}):
		frappe.get_doc({
			"doctype": "Custom Field",
			"dt": "Task",
			"fieldname": "custom_task_employee_log",
			"fieldtype": "Table",
			"label": "Employee Log",
			"options": "Task Employee Log",
			"insert_after": "custom_deps_cb",
			"description": "Track which employees contributed to completing this task",
		}).insert(ignore_permissions=True)
		frappe.db.commit()
		print("Custom field created on Task")
	else:
		print("Custom field already exists")
