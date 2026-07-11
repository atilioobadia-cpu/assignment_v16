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

		if (frm.doc.custom_client_delay_log) {
			frm.add_custom_button(__("Open Delay Log"), () => {
				frappe.set_route("Form", "Client Delay Log", frm.doc.custom_client_delay_log);
			}, __("Navigate"));
		}
	},
});
