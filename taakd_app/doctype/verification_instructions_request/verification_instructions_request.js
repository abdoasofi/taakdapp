// Copyright (c) 2024, Asofi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Verification Instructions Request", {
	refresh(frm) {
		frm.fields_dict['education_information'].grid.get_field('country').get_query = function(doc) {
			return {
				"filters": {
                    is_group: 1,
                    location_type:"Country",
				}
			}
		};
		frm.fields_dict['education_information'].grid.get_field('city').get_query = function(doc) {
			return {
				"filters": {
                    is_group: 1,
                    location_type:"City",
                    parent_location:frm.doc.country
				}
			}
		};
		frm.fields_dict['education_information'].grid.get_field('governorate').get_query = function(doc) {
			return {
				"filters": {
                    location_type:"Governorate",
                    parent_location:frm.doc.city
				}
			}
		};                
		frm.fields_dict['employment_history'].grid.get_field('country').get_query = function(doc) {
			return {
				"filters": {
                    is_group: 1,
                    location_type:"Country",
				}
			}
		};
		frm.fields_dict['employment_history'].grid.get_field('city').get_query = function(doc) {
			return {
				"filters": {
                    is_group: 1,
                    location_type:"City",
                    parent_location:frm.doc.country
				}
			}
		};
		frm.fields_dict['employment_history'].grid.get_field('governorate').get_query = function(doc) {
			return {
				"filters": {
                    location_type:"Governorate",
                    parent_location:frm.doc.city
				}
			}
		}; 		        
        frm.set_query('country', () => {
            let filters = {
                    is_group: 1,
                    location_type:"Country",

                };


            return {filters: filters};
        });
        frm.set_query('city', () => {
            let filters = {
                    is_group: 1,
                    location_type:"City",
                    parent_location:frm.doc.country
                };


            return {filters: filters};
        });
        frm.set_query('governorate', () => {
            let filters = {
                    // is_group: 1,
                    location_type:"Governorate",
                    parent_location:frm.doc.city
                };


            return {filters: filters};
        });                
	},
});
