# Copyright (c) 2024, Asofi and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class VerificationInstructionsRequest(Document):
	
	def before_save(self):
		self.add_full_name()

	def add_full_name(self):
		middle_name = self.middle_name
		if self.middle_name == None: 
			middle_name = ""
		# self.full_name = f"{self.first_name} {middle_name} {self.last_name}"  
