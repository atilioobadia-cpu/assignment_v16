from frappe.model.document import Document
from frappe.utils import today

class ReviewGateRegister(Document):
    def validate(self):
        if self.review_comments and not self.review_date:
            self.review_date = today()
