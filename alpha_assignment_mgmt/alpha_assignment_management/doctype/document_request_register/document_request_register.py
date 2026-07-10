import frappe
from frappe.model.document import Document
from frappe.utils import today

class DocumentRequestRegister(Document):
    def validate(self):
        if not self.requested_date:
            self.requested_date = today()
        if not self.requested_by:
            self.requested_by = frappe.session.user
