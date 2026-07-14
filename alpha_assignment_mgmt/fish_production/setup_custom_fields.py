import frappe, json

def execute():
    with open("/home/unix/frappe-bench/apps/alpha_assignment_mgmt/alpha_assignment_mgmt/fish_production/fixtures/custom_fields_fish.json") as f:
        fields = json.load(f)

    for field in fields:
        dt = field["dt"]
        fieldname = field["fieldname"]
        exists = frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fieldname})
        if not exists:
            cf = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": dt,
                "fieldname": fieldname,
                "fieldtype": field.get("fieldtype", "Data"),
                "label": field.get("label", ""),
                "insert_after": field.get("insert_after", ""),
                "options": field.get("options", ""),
                "default": field.get("default", ""),
                "description": field.get("description", ""),
            })
            cf.insert(ignore_permissions=True)
            print(f"Created: {dt}.{fieldname}")
        else:
            print(f"Exists:  {dt}.{fieldname}")

    frappe.db.commit()
    print("Done!")
