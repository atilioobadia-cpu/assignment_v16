// Copyright (c) 2025, Alpha Associates (T) Limited and contributors
// For license information, please see license.txt

frappe.query_reports["SLA Compliance Overview"] = {
	"filters": [
		{
			"fieldname": "sla_status",
			"fieldtype": "Select",
			"label": __("SLA Status"),
			"mandatory": 0,
			"options": "\nActive\nBreached\nCompleted\nCancelled"
		},
		{
			"fieldname": "sla_level",
			"fieldtype": "Select",
			"label": __("SLA Level"),
			"mandatory": 0,
			"options": "\nSLA A - Urgent Statutory\nSLA B - Audit Readiness\nSLA C - Monthly Bookkeeping\nSLA D - Reconstruction\nSLA E - Advisory/Research/Training"
		}
	]
};
