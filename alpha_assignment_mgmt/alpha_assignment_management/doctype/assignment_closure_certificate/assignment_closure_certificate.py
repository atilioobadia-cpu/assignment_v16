import frappe
from frappe.model.document import Document
from frappe.utils import today


class AssignmentClosureCertificate(Document):
	def validate(self):
		if not self.closure_date:
			self.closure_date = today()

	def on_update(self):
		"""When certificate is approved, link it back to Project and mark completed."""
		if self.status == "Approved" and self.project:
			frappe.db.set_value(
				"Project",
				self.project,
				"custom_closure_certificate",
				self.name,
			)

			# Auto-set project status to Completed when certificate is approved
			project = frappe.get_doc("Project", self.project)
			if project.status != "Completed":
				project.status = "Completed"
				project.flags.ignore_permissions = True
				project.save()

			# Also update origination closure status
			if self.assignment_origination:
				frappe.db.set_value(
					"Alpha Assignment Origination",
					self.assignment_origination,
					"closure_status",
					"Completed",
				)

			frappe.msgprint(
				f"Project {self.project} has been marked as Completed.",
				alert=True,
			)

	def on_submit(self):
		"""When submitted and approved, link to Project."""
		if self.status == "Approved" and self.project:
			frappe.db.set_value(
				"Project",
				self.project,
				"custom_closure_certificate",
				self.name,
			)

			# Auto-set project status to Completed
			project = frappe.get_doc("Project", self.project)
			if project.status != "Completed":
				project.status = "Completed"
				project.flags.ignore_permissions = True
				project.save()

			if self.assignment_origination:
				frappe.db.set_value(
					"Alpha Assignment Origination",
					self.assignment_origination,
					"closure_status",
					"Completed",
				)
