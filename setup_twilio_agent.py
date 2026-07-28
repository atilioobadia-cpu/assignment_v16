import frappe

def execute():
    existing = frappe.db.exists("TP Telephony Agent", "Administrator")
    if existing:
        print("Agent already exists:", existing)
        return

    doc = frappe.get_doc({
        "doctype": "TP Telephony Agent",
        "user": "Administrator",
        "default_medium": "Twilio",
        "twilio": 1,
        "twilio_number": "+12184032495",
        "call_receiving_device": "Computer",
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Agent created for Administrator")
