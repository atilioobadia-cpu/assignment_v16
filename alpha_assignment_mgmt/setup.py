import frappe
import json
import os


def after_install():
    """Set up CEO Dashboard and all report components after app install."""
    create_number_cards()
    create_dashboard_charts()
    create_custom_html_block()
    setup_ceo_workspace()
    setup_aims_desk_workspace()
    create_ceo_api_method()
    frappe.db.commit()


def after_migrate():
    """Re-sync dashboard components after migration."""
    after_install()


def create_number_cards():
    cards = [
        {
            "name": "Tasks Completed",
            "label": "Tasks Completed",
            "filters": '[["Task","status","=","Completed"]]',
            "color": "#28a745",
        },
        {
            "name": "Tasks Pending",
            "label": "Tasks Pending",
            "filters": '[["Task","status","in",["Open","Working","Overdue"]]]',
            "color": "#ff6b6b",
        },
    ]
    for c in cards:
        if frappe.db.exists("Number Card", c["name"]):
            frappe.db.set_value("Number Card", c["name"], {
                "document_type": "Task",
                "function": "Count",
                "type": "Document Type",
                "is_standard": 0,
                "is_public": 1,
                "filters_json": c["filters"],
                "show_percentage_stats": 1,
                "stats_time_interval": "Daily",
                "color": c["color"],
                "module": "Alpha Assignment Management",
            })
        else:
            doc = frappe.new_doc("Number Card")
            doc.name = c["name"]
            doc.label = c["label"]
            doc.document_type = "Task"
            doc.function = "Count"
            doc.type = "Document Type"
            doc.is_public = 1
            doc.is_standard = 0
            doc.module = "Alpha Assignment Management"
            doc.filters_json = c["filters"]
            doc.show_percentage_stats = 1
            doc.stats_time_interval = "Daily"
            doc.color = c["color"]
            doc.insert(ignore_permissions=True)

    # Make Active Staff and Active Clients public if they exist
    for name in ["Active Staff", "Active Clients"]:
        if frappe.db.exists("Number Card", name):
            frappe.db.set_value("Number Card", name, {
                "is_public": 1,
                "module": "Alpha Assignment Management",
            })


def create_dashboard_charts():
    charts = [
        {
            "name": "Employee Performance Trend",
            "chart_type": "Count",
            "document_type": "Task",
            "based_on": "completed_on",
            "type": "Line",
            "filters": '[["Task","status","=","Completed"]]',
            "timeseries": 1,
            "time_interval": "Monthly",
            "custom_options": json.dumps({"colors": ["#5e64ff"]}),
        },
        {
            "name": "Tasks by Status",
            "chart_type": "Group By",
            "document_type": "Task",
            "group_by_based_on": "status",
            "type": "Pie",
            "filters": "[]",
            "custom_options": json.dumps({"colors": ["#5e64ff", "#28a745", "#ff6b6b", "#ffa726", "#42a5f5"]}),
        },
        {
            "name": "Tasks Completed Over Time",
            "chart_type": "Count",
            "document_type": "Task",
            "based_on": "completed_on",
            "type": "Bar",
            "filters": '[["Task","status","=","Completed"]]',
            "timeseries": 1,
            "time_interval": "Monthly",
            "custom_options": json.dumps({"colors": ["#28a745"]}),
        },
        {
            "name": "Open Tasks by Project",
            "chart_type": "Group By",
            "document_type": "Task",
            "group_by_based_on": "project",
            "type": "Bar",
            "filters": '[["Task","status","in",["Open","Working","Overdue"]]]',
            "custom_options": json.dumps({"colors": ["#ffa726", "#5e64ff", "#ff6b6b", "#28a745"]}),
        },
        {
            "name": "Task Priority Distribution",
            "chart_type": "Group By",
            "document_type": "Task",
            "group_by_based_on": "priority",
            "type": "Bar",
            "filters": "[]",
            "custom_options": json.dumps({"colors": ["#ff6b6b", "#ffa726", "#5e64ff", "#28a745"]}),
        },
    ]

    for ch in charts:
        if frappe.db.exists("Dashboard Chart", ch["name"]):
            vals = {
                "chart_type": ch["chart_type"],
                "document_type": ch["document_type"],
                "type": ch["type"],
                "filters_json": ch["filters"],
                "custom_options": ch.get("custom_options"),
                "is_standard": 0,
                "is_public": 1,
                "module": "Alpha Assignment Management",
                "timeseries": ch.get("timeseries", 0),
                "chart_name": ch["name"],
            }
            if ch.get("based_on"):
                vals["based_on"] = ch["based_on"]
            if ch.get("group_by_based_on"):
                vals["group_by_based_on"] = ch["group_by_based_on"]
            if ch.get("time_interval"):
                vals["time_interval"] = ch["time_interval"]
            frappe.db.set_value("Dashboard Chart", ch["name"], vals)
        else:
            doc = frappe.new_doc("Dashboard Chart")
            for k, v in ch.items():
                setattr(doc, k, v)
            doc.chart_name = ch["name"]
            doc.is_standard = 0
            doc.is_public = 1
            doc.module = "Alpha Assignment Management"
            doc.insert(ignore_permissions=True)


