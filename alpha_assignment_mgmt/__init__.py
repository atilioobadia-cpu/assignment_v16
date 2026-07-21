__version__ = "0.0.1"

import frappe

frappe.sendmail_default_delayed = True
_sendmail = frappe.sendmail

def _sendmail_now(*args, **kwargs):
	kwargs["delayed"] = False
	return _sendmail(*args, **kwargs)

frappe.sendmail = _sendmail_now
