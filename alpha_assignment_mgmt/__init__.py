__version__ = "0.0.1"

import frappe

frappe.sendmail_default_delayed = True
_sendmail = frappe.sendmail

def _sendmail_now(*args, **kwargs):
	kwargs["delayed"] = False
	return _sendmail(*args, **kwargs)

frappe.sendmail = _sendmail_now

from frappe.email.doctype.email_account.email_account import EmailAccount, get_port, EmailServer

def _patched_get_incoming_server(self, in_receive=False, email_sync_rule="UNSEEN"):
	oauth_token = self.get_oauth_token()
	args = frappe._dict(
		{
			"email_account_name": self.email_account_name,
			"email_account": self.name,
			"host": self.email_server,
			"use_ssl": self.use_ssl,
			"use_starttls": self.use_starttls,
			"username": getattr(self, "login_id", None) or self.email_id,
			"use_imap": self.use_imap,
			"email_sync_rule": email_sync_rule,
			"incoming_port": get_port(self),
			"initial_sync_count": self.initial_sync_count or 100,
			"use_oauth": self.auth_method == "OAuth",
			"access_token": oauth_token.get_password("access_token") if oauth_token else None,
		}
	)
	try:
		args.password = self.get_password()
	except Exception:
		pass
	if not args.get("host"):
		frappe.throw(frappe._("{0} is required").format("Email Server"))
	if self.flags.validate_imap_pop_connection:
		args.timeout = 30
	email_server = EmailServer(frappe._dict(args))
	self.check_email_server_connection(email_server, in_receive)
	if not in_receive and self.use_imap:
		email_server.imap.logout()
	return email_server

EmailAccount.get_incoming_server = _patched_get_incoming_server

_original_build_email_sync_rule = EmailAccount.build_email_sync_rule

def _patched_build_email_sync_rule(self):
	if not self.use_imap:
		return "UNSEEN"
	if self.email_sync_option == "ALL":
		from frappe.email.doctype.email_account.email_account import get_max_email_uid
		max_uid = get_max_email_uid(self.name)
		if max_uid <= 1:
			return "UID 1:*"
		return f"UID {max_uid}:*"
	return self.email_sync_option or "UNSEEN"

EmailAccount.build_email_sync_rule = _patched_build_email_sync_rule

try:
	from helpdesk.overrides.email_account import CustomEmailAccount
	CustomEmailAccount.get_incoming_server = _patched_get_incoming_server
	CustomEmailAccount.build_email_sync_rule = _patched_build_email_sync_rule
except ImportError:
	pass
