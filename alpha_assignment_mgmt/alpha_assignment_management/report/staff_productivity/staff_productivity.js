// Copyright (c) 2026, Alpha Integrated Management System
// For license information, please see license.txt

frappe.query_reports["Staff Productivity"] = {
	"filters": [
		{
			"fieldname": "branch",
			"fieldtype": "Link",
			"label": __("Branch"),
			"mandatory": 0,
			"options": "Branch"
		},
		{
			"fieldname": "designation",
			"fieldtype": "Link",
			"label": __("Designation"),
			"mandatory": 0,
			"options": "Designation"
		}
	]
};
