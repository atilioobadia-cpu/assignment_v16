import frappe
from frappe.utils import now_datetime, add_days


def daily_review_gate_escalation_check():
    """Escalate Review Gates that have been pending too long."""
    pending_gates = frappe.get_all(
        "Review Gate Register",
        filters={
            "approval_status": "Pending",
            "docstatus": 1,
        },
        fields=["name", "task", "project", "reviewer", "creation", "preparer"],
    )

    for gate in pending_gates:
        days_pending = (now_datetime() - gate.creation).days

        if days_pending < 2:
            continue

        if days_pending >= 5:
            _escalate_gate(gate, "Level 3 - Partner/Director")
        elif days_pending >= 3:
            _escalate_gate(gate, "Level 2 - Branch Manager")
        else:
            _escalate_gate(gate, "Level 1 - Engagement Manager")


def _escalate_gate(gate, level):
    """Escalate a review gate to the next level."""
    frappe.db.set_value("Review Gate Register", gate.name, "approval_status", "Escalated")

    recipient = None
    project = frappe.get_cached_doc("Project", gate.project) if gate.project else None

    if level == "Level 1 - Engagement Manager" and project:
        recipient = project.custom_engagement_manager
    elif level == "Level 2 - Branch Manager" and project:
        recipient = project.custom_branch_manager
    elif level == "Level 3 - Partner/Director":
        partner_users = frappe.get_all(
            "Has Role",
            filters={"role": "Alpha Partner/Director", "parenttype": "User"},
            pluck="parent",
            distinct=True,
        )
        for user_id in partner_users:
            email = frappe.db.get_value("User", user_id, "email")
            if email:
                _send_escalation_email(email, gate, level)
        return

    if recipient:
        email = frappe.db.get_value("User", recipient, "email")
        if email:
            _send_escalation_email(email, gate, level)


def _send_escalation_email(email, gate, level):
    try:
        frappe.sendmail(
            recipients=[email],
            subject=f"[AIMS] Review Gate Escalation: {gate.name}",
            message=(
                f"<h3>Review Gate Escalation</h3>"
                f"<p>Review Gate <b>{gate.name}</b> has been escalated to <b>{level}</b>.</p>"
                f"<p>Task: <b>{gate.task}</b></p>"
                f"<p>Project: <b>{gate.project or 'N/A'}</b></p>"
                f"<p>Please review and take action.</p>"
            ),
        )
    except Exception:
        pass
