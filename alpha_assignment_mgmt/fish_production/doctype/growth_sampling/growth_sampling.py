import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class GrowthSampling(Document):
    def validate(self):
        self.calculate_metrics()
        self.update_batch_status()
    
    def calculate_metrics(self):
        if not self.batch_no:
            return
        
        batch = frappe.get_doc("Batch", self.batch_no)
        batch_qty = batch.batch_qty or 0
        
        prev = frappe.get_all("Growth Sampling", 
            filters={"batch_no": self.batch_no, "sampling_date": ["<", self.sampling_date]},
            order_by="sampling_date desc",
            fields=["cumulative_mortality"],
            limit=1
        )
        prev_mortality = prev[0].cumulative_mortality if prev else 0
        self.cumulative_mortality = prev_mortality + (self.mortality_today or 0)
        
        original_qty = frappe.db.get_value("Batch", self.batch_no, "batch_qty") or batch_qty
        stock_in = frappe.db.sql("""
            SELECT COALESCE(SUM(qty), 0) as total
            FROM `tabStock Entry Detail`
            WHERE batch_no = %s AND docstatus = 1
        """, self.batch_no, as_dict=True)
        if stock_in and stock_in[0].total:
            original_qty = stock_in[0].total
        
        self.estimated_count = max(0, original_qty - self.cumulative_mortality)
        self.survival_rate = (self.estimated_count / original_qty * 100) if original_qty > 0 else 0
        self.total_biomass_kg = (self.estimated_count * (self.avg_weight_grams or 0)) / 1000
        
        if prev:
            prev_doc = frappe.get_all("Growth Sampling",
                filters={"batch_no": self.batch_no, "sampling_date": ["<", self.sampling_date]},
                order_by="sampling_date desc",
                fields=["avg_weight_grams", "sampling_date"],
                limit=1
            )
            if prev_doc:
                days_diff = (getdate(self.sampling_date) - getdate(prev_doc[0].sampling_date)).days
                if days_diff > 0:
                    self.daily_weight_gain = ((self.avg_weight_grams or 0) - (prev_doc[0].avg_weight_grams or 0)) / days_diff
        
        if self.expected_weight_grams and self.expected_weight_grams > 0:
            self.weight_deviation = ((self.avg_weight_grams or 0) - self.expected_weight_grams) / self.expected_weight_grams * 100
        
        if self.total_feed_to_date and self.total_biomass_kg:
            initial_biomass = (original_qty * 0.003)
            biomass_gain = self.total_biomass_kg - initial_biomass
            if biomass_gain > 0:
                self.fcr_to_date = self.total_feed_to_date / biomass_gain
    
    def update_batch_status(self):
        if not self.batch_no or not self.avg_weight_grams:
            return
        if self.avg_weight_grams < 50:
            new_status = "Nursery"
        elif self.avg_weight_grams < 500:
            new_status = "Grow-Out"
        else:
            new_status = "Harvest Ready"
        
        self.batch_status = new_status
        frappe.db.set_value("Batch", self.batch_no, "custom_avg_weight_grams", self.avg_weight_grams)
        frappe.db.set_value("Batch", self.batch_no, "custom_survival_rate", self.survival_rate)
