// Copyright (c) 2026, Alpha Associates (T) Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Client Risk Register", {
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
				fields: [
					"customer",
					"custom_assignment_origination",
					"custom_risk_rating",
					"custom_engagement_manager",
				],
			},
			callback(r) {
				if (r.message) {
					const d = r.message;
					if (d.customer) frm.set_value("customer", d.customer);
					if (d.custom_assignment_origination) frm.set_value("assignment_origination", d.custom_assignment_origination);
					if (d.custom_engagement_manager) frm.set_value("owner", d.custom_engagement_manager);
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
				fields: ["customer", "risk_rating"],
			},
			callback(r) {
				if (r.message) {
					if (r.message.customer) frm.set_value("customer", r.message.customer);
					if (r.message.risk_rating) {
						frm.set_value("risk_rating", r.message.risk_rating);
					}
				}
			},
		});
	},

	validate(frm) {
		if (frm.doc.risk_rating === "Critical" && frm.doc.status === "Open") {
			frappe.msgprint(
				__("Warning: Critical risk is open. Please ensure mitigation is in progress."),
				__("Risk Alert")
			);
		}
	},
});
