// Copyright (c) 2026, Alpha Associates (T) Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Performance Feedback", {
	refresh(frm) {
		if (frm.doc.project) {
			frm.add_custom_button(__("Open Project"), () => {
				frappe.set_route("Form", "Project", frm.doc.project);
			}, __("Navigate"));
		}
		if (frm.doc.employee) {
			frm.add_custom_button(__("Open Employee"), () => {
				frappe.set_route("Form", "Employee", frm.doc.employee);
			}, __("Navigate"));
		}
		if (frm.doc.status === "Submitted" && !frm.doc.acknowledged_by) {
			frm.add_custom_button(__("Acknowledge"), () => {
				frm.set_value("acknowledged_by", frappe.session.user);
				frm.set_value("acknowledged_date", frappe.datetime.get_today());
				frm.set_value("status", "Acknowledged");
				frm.save();
			}, __("Actions"));
		}
	},

	employee(frm) {
		if (!frm.doc.employee) {
			return;
		}
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Employee",
				filters: { name: frm.doc.employee },
				fieldname: ["user_id", "employee_name", "designation", "branch"],
			},
			callback(r) {
				if (r.message && r.message.user_id) {
					frm.set_value("feedback_from", r.message.employee_name);
				}
			},
		});
	},

	project(frm) {
		if (!frm.doc.project || frm.doc.assignment_origination) {
			return;
		}
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Project",
				filters: { name: frm.doc.project },
				fieldname: ["custom_assignment_origination"],
			},
			callback(r) {
				if (r.message && r.message.custom_assignment_origination) {
					frm.set_value("assignment_origination", r.message.custom_assignment_origination);
				}
			},
		});
	},
});
