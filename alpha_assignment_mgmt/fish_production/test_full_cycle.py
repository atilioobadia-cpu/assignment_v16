"""
Full Fish Production Cycle Test - Demo Data & Verification
Run: bench --site tbbcl.local execute alpha_assignment_mgmt.fish_production.test_full_cycle.run
"""
import frappe

COMPANY = "The Big Best Company Limited"

def run():
    print("=" * 60)
    print("FISH PRODUCTION FULL CYCLE TEST")
    print("=" * 60)

    # Step 1: Ensure infrastructure exists
    print("\n[1/8] Verifying infrastructure...")
    ensure_locations()
    ensure_warehouses()
    ensure_items()

    # Step 2: Create a breeding cycle
    print("\n[2/8] Creating Breeding Cycle...")
    cycle = create_breeding_cycle()
    print(f"  Created: {cycle.name}")

    # Step 3: Verify Work Order auto-created
    print("\n[3/8] Verifying auto-created Work Order...")
    wo = frappe.db.get_value("Work Order", {"custom_breeding_cycle": cycle.name}, "name")
    if wo:
        print(f"  Work Order created: {wo}")
    else:
        print("  INFO: No Work Order auto-created (may need BOM)")

    # Step 4: Create output batch (before sampling so batch_no is available)
    print("\n[4/8] Creating Output Batch...")
    batch = create_output_batch(cycle.name)
    print(f"  Batch: {batch.name}, qty: {batch.batch_qty}")

    # Step 5: Create Spawning Record
    print("\n[5/8] Creating Spawning Record...")
    spawning = create_spawning_record(cycle.name)
    print(f"  Created: {spawning.name}")
    print(f"  Fry collected: {spawning.fry_collected}")

    # Step 6: Create Growth Samplings
    print("\n[6/8] Creating Growth Sampling Records...")
    for day, weight, count in [(7, 0.02, 480000), (14, 0.05, 460000), (21, 0.12, 440000), (28, 0.25, 420000)]:
        gs = create_growth_sampling(cycle.name, batch.name, day, weight, count)
        print(f"  Day {day}: avg_wt={weight}g, count={count}, survival={gs.survival_rate:.1f}%")

    # Step 7: Check GL entries
    print("\n[7/8] Checking GL Entries...")
    check_gl_entries()

    # Step 8: Summary
    print("\n[8/8] TEST SUMMARY")
    print("-" * 40)
    print(f"  Breeding Cycle: {cycle.name}")
    print(f"  Spawning Record: {spawning.name}")
    print(f"  Work Order: {wo or 'None (no BOM found)'}")
    print(f"  Output Batch: {batch.name}")
    print(f"  Survival Rate: {cycle.survival_rate:.1f}%")
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


def ensure_locations():
    locations = [
        ("Broodstock Pond 1", "Broodstock", 500.0),
        ("Broodstock Pond 2", "Broodstock", 500.0),
        ("Nursery Tank 1", "Nursery", 50.0),
        ("Nursery Tank 2", "Nursery", 50.0),
        ("Cage 1 - Lake", "Grow-Out", 1000.0),
    ]
    for loc_name, pond_type, capacity in locations:
        if frappe.db.exists("Location", loc_name):
            print(f"  Exists: {loc_name}")
        else:
            frappe.get_doc({
                "doctype": "Location",
                "location_name": loc_name,
                "company": COMPANY,
                "custom_pond_type": pond_type,
                "custom_water_capacity_m3": capacity,
            }).insert(ignore_permissions=True)
            print(f"  Created Location: {loc_name}")


def ensure_warehouses():
    for wh_name in ["Hatchery / Nursery - TBBCL", "Feed Store - TBBCL", "Harvested Fish - Kasamiko - TBBCL"]:
        if frappe.db.exists("Warehouse", wh_name):
            print(f"  Exists: {wh_name}")
        else:
            try:
                frappe.get_doc({
                    "doctype": "Warehouse",
                    "warehouse_name": wh_name.replace(" - TBBCL", ""),
                    "company": COMPANY,
                    "parent_warehouse": "All Warehouses - TBBCL",
                }).insert(ignore_permissions=True)
                print(f"  Created Warehouse: {wh_name}")
            except Exception as e:
                print(f"  Skipped warehouse {wh_name}: {e}")