def create_custom_html_block():
    html = """<div id="ceo-top-bottom" style="padding: 10px;">
<h5 style="margin-bottom: 15px;"><b>Employee Task Performance</b></h5>
<div class="row">
    <div class="col-md-6">
        <div style="border-left: 4px solid #28a745; padding: 15px; background: #f8f9fa; border-radius: 4px;">
            <h6 style="color: #28a745; font-weight: bold; margin-bottom: 10px;">Top 5 - Most Completed Tasks</h6>
            <div id="top-5-list"><p class="text-muted">Loading...</p></div>
        </div>
    </div>
    <div class="col-md-6">
        <div style="border-left: 4px solid #dc3545; padding: 15px; background: #f8f9fa; border-radius: 4px;">
            <h6 style="color: #dc3545; font-weight: bold; margin-bottom: 10px;">Bottom 5 - Needs Attention</h6>
            <div id="bottom-5-list"><p class="text-muted">Loading...</p></div>
        </div>
    </div>
</div>
</div>"""

    script = """frappe.ready(function() {
    frappe.call({
        method: 'alpha_assignment_mgmt.alpha_assignment_management.api.ceo_dashboard.get_ceo_top_bottom',
        callback: function(r) {
            if (!r.message) return;
            var data = r.message;
            renderList('#top-5-list', data.top5, true);
            renderList('#bottom-5-list', data.bottom5, false);
        }
    });

    function renderList(selector, items, isTop) {
        if (!items || !items.length) {
            $(selector).html('<p class="text-muted">No data</p>');
            return;
        }
        var html = '<table class="table table-sm table-borderless mb-0">';
        html += '<tr style="font-weight:bold;color:#666;font-size:12px;"><td style="width:30px">#</td><td>Employee</td><td style="width:80px;text-align:center;">Completed</td><td style="width:80px;text-align:center;">Pending</td></tr>';
        items.forEach(function(item, i) {
            var rank = i + 1;
            var medal = '';
            if (isTop && rank === 1) medal = ' ';
            else if (isTop && rank === 2) medal = ' ';
            else if (isTop && rank === 3) medal = ' ';
            var completedBadge = item.completed > 0
                ? '<span class="badge" style="background:#28a745;color:#fff;font-size:12px;">' + item.completed + '</span>'
                : '<span class="badge" style="background:#6c757d;color:#fff;font-size:12px;">0</span>';
            var pendingBadge = item.pending > 0
                ? '<span class="badge" style="background:#dc3545;color:#fff;font-size:12px;">' + item.pending + '</span>'
                : '<span class="badge" style="background:#28a745;color:#fff;font-size:12px;">0</span>';
            html += '<tr><td><b>' + rank + '</b></td><td>' + item.name + medal + '</td><td style="text-align:center;">' + completedBadge + '</td><td style="text-align:center;">' + pendingBadge + '</td></tr>';
        });
        html += '</table>';
        $(selector).html(html);
    }
});"""

    block_name = "CEO Top Bottom Employees"
    if frappe.db.exists("Custom HTML Block", block_name):
        frappe.db.set_value("Custom HTML Block", block_name, {
            "html": html, "script": script, "private": 0,
        })
    else:
        doc = frappe.new_doc("Custom HTML Block")
        doc.name = block_name
        doc.html = html
        doc.script = script
        doc.private = 0
        doc.insert(ignore_permissions=True)


