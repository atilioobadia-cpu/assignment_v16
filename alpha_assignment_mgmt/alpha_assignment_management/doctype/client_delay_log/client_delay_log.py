from frappe.model.document import Document
from frappe.utils import today, date_diff

class ClientDelayLog(Document):
    def validate(self):
        if self.date_requested:
            self.ageing_days = date_diff(today(), self.date_requested)
        if not self.date_requested:
            self.date_requested = today()
