import frappe


def fix_workflow_state_allow_on_submit():
    field_name = frappe.db.get_value(
        "DocField",
        {"parent": "Alpha Assignment Origination", "fieldname": "workflow_state"},
        "name",
    )
    if field_name:
        frappe.db.set_value("DocField", field_name, "allow_on_submit", 1)

    frappe.get_doc(
        {
            "doctype": "Property Setter",
            "doctype_or_field": "DocField",
            "doc_type": "Alpha Assignment Origination",
            "field_name": "workflow_state",
            "property": "allow_on_submit",
            "value": 1,
            "property_type": "Check",
        }
    ).insert(ignore_permissions=True)
    frappe.db.commit()
    print("Fixed workflow_state allow_on_submit")
    frappe.clear_cache(doctype="Alpha Assignment Origination")
