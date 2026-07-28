import frappe
from frappe.model.document import Document


class AlphaServiceContractItem(Document):
    def validate(self):
        if self.rate and self.quantity:
            self.amount = self.rate * self.quantity
