import frappe
from frappe.model.document import Document


class AlphaProjectTemplate(Document):
	def validate(self):
		self.total_tasks = len(self.tasks) if self.tasks else 0
		self.total_expected_hours = sum(
			t.expected_hours or 0 for t in self.tasks
		) if self.tasks else 0
