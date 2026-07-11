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
							freeze_message: __("Creating Project..."),
							callback(r) {
								if (r.message) {
									frappe.msgprint(__("Project {0} created successfully.", [r.message]));
									frm.reload_doc();
								}
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
		}
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
				fields: ["email_id", "mobile_no", "tax_id", "customer_primary_address"],
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