def setup_ceo_workspace():
    ceo_content = json.dumps([
        {"id": "h1", "type": "header", "data": {"text": "<span class=\"h4\"><b>CEO Dashboard</b></span>", "col": 12}},
        {"id": "p1", "type": "paragraph", "data": {"text": "Overview of employee task completion and project productivity.", "col": 12}},
        {"id": "nc1", "type": "number_card", "data": {"number_card_name": "Tasks Completed", "col": 3}},
        {"id": "nc2", "type": "number_card", "data": {"number_card_name": "Tasks Pending", "col": 3}},
        {"id": "nc3", "type": "number_card", "data": {"number_card_name": "Active Staff", "col": 3}},
        {"id": "nc4", "type": "number_card", "data": {"number_card_name": "Active Clients", "col": 3}},
        {"id": "cb1", "type": "custom_block", "data": {"custom_block_name": "CEO Top Bottom Employees", "col": 12}},
        {"id": "c1", "type": "chart", "data": {"chart_name": "Employee Performance Trend", "col": 12}},
        {"id": "c2", "type": "chart", "data": {"chart_name": "Tasks by Status", "col": 6}},
        {"id": "c3", "type": "chart", "data": {"chart_name": "Tasks Completed Over Time", "col": 6}},
        {"id": "c4", "type": "chart", "data": {"chart_name": "Open Tasks by Project", "col": 6}},
        {"id": "c5", "type": "chart", "data": {"chart_name": "Task Priority Distribution", "col": 6}},
        {"id": "sp1", "type": "spacer", "data": {"col": 12}},
        {"id": "sh2", "type": "header", "data": {"text": "<span class=\"h5\"><b>Quick Actions</b></span>", "col": 12}},
        {"id": "s1", "type": "shortcut", "data": {"shortcut_name": "Staff Productivity", "col": 3}},
        {"id": "s2", "type": "shortcut", "data": {"shortcut_name": "Employee Performance", "col": 3}},
    ])

    # Use SQL to avoid developer mode check on standard DocType
    if frappe.db.exists("Workspace", "CEO"):
        frappe.db.set_value("Workspace", "CEO", "content", ceo_content)
    else:
        frappe.db.sql("""
            INSERT INTO `tabWorkspace`
            (name, label, module, is_hidden, public, content, docstatus, creation, modified, owner, modified_by)
            VALUES ('CEO', 'CEO', 'Alpha Assignment Management', 0, 1, %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
        """, (ceo_content,))

    # Setup child tables
    _setup_workspace_children("CEO", ceo_content)


def setup_aims_desk_workspace():
    aims_content = json.dumps([
        {"id": "h1", "type": "header", "data": {"text": "<span class=\"h4\"><b>AIMS Desk</b></span>", "col": 12}},
        {"id": "p1", "type": "paragraph", "data": {"text": "Manage client assignments from origination to closure.", "col": 12}},
        {"id": "nc1", "type": "number_card", "data": {"number_card_name": "Active Assignments", "col": 3}},
        {"id": "nc2", "type": "number_card", "data": {"number_card_name": "Active Projects", "col": 3}},
        {"id": "nc3", "type": "number_card", "data": {"number_card_name": "Tasks Completed", "col": 3}},
        {"id": "nc4", "type": "number_card", "data": {"number_card_name": "Tasks Pending", "col": 3}},
        {"id": "c1", "type": "chart", "data": {"chart_name": "Employee Performance Trend", "col": 12}},
        {"id": "sp1", "type": "spacer", "data": {"col": 12}},
        {"id": "sh2", "type": "header", "data": {"text": "<span class=\"h5\"><b>Quick Actions</b></span>", "col": 12}},
        {"id": "s1", "type": "shortcut", "data": {"shortcut_name": "New Assignment Origination", "col": 3}},
        {"id": "s2", "type": "shortcut", "data": {"shortcut_name": "All Assignments", "col": 3}},
        {"id": "s3", "type": "shortcut", "data": {"shortcut_name": "My Tasks", "col": 3}},
        {"id": "s4", "type": "shortcut", "data": {"shortcut_name": "Staff Productivity", "col": 3}},
    ])

    if frappe.db.exists("Workspace", "AIMS Desk"):
        frappe.db.set_value("Workspace", "AIMS Desk", "content", aims_content)


