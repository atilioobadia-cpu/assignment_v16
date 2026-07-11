import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate

class AlphaEngagementSLA(Document):
    def validate(self):
        if self.alpha_processing_deadline and getdate(self.alpha_processing_deadline) < getdate(today()):
            if self.status != "Closed":
                self.status = "Breached"
                self.breach_notified = 1
