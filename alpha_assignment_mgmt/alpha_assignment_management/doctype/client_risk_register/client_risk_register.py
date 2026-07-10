from frappe.model.document import Document

class ClientRiskRegister(Document):
    def validate(self):
        if not self.status:
            self.status = "Open"
