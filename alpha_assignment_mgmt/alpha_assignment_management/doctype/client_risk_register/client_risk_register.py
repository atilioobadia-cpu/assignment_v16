import frappe
from frappe.model.document import Document

class ClientRiskRegister(Document):
	def validate(self):
		if not self.status:
			self.status = "Open"
		self.compute_risk_score()

	def compute_risk_score(self):
		rows = self.get("risk_dimension_scores") or []
		if not rows:
			self.total_risk_score = 0
			self.risk_band = ""
			return

		total_weight = sum(float(row.weight or 0) for row in rows)
		if total_weight <= 0:
			frappe.throw("Risk Dimension Scores must have a total weight greater than 0. Please assign weights across the dimensions.")

		weighted = sum(float(row.score or 0) * (float(row.weight or 0) / total_weight) for row in rows)
		self.total_risk_score = round(weighted, 2)
		self.risk_band = self.get_band(weighted)

	def get_band(self, score):
		if score >= 4.0:
			return "Critical"
		if score >= 3.0:
			return "High"
		if score >= 2.0:
			return "Medium"
		return "Low"
