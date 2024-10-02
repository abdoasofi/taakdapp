# Copyright (c) 2024, Asofi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class ApplicantInvitation(Document):
	def before_save(self):
		self.add_company_information()
		self.add_full_name()
		self.package_price = self.get_item_price(self.package)
		self.other_services_price  =  self.sum_other_services_price()
		self.sum_total_price()
	def on_submit(self):
		self.create_user()
		
		if self.payd_from == "Employee":
			# Create or retrieve the individual Customer f
			customer_doc = self.create_customer(
				customer_name=self._full_name, 
				customer_type="Individual",
				email=self.email, 
				customer_group="Applicants"
			)
		else:
			# Create or retrieve the company Customer
			customer_doc = self.create_customer(
				customer_name=self.company_name, 
				customer_type="Company",
				email=self.company_email, 
				customer_group="Companies"
			)
		customer_name = customer_doc.name			
		# Now create the Sales Invoice with the correct Customer identifier
		sales_invoice_name = self.create_sales_invoice(customer_name)
		
		# Proceed to create Verification Instructions Request
		self.create_verification_instructions_request(sales_invoice_name)

	def on_cancel(self):
		pass	

	def add_full_name(self):
		middle_name = self.middle_name
		if self.middle_name == None: 
			middle_name = ""
		self._full_name = f"{self.first_name} {middle_name} {self.last_name}"  

	def add_company_information(self):
		user = frappe.get_doc("User", frappe.session.user)
		self.db_set("company_name",user.full_name)
		if user.full_name == "Administrator":
			self.db_set("company_email","administrator") 
		else :
			self.db_set("company_email",user.email)

	def create_user(self):
		if frappe.db.exists("User", {"email":self.email}):
			return True 
		else:
			new_doc = frappe.new_doc("User")
			new_doc.email = self.email
			new_doc.first_name = self.first_name
			new_doc.last_name = self.last_name
			new_doc.middle_name = self.middle_name
			new_doc.enabled = True
			new_doc.language = self.language
			new_doc.module_profile = ""
			new_doc.role_profile_name = "Applicant"
			new_doc.insert(ignore_permissions = True)
			return new_doc   

	def create_customer(self, customer_name, customer_type, email, customer_group):
		"""Creates a Customer if not exists and returns the Customer document.

		Args:
			customer_name (str): The name of the customer.
			customer_type (str): Type of customer. Accepted values: "Individual", "Company".
			email (str): The email of the customer.
			customer_group (str): The customer group. E.g., "Applicants", "Companies".
			
		Returns:
			doc: A Frappe Customer document.
		"""
		if frappe.db.exists(
							"Customer",
							{
								"customer_name": customer_name,
								"email": email
							}):
			frappe.logger().debug(f"Customer '{customer_name}' already exists.")
			customer_doc = frappe.get_doc("Customer", {"customer_name": customer_name})
		else:
			new_doc = frappe.new_doc("Customer")
			new_doc.customer_name = customer_name
			new_doc.customer_type = customer_type
			new_doc.customer_group = customer_group
			new_doc.email = email
			new_doc.insert(ignore_permissions=True)
			customer_doc = new_doc
			frappe.logger().debug(f"Customer Created: {customer_doc.name}")
		
		return customer_doc
			
	def create_verification_instructions_request(self,sales_invoice_name):
		new_doc = frappe.new_doc("Verification Instructions Request")
		new_doc.payd_from = self.payd_from
		new_doc.user_id = self.email
		new_doc.company_submitting_application = self.company_email
		new_doc.language = self.language
		new_doc.sales_invoice = sales_invoice_name
		# new_doc.sales_invoice = sales_invoice_name
		new_doc.insert(ignore_permissions = True)
		return new_doc  

	def create_sales_invoice(self,customer):
			if not customer:
				frappe.throw(_("Customer is not set. Cannot create Sales Invoice.") )   
			sales_invoice = frappe.get_doc(
				{
					"doctype": "Sales Invoice",
					"customer": customer,
				}
			)
			self.preparing_the_sales_invoice(self.other_services, sales_invoice)
			sales_invoice.save(ignore_permissions = True)

			return sales_invoice
			
	def preparing_the_sales_invoice(self, list_items, sales_invoice):
		for i in list_items:
			is_stock_item = frappe.get_value("Item", i.service, "is_stock_item")
			if is_stock_item:
				sales_invoice.append(
					"items",
					{
						"item_code": i.service,
						"qty": 1,
						"uom":"Nos",
					},
				)
			elif bundle := frappe.db.exists("Product Bundle", {"new_item_code": i.service}):
				self.preparing(bundle, sales_invoice)
		if self.package:
			self.preparing(self.package, sales_invoice)   

	def preparing(self, bundle, sales_invoice):
		bundle = frappe.get_doc("Product Bundle", bundle)
		for b_i in bundle.items:
			sales_invoice.append(
				"items",
				{
					"item_code": b_i.item_code,
					"qty": 1,
					"uom":"Nos",
				},
			)

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

	def sum_other_services_price (self):
		sum_other_services_price = 0
		if self.other_services:
			for i in self.other_services:
				sum_other_services_price += self.get_item_price(i.service)
			return sum_other_services_price

	def sum_total_price (self):
		self.total_price  =  self.sum_other_services_price() + self.get_item_price(self.package)

	@frappe.whitelist()
	def get_filtered_item_codes(self):
		try:
			parent = self.package 
			item_codes = frappe.db.sql_list(
				"""
				SELECT item_code
				FROM `tabProduct Bundle Item`
				WHERE parent = %s
				""", (parent)  # Ensure the parameter is a tuple
			)
			return item_codes
		except Exception as e:
			frappe.log_error(frappe.get_traceback(), "Error in get_filtered_item_codes")
			return []  # Return an empty list on error
