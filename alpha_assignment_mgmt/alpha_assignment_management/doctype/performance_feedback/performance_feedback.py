import frappe
from frappe.model.document import Document
from frappe.utils import today


class PerformanceFeedback(Document):
	def validate(self):
		if self.status == "Submitted" and not self.feedback_date:
			self.feedback_date = today()
