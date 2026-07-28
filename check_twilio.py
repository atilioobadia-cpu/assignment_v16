import frappe

def execute():
    settings = frappe.get_doc("TP Twilio Settings")
    print("Enabled:", settings.enabled)
    print("Account SID:", settings.account_sid)
    print("Record Calls:", settings.record_calls)
