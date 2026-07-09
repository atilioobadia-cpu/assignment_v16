import frappe
from frappe.utils import now_datetime


def after_install():
    create_roles()
    create_naming_series()
    create_project_types()
    create_activity_types()


def create_roles():
    roles = [
        "Alpha Partner/Director",
        "Alpha Engagement Manager",
        "Alpha Branch Manager",
        "Alpha Client Owner",
        "Alpha Reviewer",
        "Alpha Staff",
        "Alpha HR Admin",
    ]
    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role}).insert(
                ignore_permissions=True
            )


def create_naming_series():
    series_map = {
        "Alpha Assignment Origination": "AAO-.YYYY.-",
        "Alpha Engagement SLA": "AES-.YYYY.-",
        "Document Request Register": "DRR-.YYYY.-",
        "Review Gate Register": "RGR-.YYYY.-",
        "Client Delay Log": "CDL-.YYYY.-",
        "Client Risk Register": "CRR-.YYYY.-",
        "Assignment Closure Certificate": "ACC-.YYYY.-",
    }
    for doctype, series in series_map.items():
        if not frappe.db.get_value(
            "Property Setter",
            {"doc_type": doctype, "property": "naming_series"},
        ):
            frappe.get_doc({
                "doctype": "Property Setter",
                "doctype_or_field": "DocType",
                "doc_type": doctype,
                "property": "naming_series",
                "property_type": "Data",
                "value": series,
                "__islocal": 1,
            }).insert(ignore_permissions=True)


def create_project_types():
    project_types = [
        "Tax Compliance",
        "TRA Support",
        "Audit Readiness",
        "Monthly Bookkeeping",
        "Accounting Reconstruction",
        "Advisory",
        "ERPNext Implementation",
    ]
    for name in project_types:
        if not frappe.db.exists("Project Type", name):
            frappe.get_doc({"doctype": "Project Type", "project_type": name}).insert(
                ignore_permissions=True
            )


def create_activity_types():
    activity_types = [
        "Tax Preparation",
        "Tax Review",
        "Tax Filing",
        "Audit Fieldwork",
        "Audit Review",
        "Bookkeeping Entry",
        "Bookkeeping Review",
        "Reconciliation",
        "Advisory Call",
        "Advisory Report",
        "ERPNext Setup",
        "ERPNext Training",
        "Client Communication",
        "Internal Meeting",
        "Training/CPD",
        "Administrative",
    ]
    for name in activity_types:
        if not frappe.db.exists("Activity Type", name):
            frappe.get_doc({"doctype": "Activity Type", "activity_type": name}).insert(
                ignore_permissions=True
            )
