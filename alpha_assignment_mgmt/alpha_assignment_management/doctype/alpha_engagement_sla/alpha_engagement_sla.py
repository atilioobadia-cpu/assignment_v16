import frappe
from frappe.model.document import Document
from frappe.utils import today

class AlphaEngagementSLA(Document):
    def validate(self):
        if self.alpha_processing_deadline and self.alpha_processing_deadline < today():
            if self.status != "Closed":
                self.status = "Breached"
                self.breach_notified = 1
