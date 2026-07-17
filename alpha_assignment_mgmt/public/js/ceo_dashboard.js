// CEO Dashboard - Top 5 / Bottom 5 Employee Performance
// Loaded globally via app_include_js, renders only on CEO workspace page.

(function () {
	var TARGET_ID = "ceo-top-bottom-lists";
	var POLL_INTERVAL = 500;
	var MAX_POLL = 60;

	function is_ceo_workspace() {
		var route = frappe.get_route_str();
		return route.indexOf("CEO") !== -1;
	}

	function try_render(attempt) {
		if (document.getElementById(TARGET_ID)) return;
		if (attempt > MAX_POLL) return;

		// Editor.js container is #editorjs inside .layout-main-section
		var editorjs = document.querySelector("#editorjs");
		if (!editorjs) {
			setTimeout(function () { try_render(attempt + 1); }, POLL_INTERVAL);
			return;
		}

		render_employee_lists(editorjs);
	}

	frappe.ready(function () {
		if (!is_ceo_workspace()) return;

		try_render(0);

		// Also watch for route changes (SPA navigation)
		var last_route = frappe.get_route_str();
		setInterval(function () {
			var current = frappe.get_route_str();
			if (current !== last_route) {
				last_route = current;
				if (is_ceo_workspace() && !document.getElementById(TARGET_ID)) {
					try_render(0);
				}
			}
		}, 1000);
	});

	function render_employee_lists(editorjs) {
		if (document.getElementById(TARGET_ID)) return;

		var wrapper = document.createElement("div");
		wrapper.id = TARGET_ID;
		wrapper.className = "ceo-top-bottom-container";
		wrapper.style.marginBottom = "24px";
		wrapper.innerHTML =
			'<div class="section-head" style="margin-bottom: 15px;">' +
				'<span class="h5"><b>Employee Task Performance</b></span>' +
			'</div>' +
			'<div style="display: flex; gap: 20px; flex-wrap: wrap;">' +
				'<div style="flex: 1; min-width: 300px; border-left: 4px solid #28a745; padding: 15px; background: var(--card-bg); border-radius: var(--border-radius-md); box-shadow: var(--shadow-sm);">' +
					'<h6 style="color: #28a745; font-weight: bold; margin-bottom: 10px;">Top 5 - Most Completed Tasks</h6>' +
					'<div id="ceo-top5-list"><p class="text-muted">Loading...</p></div>' +
				'</div>' +
				'<div style="flex: 1; min-width: 300px; border-left: 4px solid #dc3545; padding: 15px; background: var(--card-bg); border-radius: var(--border-radius-md); box-shadow: var(--shadow-sm);">' +
					'<h6 style="color: #dc3545; font-weight: bold; margin-bottom: 10px;">Bottom 5 - Needs Attention</h6>' +
					'<p style="font-size:11px;color:#999;margin-bottom:8px;">Employees with fewer completed tasks</p>' +
					'<div id="ceo-bottom5-list"><p class="text-muted">Loading...</p></div>' +
				'</div>' +
			'</div>';

		// Insert before the Editor.js container so it appears at the top
		editorjs.parentNode.insertBefore(wrapper, editorjs);

		frappe.call({
			method: "alpha_assignment_mgmt.alpha_assignment_management.api.ceo_dashboard.get_ceo_top_bottom",
			callback: function (r) {
				if (!r.message) return;
				var data = r.message;
				renderList("ceo-top5-list", data.top5, true);
				renderList("ceo-bottom5-list", data.bottom5, false);
			},
			error: function () {
				var el1 = document.getElementById("ceo-top5-list");
				var el2 = document.getElementById("ceo-bottom5-list");
				if (el1) el1.innerHTML = '<p class="text-muted">Error loading data</p>';
				if (el2) el2.innerHTML = '<p class="text-muted">Error loading data</p>';
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
		html += '<tr style="font-weight:bold;color:var(--text-muted);font-size:12px;">' +
			'<td style="width:30px">#</td><td>Employee</td>' +
			'<td style="width:80px;text-align:center;">Completed</td>' +
			'<td style="width:80px;text-align:center;">Pending</td></tr>';
		items.forEach(function (item, i) {
			var rank = i + 1;
			var medal = "";
			if (isTop && rank === 1) medal = " \ud83e\udd47";
			else if (isTop && rank === 2) medal = " \ud83e\udd48";
			else if (isTop && rank === 3) medal = " \ud83e\udd49";
			var completedBadge =
				item.completed > 0
					? '<span class="indicator-pill" style="background:#28a745;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px;">' + item.completed + "</span>"
					: '<span class="indicator-pill" style="background:#6c757d;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px;">0</span>';
			var pendingBadge =
				item.pending > 0
					? '<span class="indicator-pill" style="background:#dc3545;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px;">' + item.pending + "</span>"
					: '<span class="indicator-pill" style="background:#28a745;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px;">0</span>';
			html += "<tr><td><b>" + rank + "</b></td><td>" + item.name + medal +
				'</td><td style="text-align:center;">' + completedBadge +
				'</td><td style="text-align:center;">' + pendingBadge + "</td></tr>";
		});
		html += "</table>";
		container.innerHTML = html;
	}
})();
