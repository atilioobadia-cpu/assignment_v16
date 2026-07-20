import frappe
from frappe.model.workflow import apply_workflow


def run():
    wf = frappe.get_doc("Workflow", "Alpha Assignment Origination Workflow")

    print("State doc_statuses:")
    for s in wf.states:
        print(f"  {s.state}: doc_status={s.doc_status}")

    print("\nTransitions:")
    for t in wf.transitions:
        print(f"  {t.state} --[{t.action}]--> {t.next_state}")
        print(f"    allowed={t.allowed}, condition={t.condition}")


def debug_pf():
    """Debug why PF is not being created for PROJ-0032."""
    p = frappe.get_doc("Project", "PROJ-0032")
    print(f"Project status: {p.status}")
    print(f"Closure cert: {p.custom_closure_certificate}")
    
    # Check _auto_create_closure_certificate conditions
    remaining = frappe.db.count("Task",
        filters={"project": p.name, "status": ["not in", ["Completed", "Cancelled"]]})
    cert_exists = frappe.db.exists("Assignment Closure Certificate", {"project": p.name})
    print(f"Remaining tasks: {remaining}")
    print(f"Cert exists: {cert_exists}")
    
    # Check PF
    pfs = frappe.get_all("Performance Feedback", filters={"project": p.name})
    print(f"PFs: {len(pfs)}")
    
    # Try running _auto_create_performance_feedback directly
    from alpha_assignment_mgmt.overrides.project import _auto_create_performance_feedback
    try:
        _auto_create_performance_feedback(p)
        frappe.db.commit()
        print("PF creation attempted")
        pfs2 = frappe.get_all("Performance Feedback", filters={"project": p.name})
        print(f"PFs after: {len(pfs2)}")
    except Exception as e:
        print(f"Error: {e}")
    cust = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": "Debug Test " + frappe.utils.now_datetime().strftime("%H%M%S"),
        "customer_group": "Commercial",
        "customer_type": "Company",
        "territory": "All Territories",
        "custom_engagement_manager": "Administrator",
        "custom_client_owner": "Administrator",
        "custom_branch_manager": "Administrator",
        "custom_service_line": "Tax Compliance",
        "custom_risk_rating": "Medium",
        "custom_sector": "Financial Services",
        "custom_tin": "TIN-DEBUG-001",
    })
    cust.flags.ignore_permissions = True
    cust.insert()

    orig = frappe.get_doc({
        "doctype": "Alpha Assignment Origination",
        "customer": cust.name,
        "assignment_title": "Debug Test",
        "service_line": "Tax Compliance",
        "date_received": frappe.utils.today(),
        "regulatory_deadline": frappe.utils.add_days(frappe.utils.today(), 30),
        "received_by": "Administrator",
    })
    orig.flags.ignore_permissions = True
    orig.insert()
    frappe.db.commit()
    print("Created:", orig.name)
    print("Initial docstatus:", orig.docstatus, "workflow_state:", orig.workflow_state)

    for action in ["Submit", "Send to Review", "Approve"]:
        apply_workflow(orig, action)
        frappe.db.commit()
        orig.reload()
        print(f"After '{action}': docstatus={orig.docstatus}, workflow_state={orig.workflow_state}")
        print(f"  project_created={getattr(orig, 'project_created', None)}, project_reference={getattr(orig, 'project_reference', None)}")
        # Check if there's a project linked
        pname = frappe.db.get_value("Project", {"custom_assignment_origination": orig.name}, "name")
        print(f"  Project found: {pname}")

    return orig.name, cust.name
