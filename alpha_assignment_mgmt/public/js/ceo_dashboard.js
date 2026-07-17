// CEO Dashboard - Top 5 / Bottom 5 Employee Performance
// Loaded globally via app_include_js, renders only on CEO workspace page.

frappe.ready(function () {
	if (frappe.get_route_str() !== "workspace/CEO") return;

	const TARGET_ID = "ceo-top-bottom-lists";
	if (document.getElementById(TARGET_ID)) return;

	frappe.after_ajax(function () {
		render_employee_lists();
	});
	if (frappe.model && frappe.model.docinfo) {
		render_employee_lists();
	}
});

function render_employee_lists() {
	if (document.getElementById(TARGET_ID)) return;

	const container = document.querySelector(".layout-main-section");
	if (!container) return;

	const wrapper = document.createElement("div");
	wrapper.id = TARGET_ID;
	wrapper.className = "ceo-top-bottom-container";
	wrapper.innerHTML = `
		<div style="margin-bottom: 20px;">
			<h5 style="margin-bottom: 15px;"><b>Employee Task Performance</b></h5>
			<div style="display: flex; gap: 20px; flex-wrap: wrap;">
				<div style="flex: 1; min-width: 300px; border-left: 4px solid #28a745; padding: 15px; background: #f8f9fa; border-radius: 4px;">
					<h6 style="color: #28a745; font-weight: bold; margin-bottom: 10px;">Top 5 - Most Completed Tasks</h6>
					<div id="top-5-list"><p class="text-muted">Loading...</p></div>
				</div>
				<div style="flex: 1; min-width: 300px; border-left: 4px solid #dc3545; padding: 15px; background: #f8f9fa; border-radius: 4px;">
					<h6 style="color: #dc3545; font-weight: bold; margin-bottom: 10px;">Bottom 5 - Needs Attention</h6>
					<p style="font-size:11px;color:#999;margin-bottom:8px;">Employees with fewer completed tasks</p>
					<div id="bottom-5-list"><p class="text-muted">Loading...</p></div>
				</div>
			</div>
		</div>`;

	// Insert after the number cards row, before charts
	const firstChart = container.querySelector('[data-widget-type="chart"]');
	if (firstChart) {
		firstChart.parentNode.insertBefore(wrapper, firstChart);
	} else {
		container.appendChild(wrapper);
	}

	frappe.call({
		method: "alpha_assignment_mgmt.alpha_assignment_management.api.ceo_dashboard.get_ceo_top_bottom",
		callback: function (r) {
			if (!r.message) return;
			var data = r.message;
			renderList("top-5-list", data.top5, true);
			renderList("bottom-5-list", data.bottom5, false);
		},
		error: function () {
			document.getElementById("top-5-list").innerHTML = '<p class="text-muted">Error loading data</p>';
			document.getElementById("bottom-5-list").innerHTML = '<p class="text-muted">Error loading data</p>';
		},
	});
}

function renderList(containerId, items, isTop) {
	var container = document.getElementById(containerId);
	if (!container) return;
	if (!items || !items.length) {
		container.innerHTML = '<p class="text-muted">No data</p>';
		return;
	}
	var html = '<table class="table table-sm table-borderless mb-0">';
	html += '<tr style="font-weight:bold;color:#666;font-size:12px;"><td style="width:30px">#</td><td>Employee</td><td style="width:80px;text-align:center;">Completed</td><td style="width:80px;text-align:center;">Pending</td></tr>';
	items.forEach(function (item, i) {
		var rank = i + 1;
		var medal = "";
		if (isTop && rank === 1) medal = " \ud83e\udd47";
		else if (isTop && rank === 2) medal = " \ud83e\udd48";
		else if (isTop && rank === 3) medal = " \ud83e\udd49";
		var completedBadge =
			item.completed > 0
				? '<span class="badge" style="background:#28a745;color:#fff;font-size:12px;">' + item.completed + "</span>"
				: '<span class="badge" style="background:#6c757d;color:#fff;font-size:12px;">0</span>';
		var pendingBadge =
			item.pending > 0
				? '<span class="badge" style="background:#dc3545;color:#fff;font-size:12px;">' + item.pending + "</span>"
				: '<span class="badge" style="background:#28a745;color:#fff;font-size:12px;">0</span>';
		html += "<tr><td><b>" + rank + "</b></td><td>" + item.name + medal + '</td><td style="text-align:center;">' + completedBadge + '</td><td style="text-align:center;">' + pendingBadge + "</td></tr>";
	});
	html += "</table>";
	container.innerHTML = html;
}
