// Copyright (c) 2026, Alpha Associates (T) Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Alpha Assignment Origination", {
	refresh(frm) {
		if (frm.doc.docstatus === 1 && frm.doc.workflow_state === "Approved" && !frm.doc.project_created) {
			frm.add_custom_button(__("Create Project"), () => {
				frappe.confirm(
					__("Create a Project from this Assignment Origination?"),
					() => {
						frappe.call({
							method: "alpha_assignment_mgmt.overrides.assignment_origination.create_project_from_origination",
							args: { origination_name: frm.doc.name },
							freeze: true,
							freeze_message: __("Creating Project and generating tasks..."),
							callback(r) {
								if (r.message) {
									frappe.msgprint(__("Project {0} created successfully.", [r.message]));
									frm.reload_doc();
								}
							},
							error() {
								frm.reload_doc();
							},
						});
					}
				);
			}, __("Actions"));
		}

		if (frm.doc.project_reference) {
			frm.add_custom_button(__("Open Project"), () => {
				frappe.set_route("Form", "Project", frm.doc.project_reference);
			}, __("Navigate"));
		}

		if (frm.doc.project_created) {
			frm.set_df_property("customer", "read_only", 1);
			frm.set_df_property("service_line", "read_only", 1);
		}

		if (frm.doc.docstatus === 1 && frm.doc.email) {
			frm.add_custom_button(__("Send Email"), () => {
				frm.email_doc(__("Re: {0} - {1}", [frm.doc.name, frm.doc.assignment_title || frm.doc.name]));
			}, __("Communication"));
		}
	},

	service_line(frm) {
		if (!frm.doc.service_line) {
			frm.set_value("custom_project_template", "");
			return;
		}

		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Alpha Project Template",
				filters: {
					project_type: frm.doc.service_line,
					is_active: 1,
				},
				fieldname: ["name", "template_name", "total_tasks"],
			},
			callback(r) {
				if (r.message) {
					frm.set_value("custom_project_template", r.message.name);
					frappe.show_alert({
						message: __("Template auto-selected: {0} ({1} tasks)", [r.message.template_name, r.message.total_tasks]),
						indicator: "green",
					});
				}
			},
		});
	},

	customer(frm) {
		if (!frm.doc.customer) {
			return;
		}
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Customer",
				filters: { name: frm.doc.customer },
				fieldname: ["email_id", "mobile_no", "tax_id", "customer_primary_address"],
			},
			callback(r) {
				if (r.message) {
					if (r.message.email_id) {
						frm.set_value("email", r.message.email_id);
					}
					if (r.message.mobile_no) {
						frm.set_value("contact_number", r.message.mobile_no);
					}
					if (r.message.tax_id) {
						frm.set_value("tin_reference", r.message.tax_id);
					}
				}
			},
		});

		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Contact",
				filters: [
					["Dynamic Link", "link_doctype", "=", "Customer"],
					["Dynamic Link", "link_name", "=", frm.doc.customer],
				],
				fields: ["first_name", "last_name", "phone", "email_id"],
				limit_page_length: 1,
			},
			callback(r) {
				if (r.message && r.message.length) {
					const contact = r.message[0];
					const name = [contact.first_name, contact.last_name].filter(Boolean).join(" ");
					if (name && !frm.doc.client_focal_person) {
						frm.set_value("client_focal_person", name);
					}
					if (contact.phone && !frm.doc.contact_number) {
						frm.set_value("contact_number", contact.phone);
					}
					if (contact.email_id && !frm.doc.email) {
						frm.set_value("email", contact.email_id);
					}
				}
			},
		});
	},
});
