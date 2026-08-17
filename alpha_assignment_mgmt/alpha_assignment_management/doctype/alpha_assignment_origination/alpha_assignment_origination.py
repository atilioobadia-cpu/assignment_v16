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
        if self.deposit_required and self.proposed_fee:
            if self.deposit_required > self.proposed_fee:
                frappe.throw(
                    "Deposit Required ({0}) cannot be greater than Proposed Fee ({1})".format(
                        frappe.format(self.deposit_required, 'Currency'),
                        frappe.format(self.proposed_fee, 'Currency')
                    )
                )
