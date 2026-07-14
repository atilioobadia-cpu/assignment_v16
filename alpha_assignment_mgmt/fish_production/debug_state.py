import frappe

def run():
    spw = frappe.get_all("Spawning Record", fields=["name", "fry_batch", "fry_collected", "nursery_stock_entry"], limit_page_length=0)
    print("Spawning Records:")
    for s in spw:
        print(f"  {s.name}: fry_batch={s.fry_batch}, fry_collected={s.fry_collected}, stock_entry={s.nursery_stock_entry}")

    batches = frappe.get_all("Batch", {"item": "FNG-STD"}, ["name", "batch_id", "batch_qty", "custom_breeding_cycle", "disabled"], limit_page_length=0)
    print("\nBatches (FNG-STD):")
    for b in batches:
        print(f"  {b.name}: qty={b.batch_qty}, cycle={b.custom_breeding_cycle}, disabled={b.disabled}")

    cycles = frappe.get_all("Breeding Cycle", ["name", "status", "parent_batch", "output_batch", "fry_collected", "fingerlings_produced"], limit_page_length=0)
    print("\nBreeding Cycles:")
    for c in cycles:
        print(f"  {c.name}: status={c.status}, parent={c.parent_batch}, output={c.output_batch}, fry={c.fry_collected}, produced={c.fingerlings_produced}")

    ses = frappe.db.sql("""
        SELECT se.name, se.stock_entry_type, se.docstatus
        FROM `tabStock Entry` se
        JOIN `tabStock Entry Detail` sed ON sed.parent = se.name
        WHERE sed.item_code = 'FNG-STD' AND se.docstatus = 1
        GROUP BY se.name ORDER BY se.creation DESC LIMIT 10
    """, as_dict=True)
    print(f"\nSubmitted Stock Entries (FNG-STD): {len(ses)}")
    for se in ses:
        print(f"  {se.name}: {se.stock_entry_type}")
