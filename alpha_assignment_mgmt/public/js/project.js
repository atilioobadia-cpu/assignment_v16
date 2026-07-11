// Copyright (c) 2026, Alpha Associates (T) Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project", {
	refresh(frm) {
		if (frm.doc.custom_assignment_origination) {
			frm.add_custom_button(__("Open Origination"), () => {
				frappe.set_route("Form", "Alpha Assignment Origination", frm.doc.custom_assignment_origination);
			}, __("Navigate"));
		}
		if (frm.doc.custom_engagement_sla) {
			frm.add_custom_button(__("Open SLA"), () => {
				frappe.set_route("Form", "Alpha Engagement SLA", frm.doc.custom_engagement_sla);
			}, __("Navigate"));
		}
		if (frm.doc.custom_closure_certificate) {
			frm.add_custom_button(__("Open Closure Certificate"), () => {
				frappe.set_route("Form", "Assignment Closure Certificate", frm.doc.custom_closure_certificate);
			}, __("Navigate"));
		}

		if (frm.doc.status === "Active") {
			frm.add_custom_button(__("New Task"), () => {
				const task = frappe.model.get_new_doc("Task");
				task.project = frm.doc.name;
				frappe.set_route("Form", "Task", task);
			}, __("Actions"));
		}
	},

	custom_assignment_origination(frm) {
		if (!frm.doc.custom_assignment_origination) {
			return;
		}
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Alpha Assignment Origination",
				filters: { name: frm.doc.custom_assignment_origination },
			fieldname: [
				"customer",
				"service_line",
				"risk_rating",
				"engagement_manager",
				"lead_branch_manager",
				"client_owner",
				"branch",
				"proposed_fee",
				"billing_method",
				"statutory_deadline",
				"regulatory_deadline",
				"urgency_level",
			],
			},
			callback(r) {
				if (r.message) {
					const d = r.message;
					if (d.customer) frm.set_value("customer", d.customer);
					if (d.service_line) {
						frm.set_value("custom_service_line", d.service_line);
						frm.set_value("project_type", d.service_line);
					}
					if (d.risk_rating) frm.set_value("custom_risk_rating", d.risk_rating);
					if (d.engagement_manager) frm.set_value("custom_engagement_manager", d.engagement_manager);
					if (d.lead_branch_manager) frm.set_value("custom_branch_manager", d.lead_branch_manager);
					if (d.client_owner) frm.set_value("custom_client_owner", d.client_owner);
					if (d.branch) frm.set_value("branch", d.branch);
					if (d.proposed_fee) frm.set_value("estimated_costing", d.proposed_fee);
					if (d.statutory_deadline && !frm.doc.expected_end_date) {
						frm.set_value("expected_end_date", d.statutory_deadline);
					} else if (d.regulatory_deadline && !frm.doc.expected_end_date) {
						frm.set_value("expected_end_date", d.regulatory_deadline);
					}
					frappe.show_alert({ message: __("Fields populated from Assignment Origination."), indicator: "green" });
				}
			},
		});
	},
});
