import frappe
import datetime


@frappe.whitelist()
def produce_fingerlings(cycle_name):
    """Called from client script to produce fingerlings - creates batch and stock entries"""
    cycle = frappe.get_doc("Breeding Cycle", cycle_name)

    if not cycle.fingerlings_produced:
        frappe.throw("Please enter fingerlings produced count first")

    company = "The Big Best Company Limited"

    # Create output batch with qty 0 - Material Receipt will set the actual qty
    batch_id = f"BATCH-FNG-{datetime.datetime.now().year}-{cycle.name}"

    batch = frappe.get_doc({
        "doctype": "Batch",
        "item": "FNG-STD",
        "batch_id": batch_id,
        "manufacturing_date": frappe.utils.today(),
        "batch_qty": 0,
        "custom_breeding_cycle": cycle.name,
        "custom_sex_reversal_applied": cycle.sex_reversal_done or 0,
        "custom_avg_weight_grams": cycle.avg_weight_grams or 0,
        "description": f"Fingerlings from {cycle.name} - {cycle.fish_type}"
    })
    batch.insert(ignore_permissions=True)

    # Calculate cost per fingerling from all linked stock entries
    total_cost = frappe.db.sql("""
        SELECT COALESCE(SUM(debit), 0) as total
        FROM `tabGL Entry`
        WHERE voucher_type = 'Stock Entry'
        AND voucher_no IN (
            SELECT parent FROM `tabStock Entry Detail` WHERE batch_no IN (
                SELECT name FROM `tabBatch` WHERE custom_breeding_cycle = %s
            )
        )
    """, cycle.name, as_dict=True)

    cost = total_cost[0].total if total_cost else 0

    # Create stock entry: issue nursery stock
    nursery_wh = cycle.hatchery_warehouse or "Hatchery / Nursery - TBBCL"

    if nursery_wh and cycle.parent_batch:
        try:
            se_issue = frappe.get_doc({
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Issue",
                "company": company,
                "items": [{
                    "item_code": "FNG-STD",
                    "qty": cycle.fingerlings_produced,
                    "s_warehouse": nursery_wh,
                    "batch_no": cycle.parent_batch,
                }]
            })
            se_issue.insert(ignore_permissions=True)
            se_issue.submit()
        except Exception:
            pass

    # Create stock entry: receive at hatchery
    try:
        se_receive = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Receipt",
            "company": company,
            "items": [{
                "item_code": "FNG-STD",
                "qty": cycle.fingerlings_produced,
                "t_warehouse": cycle.hatchery_warehouse or "Hatchery / Nursery - TBBCL",
                "batch_no": batch.name,
            }]
        })
        se_receive.insert(ignore_permissions=True)
        se_receive.submit()
    except Exception:
        pass

    # Update cycle
    frappe.db.set_value("Breeding Cycle", cycle.name, {
        "output_batch": batch.name,
        "total_cost": cost,
        "status": "Fingerlings Ready"
    })

    return {"batch": batch.name, "cost": cost}
