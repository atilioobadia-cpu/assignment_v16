// Copyright (c) 2026, Alpha Associates (T) Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Document Request Register", {
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

		if (frm.doc.status === "Requested" || frm.doc.status === "Overdue") {
			frm.add_custom_button(__("Mark Received"), () => {
				frm.set_value("status", "Received");
				frm.set_value("received_date", frappe.datetime.get_today());
				frm.save();
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
				"custom_assignment_origination",
				"custom_client_owner",
			],
			},
			callback(r) {
				if (r.message) {
					const d = r.message;
					if (d.custom_assignment_origination) frm.set_value("assignment_origination", d.custom_assignment_origination);
					if (d.custom_client_owner) frm.set_value("responsible_person", d.custom_client_owner);
				}
			},
		});
	},

	assignment_origination(frm) {
		if (!frm.doc.assignment_origination || frm.doc.project) {
			return;
		}
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Alpha Assignment Origination",
				filters: { name: frm.doc.assignment_origination },
				fieldname: ["customer"],
			},
			callback(r) {
				if (r.message) {
					frappe.show_alert({
						message: __("Origination linked: {0}", [frm.doc.assignment_origination]),
						indicator: "green",
					});
				}
			},
		});
	},
});
