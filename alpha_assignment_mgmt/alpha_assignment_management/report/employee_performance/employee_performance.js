// Copyright (c) 2026, Alpha Associates (T) Limited and contributors

frappe.query_reports["Employee Performance"] = {
	"filters": [
		{
			"fieldname": "days",
			"fieldtype": "Int",
			"label": __("Days (Lookback)"),
			"default": 30,
			"reqd": 1,
		},
	],
	"onload": function (report) {
		frappe.call({
			method: "alpha_assignment_mgmt.alpha_assignment_management.report.employee_performance.employee_performance.get_top_bottom",
			args: { days: 30 },
			callback: function (r) {
				if (r.message) {
					render_performance_cards(report, r.message);
				}
			},
		});
	},
};

function render_performance_cards(report, data) {
	let wrapper = report.$wrapper.find(".report-wrapper").first();
	let card_section = $(
		'<div class="row" style="margin-bottom: 15px;"></div>'
	);

	// Top contributors
	let top_html = '<div class="col-md-6"><div class="card" style="border-left: 4px solid #28a745;">';
	top_html += '<div class="card-body"><h6 class="card-title" style="color: #28a745;">Top Contributors</h6>';
	if (data.top_contributors && data.top_contributors.length) {
		top_html += '<table class="table table-sm table-borderless mb-0">';
		data.top_contributors.forEach((emp, i) => {
			top_html += `<tr><td><strong>#${i + 1}</strong></td><td>${emp.employee_name}</td><td class="text-right"><span class="badge badge-success">${emp.hours_logged}h</span></td><td class="text-right"><span class="badge badge-info">${emp.tasks_completed} tasks</span></td></tr>`;
		});
		top_html += "</table>";
	} else {
		top_html += '<p class="text-muted">No data yet</p>';
	}
	top_html += "</div></div></div>";

	// Bottom performers
	let bottom_html = '<div class="col-md-6"><div class="card" style="border-left: 4px solid #dc3545;">';
	bottom_html += '<div class="card-body"><h6 class="card-title" style="color: #dc3545;">Needs Attention</h6>';
	if (data.bottom_performers && data.bottom_performers.length) {
		bottom_html += '<table class="table table-sm table-borderless mb-0">';
		data.bottom_performers.forEach((emp, i) => {
			bottom_html += `<tr><td><strong>#${i + 1}</strong></td><td>${emp.employee_name}</td><td class="text-right"><span class="badge badge-warning">${emp.hours_logged}h</span></td><td class="text-right"><span class="badge badge-secondary">${emp.tasks_completed} tasks</span></td></tr>`;
		});
		bottom_html += "</table>";
	} else {
		bottom_html += '<p class="text-muted">No data yet</p>';
	}
	bottom_html += "</div></div></div>";

	card_section.append(top_html).append(bottom_html);
	wrapper.prepend(card_section);
}
