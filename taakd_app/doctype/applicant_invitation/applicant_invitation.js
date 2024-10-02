// // Copyright (c) 2024, Asofi and contributors
// // For license information, please see license.txt

frappe.ui.form.on("Applicant Invitation", {
    refresh(frm) {
        frm.trigger('package');
    },
    onload: function(frm){
        frm.trigger('package');
	},
    package: function(frm){
        item_list = [];
        frappe.call({
            doc: frm.doc,
            method: 'get_filtered_item_codes', 
            callback: function(r){
                if (r.message) {
                    item_list = r.message;
                    frm.fields_dict['other_services'].grid.get_field('service').get_query = function(doc) {
                        return {
                            "filters": {
                                "item_code": ["in", item_list] 
                            }
                        }
                    };
                    
                    frm.refresh_field('other_services');
                }
            }
        });
    },
    other_services_add: function(frm, cdt, cdn) {
        // حدث عند إضافة صف جديد إلى Child Table
        let row = locals[cdt][cdn]; 
        row.service_price = 0;
    }

});
frappe.ui.form.on('Other Services', {
    service: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.service) {
            // استعلام السعر من جدول Item Price
            frappe.db.get_list('Item Price', {
                fields: ['price_list_rate'],
                filters: {
                    item_code: row.service
                },
                limit: 1 // لاسترداد سعر واحد
            }).then((data) => {
                if (data.length > 0) {
                    row.service_price = data[0].price_list_rate; // الحصول على السعر
                } else {
                    row.service_price = 0; // إذا لم يتم العثور على سعر
                }
                frm.refresh_field('other_services'); // تحديث الحقول لعرض القيمة الجديدة
            }).catch((error) => {
                console.error("حدث خطأ أثناء جلب السعر:", error);
                row.service_price = 0; // تأكد من تعيين السعر إلى 0 في حالة وجود خطأ
                frm.refresh_field('other_services');
            });
        } else {
            row.service_price = 0; // إذا لم يتم تحديد الخدمة
            frm.refresh_field('other_services'); // تحديث الحقول لعرض القيمة الجديدة
        }
    }
});