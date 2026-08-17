import frappe


def create_sales_order(project):
    """Auto-create Sales Order when a new Project is created."""
    if not project.customer:
        return
    if frappe.db.get_value("Sales Order", {"custom_project": project.name}):
        return

    item_code = _get_service_item()
    if not item_code:
        return

    rate = _get_service_rate(project)

    so = frappe.new_doc("Sales Order")
    so.customer = project.customer
    so.delivery_date = project.expected_end_date or frappe.utils.today()
    so.custom_project = project.name
    so.company = frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company")
    so.append("items", {
        "item_code": item_code,
        "qty": 1,
        "rate": rate,
        "delivery_date": so.delivery_date,
    })
    so.flags.ignore_permissions = True
    so.insert()

    project.db_set("custom_sales_order", so.name)
    project.db_set("custom_billing_status", "Not Billed")

    _notify_billing_team(project, so)


def _get_service_item():
    """Return the default AIMS service item, creating it if needed."""
    item_code = "AIMS Professional Services"
    if not frappe.db.exists("Item", item_code):
        doc = frappe.new_doc("Item")
        doc.item_code = item_code
        doc.item_name = "AIMS Professional Services"
        doc.item_type = "Service"
        doc.is_stock_item = 0
        doc.description = "Professional services provided by Alpha Associates"
        doc.stock_uom = "Nos"
        doc.flags.ignore_permissions = True
        doc.insert()
    return item_code


def _get_service_rate(project):
    """Get rate from Origination's proposed_fee, then Service Contract, default to 0."""
    orig_name = frappe.db.get_value("Project", project.name, "custom_assignment_origination")
    if orig_name:
        proposed_fee = frappe.db.get_value("Alpha Assignment Origination", orig_name, "proposed_fee")
        if proposed_fee:
            return proposed_fee

    contract = frappe.db.get_value(
        "Alpha Service Contract",
        {"customer": project.customer, "docstatus": 1, "status": "Active"},
        "name",
    )
    if contract:
        contract_doc = frappe.get_cached_doc("Alpha Service Contract", contract)
        if contract_doc.get("items") and len(contract_doc.items) > 0:
            return contract_doc.items[0].rate
    return 0


def _notify_billing_team(project, so):
    """Notify billing/accounts team about new Sales Order."""
    billing_users = frappe.get_all(
        "Has Role",
        filters={"role": "Accounts Manager", "parenttype": "User"},
        pluck="parent",
        distinct=True,
    )
    for user_id in billing_users:
        email = frappe.db.get_value("User", user_id, "email")
        if email:
            try:
                frappe.sendmail(
                    recipients=[email],
                    subject=f"[AIMS] Sales Order Created: {so.name}",
                    message=(
                        f"<h3>New Sales Order</h3>"
                        f"<p>Sales Order <b>{so.name}</b> has been auto-created for Project <b>{project.name}</b>.</p>"
                        f"<p>Customer: <b>{project.customer}</b></p>"
                        f"<p>Amount: <b>{so.total}</b></p>"
                        f"<p><a href='/app/sales-order/{so.name}'>View Sales Order</a></p>"
                    ),
                )
            except Exception:
                pass


def create_invoice_from_closure(closure):
    """Auto-create Sales Invoice when Closure Certificate is approved."""
    if not closure.project:
        return

    project = frappe.get_cached_doc("Project", closure.project)
    so_name = project.custom_sales_order

    if not so_name:
        return

    if frappe.db.get_value("Sales Invoice", {"custom_project": project.name}):
        return

    so = frappe.get_cached_doc("Sales Order", so_name)

    si = frappe.new_doc("Sales Invoice")
    si.customer = so.customer
    si.project = project.name
    si.custom_project = project.name
    si.sales_order = so_name
    si.company = so.company
    si.posting_date = frappe.utils.today()

    for item in so.items:
        si.append("items", {
            "item_code": item.item_code,
            "qty": item.qty,
            "rate": item.rate,
            "amount": item.amount,
            "sales_order": so_name,
            "so_detail": item.name,
            "delivery_date": item.delivery_date,
        })

    si.flags.ignore_permissions = True
    si.insert()

    project.db_set("custom_sales_invoice", si.name)
    project.db_set("custom_billing_status", "Fully Billed")

    _notify_client_invoice_ready(project, si)


def _notify_client_invoice_ready(project, si):
    """Notify client about new invoice via their portal user."""
    portal_user = frappe.db.get_value("Customer", project.customer, "custom_portal_user")
    if portal_user:
        email = frappe.db.get_value("User", portal_user, "email")
        if email:
            try:
                frappe.sendmail(
                    recipients=[email],
                    subject=f"[AIMS] Invoice Ready: {si.name}",
                    message=(
                        f"<h3>Invoice for {project.name}</h3>"
                        f"<p>Dear Client,</p>"
                        f"<p>Your invoice <b>{si.name}</b> for project <b>{project.name}</b> is ready.</p>"
                        f"<p>Amount: <b>{si.grand_total}</b></p>"
                    ),
                )
            except Exception:
                pass
