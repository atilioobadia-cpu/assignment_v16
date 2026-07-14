import frappe
from frappe.model.document import Document


class BreedingCycle(Document):
    def validate(self):
        self.calculate_totals()
        self.set_default_warehouses()

    def calculate_totals(self):
        self.total_broodstock = (self.male_count or 0) + (self.female_count or 0)
        if self.eggs_collected and self.hatching_rate:
            self.fry_collected = int(self.eggs_collected * self.hatching_rate / 100)
        if self.fingerlings_produced and self.total_broodstock:
            self.survival_rate = (self.fingerlings_produced / self.total_broodstock) * 100
        total_mort = frappe.db.sql("""
            SELECT COALESCE(SUM(mortality_today), 0) as total
            FROM `tabGrowth Sampling`
            WHERE batch_no IN (SELECT name FROM `tabBatch` WHERE custom_breeding_cycle = %s)
        """, self.name, as_dict=True)
        if total_mort:
            self.total_mortality = total_mort[0].total
        if self.fingerlings_produced and self.total_cost:
            self.cost_per_fingerling = self.total_cost / self.fingerlings_produced

    def set_default_warehouses(self):
        if not self.hatchery_warehouse:
            self.hatchery_warehouse = "Hatchery / Nursery - TBBCL"
        if not self.grow_out_warehouse:
            self.grow_out_warehouse = "Harvested Fish - Kasamiko - TBBCL"

    def on_update(self):
        if self.status == "Draft" and not self.work_order:
            self.create_work_order()

    def create_work_order(self):
        """Auto-create Work Order when breeding cycle is created"""
        bom_name = frappe.db.get_value(
            "BOM", {"item": "FNG-STD", "is_default": 1, "docstatus": 1}, "name"
        )
        if not bom_name:
            return

        wip_wh = ""
        if self.pond:
            loc = frappe.db.get_value("Location", self.pond, "custom_cost_center")
            wip_wh = frappe.db.get_value(
                "Warehouse", {"warehouse_name": ["like", "%Hatchery%"]}, "name"
            ) or ""

        wo = frappe.get_doc({
            "doctype": "Work Order",
            "production_item": "FNG-STD",
            "bom_no": bom_name,
            "qty": self.fry_collected or 1000,
            "company": "The Big Best Company Limited",
            "wip_warehouse": wip_wh,
            "fg_warehouse": self.hatchery_warehouse or "",
            "planned_start_date": self.stocking_date,
            "planned_end_date": self.treatment_end_date,
            "description": f"Breeding Cycle: {self.name} - {self.fish_type}",
        })
        wo.insert(ignore_permissions=True)
        frappe.db.set_value("Breeding Cycle", self.name, "work_order", wo.name)
