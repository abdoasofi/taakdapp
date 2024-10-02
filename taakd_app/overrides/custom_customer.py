from erpnext.selling.doctype.customer.customer import Customer
import frappe
from frappe import _, msgprint

class CustomCustomer(Customer):
    def after_insert(self):
        self.create_user()
    def create_user(self):
        if frappe.db.exists("User", {"email":self.email}):
            return True 
        else:
            new_doc = frappe.new_doc("User")
            new_doc.email = self.email
            new_doc.first_name = self.customer_name
            new_doc.enabled = True
            new_doc.module_profile = ""
            new_doc.role_profile_name = "Company"
            new_doc.insert(ignore_permissions = True)
            return new_doc    