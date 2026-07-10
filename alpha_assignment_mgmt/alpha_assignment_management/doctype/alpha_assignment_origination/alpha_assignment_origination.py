import frappe
from frappe.model.document import Document
from frappe.utils import today

class AlphaAssignmentOrigination(Document):
    def validate(self):
        if not self.date_received:
            self.date_received = today()
        if not self.received_by:
            self.received_by = frappe.session.user
        if not self.acceptance_status:
            self.acceptance_status = "Draft"
