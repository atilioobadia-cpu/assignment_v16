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

		if (frm.doc.status !== "Completed" && frm.doc.status !== "Cancelled") {
			frm.add_custom_button(__("Log Employee Contribution"), () => {
				let d = frappe.prompt({
					label: __("Employee"),
					fieldname: "employee",
					fieldtype: "Link",
					options: "Employee",
					reqd: 1,
				}, () => {
					frm.add_custom_button(__("Log Employee Contribution"), () => {
						// already handled below
					});
				});

				// Use a dialog instead
				let dialog = new frappe.ui.Dialog({
					title: __("Log Employee Contribution"),
					fields: [
						{
							label: __("Employee"),
							fieldname: "employee",
							fieldtype: "Link",
							options: "Employee",
							reqd: 1,
						},
						{
							label: __("Hours Spent"),
							fieldname: "hours_spent",
							fieldtype: "Float",
							default: 0,
						},
						{
							label: __("Completion Status"),
							fieldname: "completion_status",
							fieldtype: "Select",
							options: "Completed\nPartial",
							default: "Completed",
						},
						{
							label: __("Notes"),
							fieldname: "notes",
							fieldtype": "Small Text",
						},
					],
					primary_action: (values) => {
						let row = frappe.model.add_child(frm.doc, {
							doctype: "Task Employee Log",
							parentfield: "custom_task_employee_log",
							employee: values.employee,
							hours_spent: values.hours_spent,
							completion_status: values.completion_status,
							notes: values.notes,
						});
						frm.refresh_field("custom_task_employee_log");
						dialog.hide();
						frappe.show_alert({
							message: __("Employee contribution logged"),
							indicator: "green",
						});
					},
					primary_action_label: __("Add"),
				});
				dialog.show();
			}, __("Actions"));
		}

		// Show summary of employee contributions
		if (frm.doc.custom_task_employee_log && frm.doc.custom_task_employee_log.length > 0) {
			let total_hours = frm.doc.custom_task_employee_log.reduce(
				(sum, r) => sum + (r.hours_spent || 0), 0
			);
			let employees = frm.doc.custom_task_employee_log
				.map(r => r.employee)
				.filter(Boolean)
				.join(", ");
			frm.dashboard.add_comment(
				__("Employee Log: {0} employees, {1} total hours", [employees, total_hours]),
				"blue", true
			);
		}
	},
});
