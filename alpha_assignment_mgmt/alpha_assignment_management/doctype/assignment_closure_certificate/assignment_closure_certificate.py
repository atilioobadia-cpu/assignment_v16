import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate


class AssignmentClosureCertificate(Document):
	def validate(self):
		if not self.closure_date:
			self.closure_date = today()

		if self.status == "Approved":
			validate_checklist_before_approval(self)

	def on_update(self):
		if self.status == "Approved" and self.project:
			_link_certificate_to_project(self)

	def on_submit(self):
		if self.status == "Approved" and self.project:
			_link_certificate_to_project(self)


def _link_certificate_to_project(doc):
	frappe.db.set_value("Project", doc.project, "custom_closure_certificate", doc.name)

	project = frappe.get_doc("Project", doc.project)
	if project.status != "Completed":
		project.status = "Completed"
		project.flags.ignore_permissions = True
		project.save()

	if doc.assignment_origination:
		frappe.db.set_value(
			"Alpha Assignment Origination",
			doc.assignment_origination,
			"closure_status",
			"Completed",
		)

	frappe.msgprint(
		f"Project {doc.project} has been marked as Completed.",
		alert=True,
	)


def validate_checklist_before_approval(doc):
	"""Enforce all checklist items before approval."""
	if doc.project:
		incomplete_tasks = frappe.db.count(
			"Task",
			filters={
				"project": doc.project,
				"status": ["not in", ["Completed", "Cancelled"]],
			},
		)
		if incomplete_tasks > 0:
			frappe.throw(
				f"Cannot approve: {incomplete_tasks} task(s) are not yet completed. "
				"All tasks must be completed or cancelled before approving the Closure Certificate."
			)

		unsubmitted_ts = frappe.db.count(
			"Timesheet",
			filters={
				"employee": doc.prepared_by,
				"docstatus": 0,
			},
		)
		if unsubmitted_ts > 0:
			frappe.throw(
				f"Cannot approve: {unsubmitted_ts} timesheet(s) are in Draft status. "
				"All timesheets must be submitted before approving the Closure Certificate."
			)
