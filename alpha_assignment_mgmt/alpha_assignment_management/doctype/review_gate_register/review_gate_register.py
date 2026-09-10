from frappe.model.document import Document
from frappe.utils import today
import frappe

class ReviewGateRegister(Document):
    def validate(self):
        if self.preparer and self.reviewer and self.preparer == self.reviewer:
            frappe.throw("Preparer and Reviewer must be different users.")

        if self.review_comments and not self.review_date:
            self.review_date = today()

    def before_submit(self):
        if self.approval_status != "Approved":
            self.approval_status = "Approved"
        if not self.approved_date:
            self.approved_date = today()
