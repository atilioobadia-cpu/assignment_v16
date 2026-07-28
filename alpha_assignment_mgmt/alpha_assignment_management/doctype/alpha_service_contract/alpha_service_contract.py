import frappe
from frappe.model.document import Document


class AlphaServiceContract(Document):
    def validate(self):
        self.set_renewal_date()
        self.set_contract_status()

    def set_renewal_date(self):
        if self.end_date and self.renewal_auto:
            from frappe.utils import add_days
            self.renewal_date = add_days(self.end_date, -30)

    def set_contract_status(self):
        from frappe.utils import getdate
        if self.docstatus == 0:
            self.contract_status = "Draft"
        elif self.end_date and getdate(self.end_date) < getdate():
            self.contract_status = "Expired"
