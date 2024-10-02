import frappe


@frappe.whitelist(allow_guest=True)
def get_request(user_id):
    pass
def update_request(request):
    pass
  