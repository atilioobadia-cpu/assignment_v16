import frappe


def project_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	roles = frappe.get_roles(user)
	if "System Manager" in roles or "Alpha Partner/Director" in roles:
		return ""
	if "Alpha Client" in roles:
		return f"""(`tabProject`.`customer` IN (
			SELECT `tabCustomer`.`name` FROM `tabCustomer`
			WHERE `tabCustomer`.`custom_portal_user` = %(user)s
		))"""
	return ""


def project_has_permission(doc, ptype, user):
	roles = frappe.get_roles(user)
	if "System Manager" in roles or "Alpha Partner/Director" in roles:
		return True
	if "Alpha Client" in roles and doc.customer:
		portal_user = frappe.db.get_value("Customer", doc.customer, "custom_portal_user")
		if portal_user == user:
			return True
	return False


def assignment_origination_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	roles = frappe.get_roles(user)
	if "System Manager" in roles or "Alpha Partner/Director" in roles:
		return ""
	if "Alpha Client" in roles:
		return f"""(`tabAlpha Assignment Origination`.`customer` IN (
			SELECT `tabCustomer`.`name` FROM `tabCustomer`
			WHERE `tabCustomer`.`custom_portal_user` = %(user)s
		))"""
	return ""


def assignment_origination_has_permission(doc, ptype, user):
	roles = frappe.get_roles(user)
	if "System Manager" in roles or "Alpha Partner/Director" in roles:
		return True
	if "Alpha Client" in roles and doc.customer:
		portal_user = frappe.db.get_value("Customer", doc.customer, "custom_portal_user")
		if portal_user == user:
			return True
	return False


def document_request_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	roles = frappe.get_roles(user)
	if "System Manager" in roles or "Alpha Partner/Director" in roles:
		return ""
	if "Alpha Client" in roles:
		return f"""(`tabDocument Request Register`.`customer` IN (
			SELECT `tabCustomer`.`name` FROM `tabCustomer`
			WHERE `tabCustomer`.`custom_portal_user` = %(user)s
		))"""
	return ""


def document_request_has_permission(doc, ptype, user):
	roles = frappe.get_roles(user)
	if "System Manager" in roles or "Alpha Partner/Director" in roles:
		return True
	if "Alpha Client" in roles and doc.get("customer"):
		portal_user = frappe.db.get_value("Customer", doc.customer, "custom_portal_user")
		if portal_user == user:
			return True
	return False


def closure_certificate_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	roles = frappe.get_roles(user)
	if "System Manager" in roles or "Alpha Partner/Director" in roles:
		return ""
	if "Alpha Client" in roles:
		return f"""(`tabAssignment Closure Certificate`.`project` IN (
			SELECT `tabProject`.`name` FROM `tabProject`
			WHERE `tabProject`.`customer` IN (
				SELECT `tabCustomer`.`name` FROM `tabCustomer`
				WHERE `tabCustomer`.`custom_portal_user` = %(user)s
			)
		))"""
	return ""


def closure_certificate_has_permission(doc, ptype, user):
	roles = frappe.get_roles(user)
	if "System Manager" in roles or "Alpha Partner/Director" in roles:
		return True
	if "Alpha Client" in roles and doc.get("project"):
		customer = frappe.db.get_value("Project", doc.project, "customer")
		if customer:
			portal_user = frappe.db.get_value("Customer", customer, "custom_portal_user")
			if portal_user == user:
				return True
	return False


def client_delay_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	roles = frappe.get_roles(user)
	if "System Manager" in roles or "Alpha Partner/Director" in roles:
		return ""
	if "Alpha Client" in roles:
		return f"""(`tabClient Delay Log`.`customer` IN (
			SELECT `tabCustomer`.`name` FROM `tabCustomer`
			WHERE `tabCustomer`.`custom_portal_user` = %(user)s
		))"""
	return ""


def client_delay_has_permission(doc, ptype, user):
	roles = frappe.get_roles(user)
	if "System Manager" in roles or "Alpha Partner/Director" in roles:
		return True
	if "Alpha Client" in roles and doc.get("customer"):
		portal_user = frappe.db.get_value("Customer", doc.customer, "custom_portal_user")
		if portal_user == user:
			return True
	return False