def _setup_workspace_children(workspace_name, content_json):
    """Set up chart and number_card child tables from content JSON."""
    content = json.loads(content_json)

    # Clear existing children
    frappe.db.sql(
        "DELETE FROM `tabWorkspace Chart` WHERE parent = %s AND parenttype = 'Workspace'",
        workspace_name,
    )
    frappe.db.sql(
        "DELETE FROM `tabWorkspace Number Card` WHERE parent = %s AND parenttype = 'Workspace'",
        workspace_name,
    )
    frappe.db.sql(
        "DELETE FROM `tabWorkspace Custom Block` WHERE parent = %s AND parenttype = 'Workspace'",
        workspace_name,
    )

    idx_chart = 0
    idx_card = 0
    idx_cb = 0

    for block in content:
        btype = block.get("type")
        data = block.get("data", {})

        if btype == "chart":
            chart_name = data.get("chart_name")
            if chart_name and frappe.db.exists("Dashboard Chart", chart_name):
                frappe.db.sql("""
                    INSERT INTO `tabWorkspace Chart`
                    (name, chart_name, label, parent, parentfield, parenttype, idx, docstatus, creation, modified, owner, modified_by)
                    VALUES (%s, %s, %s, %s, 'charts', 'Workspace', %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
                """, (f"{workspace_name}_c{idx_chart}", chart_name, chart_name, workspace_name, idx_chart))
                idx_chart += 1

        elif btype == "number_card":
            nc_name = data.get("number_card_name")
            if nc_name and frappe.db.exists("Number Card", nc_name):
                frappe.db.sql("""
                    INSERT INTO `tabWorkspace Number Card`
                    (name, number_card_name, label, parent, parentfield, parenttype, idx, docstatus, creation, modified, owner, modified_by)
                    VALUES (%s, %s, %s, %s, 'number_cards', 'Workspace', %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
                """, (f"{workspace_name}_nc{idx_card}", nc_name, nc_name, workspace_name, idx_card))
                idx_card += 1

        elif btype == "custom_block":
            cb_name = data.get("custom_block_name")
            if cb_name and frappe.db.exists("Custom HTML Block", cb_name):
                frappe.db.sql("""
                    INSERT INTO `tabWorkspace Custom Block`
                    (name, custom_block_name, label, parent, parentfield, parenttype, idx, docstatus, creation, modified, owner, modified_by)
                    VALUES (%s, %s, %s, %s, 'custom_blocks', 'Workspace', %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
                """, (f"{workspace_name}_cb{idx_cb}", cb_name, cb_name, workspace_name, idx_cb))
                idx_cb += 1


def create_ceo_api_method():
    """Ensure the CEO dashboard API method file exists."""
    api_dir = os.path.join(
        os.path.dirname(__file__),
        "alpha_assignment_management",
        "api",
    )
    os.makedirs(api_dir, exist_ok=True)

    init_file = os.path.join(api_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("")

    api_file = os.path.join(api_dir, "ceo_dashboard.py")
    if not os.path.exists(api_file):
        with open(api_file, "w") as f:
            f.write("""import frappe


@frappe.whitelist()
def get_ceo_top_bottom():
    employees = frappe.get_all(
        "Employee",
        filters={"status": "Active", "user_id": ["is", "set"]},
        fields=["name", "employee_name", "user_id"],
    )
    if not employees:
        return {"top5": [], "bottom5": []}

    results = []
    for emp in employees:
        uid = emp.user_id
        completed = frappe.db.sql(\"\"\"
            SELECT COUNT(DISTINCT t.name)
            FROM tabTask t
            WHERE t.status = 'Completed'
            AND (JSON_CONTAINS(t._assign, %s) OR t.owner = %s)
        \"\"\", (frappe.json.dumps(uid), uid))[0][0]

        pending = frappe.db.sql(\"\"\"
            SELECT COUNT(DISTINCT t.name)
            FROM tabTask t
            WHERE t.status IN ('Open', 'Working', 'Overdue')
            AND (JSON_CONTAINS(t._assign, %s) OR t.owner = %s)
        \"\"\", (frappe.json.dumps(uid), uid))[0][0]

        results.append({
            "name": emp.employee_name or emp.name,
            "completed": completed,
            "pending": pending,
        })

    results.sort(key=lambda x: x["completed"], reverse=True)
    return {
        "top5": results[:5],
        "bottom5": list(reversed(results[-5:])) if len(results) >= 5 else list(reversed(results)),
    }
""")
