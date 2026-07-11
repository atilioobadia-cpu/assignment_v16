// Copyright (c) 2026, Alpha Associates (T) Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Review Gate Register", {
	refresh(frm) {
		if (frm.doc.task) {
			frm.add_custom_button(__("Open Task"), () => {
				frappe.set_route("Form", "Task", frm.doc.task);
			}, __("Navigate"));
		}
		if (frm.doc.project) {
			frm.add_custom_button(__("Open Project"), () => {
				frappe.set_route("Form", "Project", frm.doc.project);
			}, __("Navigate"));
		}

		if (frm.doc.docstatus === 0 && frm.doc.approval_status === "Pending") {
			frm.add_custom_button(__("Approve"), () => {
				frm.set_value("approval_status", "Approved");
				frm.set_value("review_date", frappe.datetime.get_today());
				frm.save().then(() => frappe.call({
					method: "frappe.client.submit",
					args: { doc: frm.doc },
					callback() { frm.reload_doc(); },
				}));
			}, __("Review Actions"));

			frm.add_custom_button(__("Return"), () => {
				frappe.prompt({
					label: __("Return Reason"),
					fieldname: "reason",
					fieldtype: "Small Text",
					reqd: 1,
				}, (values) => {
					frm.set_value("approval_status", "Returned");
					frm.set_value("correction_status", "Returned");
					frm.set_value("correction_notes", values.reason);
					frm.set_value("review_date", frappe.datetime.get_today());
					frm.save();
				}, __("Return for Correction"));
			}, __("Review Actions"));
		}
	},

	task(frm) {
		if (!frm.doc.task) {
			return;
		}
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Task",
				filters: { name: frm.doc.task },
				fieldname: ["project", "subject", "owner", "_assign"],
			},
			callback(r) {
				if (r.message) {
					const d = r.message;
					if (d.project) frm.set_value("project", d.project);
					if (d.owner) frm.set_value("preparer", d.owner);
				}
			},
		});
	},

	project(frm) {
		if (!frm.doc.project || frm.doc.task) {
			return;
		}
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Project",
				filters: { name: frm.doc.project },
				fieldname: ["customer", "custom_engagement_manager"],
			},
			callback(r) {
				if (r.message) {
					if (r.message.custom_engagement_manager) {
						frm.set_value("reviewer", r.message.custom_engagement_manager);
					}
				}
			},
		});
	},

	approval_status(frm) {
		if (frm.doc.approval_status === "Approved") {
			frm.set_value("review_date", frappe.datetime.get_today());
		}
	},
});
