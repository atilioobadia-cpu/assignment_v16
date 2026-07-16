import frappe

@frappe.whitelist()
def get_ceo_top_bottom():
    """Return top 5 and bottom 5 employees by completed tasks."""
    employees = frappe.get_all(
        "Employee",
        filters={"status": "Active", "user_id": ["is", "set"]},
        fields=["name", "employee_name", "user_id"],
    )
    if not employees:
        return {"top5": [], "bottom5": []}

    results = []
    for emp in employees:
        uid = emp.user_id
        completed = frappe.db.sql("""
            SELECT COUNT(DISTINCT t.name)
            FROM tabTask t
            WHERE t.status = 'Completed'
            AND (
                JSON_CONTAINS(t._assign, %s)
                OR t.owner = %s
            )
        """, (frappe.json.dumps(uid), uid))[0][0]

        pending = frappe.db.sql("""
            SELECT COUNT(DISTINCT t.name)
            FROM tabTask t
            WHERE t.status IN ('Open', 'Working', 'Overdue')
            AND (
                JSON_CONTAINS(t._assign, %s)
                OR t.owner = %s
            )
        """, (frappe.json.dumps(uid), uid))[0][0]

        results.append({
            "name": emp.employee_name or emp.name,
            "completed": completed,
            "pending": pending,
        })

    results.sort(key=lambda x: x["completed"], reverse=True)
    return {
        "top5": results[:5],
        "bottom5": list(reversed(results[-5:])) if len(results) >= 5 else list(reversed(results)),
    }
