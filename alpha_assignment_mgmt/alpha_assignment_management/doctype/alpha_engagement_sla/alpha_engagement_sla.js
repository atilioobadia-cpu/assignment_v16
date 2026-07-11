// Copyright (c) 2026, Alpha Associates (T) Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Alpha Engagement SLA", {
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
			fieldname: [
				"customer",
				"custom_assignment_origination",
				"custom_engagement_manager",
				"custom_branch_manager",
				"custom_client_owner",
				"custom_service_line",
				"custom_risk_rating",
				"expected_start_date",
				"expected_end_date",
			],
			},
			callback(r) {
				if (r.message) {
					const d = r.message;
					if (d.customer) frm.set_value("customer", d.customer);
					if (d.custom_assignment_origination) frm.set_value("assignment_origination", d.custom_assignment_origination);
					if (d.custom_engagement_manager) frm.set_value("engagement_manager", d.custom_engagement_manager);
					if (d.custom_branch_manager) frm.set_value("branch_manager", d.custom_branch_manager);
					if (d.expected_end_date && !frm.doc.client_due_date) {
						frm.set_value("client_due_date", d.expected_end_date);
					}
				}
			},
		});
	},


});
