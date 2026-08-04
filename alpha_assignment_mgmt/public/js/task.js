// Copyright (c) 2026, Alpha Associates (T) Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Task", {
	refresh(frm) {
		if (frm.doc.project) {
			frm.add_custom_button(__("Open Project"), () => {
				frappe.set_route("Form", "Project", frm.doc.project);
			}, __("Navigate"));
		}

		if (frm.doc.custom_review_gate) {
			frm.add_custom_button(__("Open Review Gate"), () => {
				frappe.set_route("Form", "Review Gate Register", frm.doc.custom_review_gate);
			}, __("Navigate"));
		}

		if (frm.doc.project) {
			frm.add_custom_button(__("Open Delay Log"), () => {
				frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "Client Delay Log",
						filters: { task: frm.doc.name },
						fields: ["name"],
						limit_page_length: 1,
					},
					callback: (r) => {
						if (r.message && r.message.length) {
							frappe.set_route("Form", "Client Delay Log", r.message[0].name);
						} else {
							frappe.msgprint(__("No Client Delay Log found for this task"));
						}
					},
				});
			}, __("Navigate"));
		}

		// Send Email with #TASK-XXXXX tag for auto-linking
		if (frm.doc.docstatus === 1 || frm.doc.docstatus === 0) {
			frm.add_custom_button(__("Send Email"), () => {
				let subject = __("Re: {0} (#{1})", [frm.doc.subject || frm.doc.name, frm.doc.name]);
				frm.email_doc(subject);
			}, __("Communication"));
		}
	},
});
