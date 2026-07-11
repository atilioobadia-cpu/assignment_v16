// Copyright (c) 2026, Alpha Associates (T) Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Assignment Closure Certificate", {
	refresh(frm) {
		if (frm.doc.project) {
			frm.add_custom_button(__("Open Project"), () => {
				frappe.set_route("Form", "Project", frm.doc.project);
			}, __("Navigate"));
		}
		if (frm.doc.assignment_origination) {
			frm.add_custom_button(__("Open Origination"), () => {
				frappe.set_route("Form", "Alpha Assignment Origination", frm.doc.assignment_origination);
			}, __("Navigate"));
		}

		if (frm.doc.status === "Draft") {
			frm.add_custom_button(__("Re-Check Tasks"), () => {
				frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "Task",
						filters: {
							project: frm.doc.project,
							status: ["not in", ["Completed", "Cancelled"]],
						},
						limit_page_length: 100,
						fields: ["name", "subject", "status"],
					},
					callback(r) {
						if (r.message && r.message.length) {
							frm.set_value("all_tasks_complete", 0);
							frappe.msgprint(
								__("There are {0} incomplete task(s): {1}", [
									r.message.length,
									r.message.map((t) => t.subject).join(", "),
								]),
								__("Incomplete Tasks")
							);
						} else {
							frm.set_value("all_tasks_complete", 1);
							frappe.msgprint(__("All tasks are complete!"), __("Check Complete"));
						}
					},
				});
			}, __("Actions"));
		}
	},

	project(frm) {
		if (!frm.doc.project) {
			return;
		}
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Project",
				filters: { name: frm.doc.project },
			fieldname: [
				"customer",
				"custom_assignment_origination",
				"custom_engagement_manager",
				"custom_branch_manager",
				"custom_client_owner",
			],
			},
			callback(r) {
				if (r.message) {
					const d = r.message;
					if (d.customer) frm.set_value("customer", d.customer);
					if (d.custom_assignment_origination) frm.set_value("assignment_origination", d.custom_assignment_origination);
					if (d.custom_engagement_manager) frm.set_value("prepared_by", d.custom_engagement_manager);

					frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "Task",
							filters: { project: frm.doc.project, status: ["not in", ["Completed", "Cancelled"]] },
							limit_page_length: 1,
						},
						callback(r2) {
							frm.set_value("all_tasks_complete", r2.message && r2.message.length ? 0 : 1);
						},
					});

					frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "Timesheet",
							filters: {
								employee: d.custom_engagement_manager,
								docstatus: 0,
							},
							limit_page_length: 1,
						},
						callback(r3) {
							frm.set_value("all_timesheets_submitted", r3.message && r3.message.length ? 0 : 1);
						},
					});
				}
			},
		});
	},

	approved_by(frm) {
		if (frm.doc.approved_by && !frm.doc.approval_date) {
			frm.set_value("approval_date", frappe.datetime.get_today());
		}
	},

	validate(frm) {
		if (frm.doc.status === "Approved") {
			const checks = [
				"all_tasks_complete",
				"all_timesheets_submitted",
				"evidence_archived",
				"client_deliverables_issued",
				"billing_complete",
				"client_sign_off_obtained",
			];
			const incomplete = checks.filter((f) => !frm.doc[f]);
			if (incomplete.length) {
				frappe.msgprint(
					__("Cannot approve: {0} checklist items are not completed.", [incomplete.length]),
					__("Checklist Incomplete")
				);
				frappe.validated = false;
			}
		}
	},
});