def ensure_items():
    for code, name, group in [
        ("FNG-STD", "Standard Fingerling (2-3g)", "Stock"),
        ("FEED-START", "Starter Feed (0.5mm)", "Stock"),
        ("FEED-GROW", "Grower Feed (2mm)", "Stock"),
        ("FEED-FIN", "Finisher Feed (4mm)", "Stock"),
    ]:
        if frappe.db.exists("Item", code):
            print(f"  Exists: {code}")
        else:
            frappe.get_doc({
                "doctype": "Item",
                "item_code": code,
                "item_name": name,
                "item_group": group,
                "stock_uom": "Nos",
                "is_stock_item": 1,
            }).insert(ignore_permissions=True)
            print(f"  Created Item: {code}")


def create_breeding_cycle():
    existing = frappe.get_list("Breeding Cycle", {"fish_type": "Tilapia", "status": ["!=", "Closed"]}, pluck="name")
    if existing:
        print(f"  Using existing cycle: {existing[0]}")
        return frappe.get_doc("Breeding Cycle", existing[0])

    doc = frappe.get_doc({
        "doctype": "Breeding Cycle",
        "breeding_cycle_name": "BC-TIL-2026-Q3",
        "fish_type": "Tilapia",
        "status": "In Progress",
        "stocking_date": frappe.utils.add_days(frappe.utils.today(), -40),
        "spawning_date": frappe.utils.add_days(frappe.utils.today(), -10),
        "treatment_start_date": frappe.utils.add_days(frappe.utils.today(), -5),
        "treatment_end_date": frappe.utils.add_days(frappe.utils.today(), 23),
        "male_count": 100,
        "female_count": 400,
        "pond": "Broodstock Pond 1",
        "nursery_tank": "Nursery Tank 1",
        "hatchery_warehouse": "Hatchery / Nursery - TBBCL",
        "grow_out_warehouse": "Harvested Fish - Kasamiko - TBBCL",
        "eggs_collected": 500000,
        "hatching_rate": 85.0,
        "total_broodstock": 500,
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc


def create_spawning_record(cycle_name):
    existing = frappe.get_list("Spawning Record", {"breeding_cycle": cycle_name}, pluck="name")
    if existing:
        return frappe.get_doc("Spawning Record", existing[0])

    doc = frappe.get_doc({
        "doctype": "Spawning Record",
        "breeding_cycle": cycle_name,
        "spawning_date": frappe.utils.add_days(frappe.utils.today(), -10),
        "eggs_collected": 500000,
        "hatching_rate": 85.0,
        "fry_collected": 425000,
        "nursery_tank": "Nursery Tank 1",
        "treatment_start_date": frappe.utils.add_days(frappe.utils.today(), -5),
        "treatment_end_date": frappe.utils.add_days(frappe.utils.today(), 23),
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc


def create_growth_sampling(cycle_name, batch_name, day, avg_weight, count):
    doc = frappe.get_doc({
        "doctype": "Growth Sampling",
        "batch_no": batch_name,
        "sampling_date": frappe.utils.add_days(frappe.utils.today(), day - 40),
        "location": "Nursery Tank 1",
        "sample_size": 50,
        "avg_weight_grams": avg_weight,
        "estimated_count": count,
        "survival_rate": (count / 425000) * 100,
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc


def create_output_batch(cycle_name):
    existing = frappe.get_list("Batch", {"custom_breeding_cycle": cycle_name}, pluck="name")
    if existing:
        return frappe.get_doc("Batch", existing[0])

    import datetime
    batch_id = f"BATCH-FNG-{datetime.datetime.now().year}-{cycle_name}"

    doc = frappe.get_doc({
        "doctype": "Batch",
        "item": "FNG-STD",
        "batch_id": batch_id,
        "manufacturing_date": frappe.utils.today(),
        "batch_qty": 420000,
        "custom_breeding_cycle": cycle_name,
        "custom_sex_reversal_applied": 1,
        "custom_avg_weight_grams": 0.25,
        "custom_survival_rate": 98.82,
        "description": f"Fingerlings from {cycle_name} - Nile Tilapia Monosex Male",
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc


def check_gl_entries():
    gl_count = frappe.db.sql("""
        SELECT COUNT(*) as cnt FROM `tabGL Entry`
        WHERE company = %s
        AND posting_date >= DATE_SUB(CURDATE(), INTERVAL 60 DAY)
    """, COMPANY, as_dict=True)
    print(f"  Total GL entries (last 60 days): {gl_count[0].cnt if gl_count else 0}")
