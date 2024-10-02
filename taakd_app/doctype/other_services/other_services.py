# Copyright (c) 2024, Asofi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OtherServices(Document):
	def before_save(self):
		self.service_price = self.get_item_price(service)

	def get_item_price(self,item):
		try:
			price_data = frappe.db.get_list(
				"Item Price",
				fields=['price_list_rate'],
				filters={'item_code': item},
				limit=1
			)
			# Check if we got any results
			if price_data:
				return price_data[0].price_list_rate  # Extracting the price
			else:
				return 0  # Handle the case where no price was found
		except Exception as e:
			print("An error occurred while fetching item price:", str(e))