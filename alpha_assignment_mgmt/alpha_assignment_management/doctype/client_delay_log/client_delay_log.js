// Copyright (c) 2026, Alpha Associates (T) Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Client Delay Log", {
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

		if (frm.doc.status === "Open") {
			frm.add_custom_button(__("Mark Resolved"), () => {
				frm.set_value("status", "Resolved");
				frm.set_value("resolved_date", frappe.datetime.get_today());
				frm.save();
			}, __("Actions"));

			frm.add_custom_button(__("Escalate"), () => {
				const levels = ["Level 1 - Staff", "Level 2 - Engagement Manager", "Level 3 - Branch Manager", "Level 4 - Management"];
				const current = levels.indexOf(frm.doc.escalation_level || levels[0]);
				if (current < levels.length - 1) {
					frm.set_value("escalation_level", levels[current + 1]);
					frm.save();
				}
			}, __("Actions"));
		}

		if (frm.doc.status === "Open" || frm.doc.status === "Escalated") {
			frm.add_custom_button(__("BM Override - Approve Delay"), () => {
				frappe.confirm(
					__("As Branch Manager, override this delay and approve it? This will close the delay and unblock the task."),
					() => {
						frm.set_value("status", "Closed");
						frm.set_value("resolved_date", frappe.datetime.get_today());
						frm.set_value("notes", (frm.doc.notes || "") + "\nBranch Manager override approval.");
						frm.save();

						if (frm.doc.task) {
							frappe.call({
								method: "frappe.client.get_value",
								args: {
									doctype: "Task",
									filters: { name: frm.doc.task },
									fields: ["status"],
								},
								callback(r) {
									if (r.message && r.message.status === "Waiting for Client") {
										frappe.call({
											method: "frappe.client.set_value",
											args: {
												doctype: "Task",
												name: frm.doc.task,
												fieldname: "status",
												value: "In Progress",
											},
										});
									}
								},
							});
						}
					}
				);
			}, __("Branch Manager"));
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
				fields: ["project", "subject", "exp_end_date"],
			},
			callback(r) {
				if (r.message) {
					if (r.message.project) frm.set_value("project", r.message.project);

					if (r.message.project) {
						frappe.call({
							method: "frappe.client.get_value",
							args: {
								doctype: "Project",
								filters: { name: r.message.project },
								fields: ["customer"],
							},
							callback(r2) {
								if (r2.message && r2.message.customer) {
									frm.set_value("customer", r2.message.customer);
								}
							},
						});
					}
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
				fields: ["customer"],
			},
			callback(r) {
				if (r.message && r.message.customer) {
					frm.set_value("customer", r.message.customer);
				}
			},
		});
	},

	expected_response_date(frm) {
		if (frm.doc.date_requested && frm.doc.expected_response_date) {
			const days = frappe.datetime.get_diff(frm.doc.expected_response_date, frm.doc.date_requested);
			if (days > 7) {
				frm.set_value("escalation_level", "Level 2");
			}
			if (days > 14) {
				frm.set_value("escalation_level", "Level 3");
			}
			if (days > 30) {
				frm.set_value("escalation_level", "Level 4");
			}
		}
	},
});
