import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 200},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Service Line"), "fieldname": "service_line", "fieldtype": "Data", "width": 120},
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 150},
        {"label": _("SO Amount"), "fieldname": "so_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Sales Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": _("Invoiced Amount"), "fieldname": "invoiced_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Billing Status"), "fieldname": "billing_status", "fieldtype": "Data", "width": 100},
        {"label": _("Total Cost (Hours)"), "fieldname": "total_cost", "fieldtype": "Currency", "width": 130},
        {"label": _("Gross Margin"), "fieldname": "gross_margin", "fieldtype": "Currency", "width": 120},
        {"label": _("Margin %"), "fieldname": "margin_pct", "fieldtype": "Percent", "width": 90},
    ]


def get_data(filters):
    conditions = ""
    if filters and filters.get("project"):
        conditions = " WHERE p.name = %(project)s"

    rows = frappe.db.sql(f"""
        SELECT
            p.name AS project,
            p.customer,
            p.custom_service_line AS service_line,
            p.custom_sales_order AS sales_order,
            p.custom_sales_invoice AS sales_invoice,
            p.custom_billing_status AS billing_status
        FROM `tabProject` p
        {conditions}
        ORDER BY p.creation DESC
    """, filters or {}, as_dict=True)

    for row in rows:
        row.so_amount = 0
        if row.sales_order:
            row.so_amount = frappe.db.get_value("Sales Order", row.sales_order, "total") or 0

        row.invoiced_amount = 0
        if row.sales_invoice:
            row.invoiced_amount = frappe.db.get_value("Sales Invoice", row.sales_invoice, "grand_total") or 0

        row.total_cost = _get_project_cost(row.project)

        row.gross_margin = row.invoiced_amount - row.total_cost
        row.margin_pct = 0
        if row.invoiced_amount:
            row.margin_pct = round((row.gross_margin / row.invoiced_amount) * 100, 1)

    return rows


def _get_project_cost(project):
    """Compute total cost from Timesheets linked to the project."""
    data = frappe.db.sql("""
        SELECT COALESCE(SUM(tsd.billing_amount), 0) AS total_billed,
               COALESCE(SUM(tsd.costing_amount), 0) AS total_cost
        FROM `tabTimesheet Detail` tsd
        INNER JOIN `tabTimesheet` ts ON ts.name = tsd.parent
        WHERE ts.docstatus = 1
          AND ts.project = %s
    """, project, as_dict=True)

    if data and data[0].total_cost:
        return data[0].total_cost

    # Fallback: estimate cost from hours * avg cost rate
    total_hours = frappe.db.sql("""
        SELECT COALESCE(SUM(tsd.hours), 0) AS total_hours
        FROM `tabTimesheet Detail` tsd
        INNER JOIN `tabTimesheet` ts ON ts.name = tsd.parent
        WHERE ts.docstatus = 1
          AND ts.project = %s
    """, project)[0][0]

    return total_hours * 50000  # placeholder rate of 50,000 TZS/hour
