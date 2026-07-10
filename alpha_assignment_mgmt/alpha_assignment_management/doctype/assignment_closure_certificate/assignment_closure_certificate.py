from frappe.model.document import Document
from frappe.utils import today

class AssignmentClosureCertificate(Document):
    def validate(self):
        if not self.closure_date:
            self.closure_date = today()
