import frappe


def on_update_after_submit(doc, method):
    """Auto-create Sales Invoice when Closure Certificate reaches Approved state."""
    if doc.workflow_state == "CC - Approved" and not frappe.db.get_value(
        "Sales Invoice", {"custom_project": doc.project}
    ):
        from alpha_assignment_mgmt.overrides.billing import create_invoice_from_closure
        try:
            create_invoice_from_closure(doc)
        except Exception:
            frappe.log_error(
                f"Failed to auto-create invoice for Closure Certificate {doc.name}",
                "AIMS Billing Error",
            )
