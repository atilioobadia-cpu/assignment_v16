// Copyright (c) 2026, Alpha Associates (T) Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Alpha Project Template", {
	refresh(frm) {
		if (frm.doc.project_type) {
			frm.add_custom_button(__("Create Project from Template"), () => {
				const project = frappe.model.get_new_doc("Project");
				project.project_type = frm.doc.project_type;
				frappe.set_route("Form", "Project", project);
			}, __("Actions"));
		}
	},
});
