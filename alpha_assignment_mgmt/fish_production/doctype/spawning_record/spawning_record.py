import frappe
from frappe.model.document import Document


class SpawningRecord(Document):
    def validate(self):
        self.calculate_fry()
        self.set_fish_type()

    def calculate_fry(self):
        if self.eggs_collected and self.hatching_rate:
            self.fry_collected = int(self.eggs_collected * self.hatching_rate / 100) - (
                self.mortality_at_collection or 0
            )
            if self.fry_collected < 0:
                self.fry_collected = 0

    def set_fish_type(self):
        if self.breeding_cycle and not self.fish_type:
            self.fish_type = frappe.db.get_value("Breeding Cycle", self.breeding_cycle, "fish_type")

    def on_update(self):
        if self.fry_collected and not self.fry_batch:
            self.create_fry_batch()
            self.create_nursery_transfer()
            self.update_breeding_cycle()

    def create_fry_batch(self):
        """Create a batch for the collected fry"""
        import datetime

        batch = frappe.get_doc(
            {
                "doctype": "Batch",
                "item": "FNG-STD",
                "batch_id": f"BATCH-FRY-{frappe.utils.now_datetime().year}-{self.name}",
                "manufacturing_date": self.spawning_date,
                "batch_qty": self.fry_collected,
                "description": f"Fry from {self.name} - {self.fish_type}",
            }
        )
        batch.insert(ignore_permissions=True)
        frappe.db.set_value("Spawning Record", self.name, "fry_batch", batch.name)

    def create_nursery_transfer(self):
        """Create Stock Entry to transfer fry to nursery"""
        if not self.nursery_tank:
            return

        cycle = frappe.db.get_value("Breeding Cycle", self.breeding_cycle,
            ["hatchery_warehouse", "pond"], as_dict=True)
        nursery_wh = cycle.hatchery_warehouse if cycle else ""
        if not nursery_wh:
            return

        pond_wh = frappe.db.get_value("Warehouse", {"warehouse_name": ["like", "%Hatchery%"]}, "name") if not nursery_wh else ""
        if not pond_wh:
            pond_wh = "Stores - TBBCL"

        cost_center = (
            frappe.db.get_value("Location", self.nursery_tank, "custom_cost_center")
            or "Nursery - Kasamiko - TBBCL"
        )

        try:
            se = frappe.get_doc(
                {
                    "doctype": "Stock Entry",
                    "stock_entry_type": "Material Transfer",
                    "company": "The Big Best Company Limited",
                    "items": [
                        {
                            "item_code": "FNG-STD",
                            "qty": self.fry_collected,
                            "s_warehouse": pond_wh,
                            "t_warehouse": nursery_wh,
                            "batch_no": self.fry_batch,
                        }
                    ],
                }
            )
            se.insert(ignore_permissions=True)
            se.submit()
            frappe.db.set_value("Spawning Record", self.name, "nursery_stock_entry", se.name)
        except Exception:
            pass

    def update_breeding_cycle(self):
        """Update parent breeding cycle with spawning data"""
        bc = frappe.get_doc("Breeding Cycle", self.breeding_cycle)
        frappe.db.set_value(
            "Breeding Cycle",
            self.breeding_cycle,
            {
                "fry_collected": self.fry_collected,
                "spawning_date": self.spawning_date,
                "nursery_tank": self.nursery_tank,
                "treatment_start_date": self.treatment_start_date,
                "treatment_end_date": self.treatment_end_date,
                "status": "Spawning Complete",
            },
        )
