import re

import frappe


def auto_link_to_task(doc, method):
    """Link incoming Communication to a Task if subject contains #TASK-XXXXX."""
    if doc.reference_doctype and doc.reference_name:
        return

    subject = doc.subject or ""
    match = re.search(r"#(TASK-\d{4}-\d+)", subject)
    if not match:
        return

    task_name = match.group(1)
    if not frappe.db.exists("Task", task_name):
        return

    doc.db_set(
        {"reference_doctype": "Task", "reference_name": task_name},
        update_modified=False,
    )
    frappe.msgprint(
        frappe._("Email linked to {0}").format(task_name),
        indicator="green",
        alert=True,
    )
