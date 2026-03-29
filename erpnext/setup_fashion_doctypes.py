import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def setup_all():
	frappe.flags.in_install = True
	create_color_master()
	create_size_set()
	create_style_master()
	create_item_custom_fields()
	frappe.db.commit()
	print("Fashion House Phase 1 Customizations Applied Successfully!")

def create_color_master():
	if not frappe.db.exists("DocType", "Color Master"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Color Master",
			"module": "Manufacturing",
			"custom": 1,
			"autoname": "field:color_name",
			"fields": [
				{"fieldname": "color_name", "fieldtype": "Data", "label": "Color Name", "reqd": 1, "unique": 1},
				{"fieldname": "color_code", "fieldtype": "Data", "label": "Color Code (Pantone/Hex)"},
				{"fieldname": "hex_value", "fieldtype": "Color", "label": "Hex Value"}
			],
			"permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
							{"role": "Manufacturing User", "read": 1, "write": 1, "create": 1},
							{"role": "Item Manager", "read": 1, "write": 1, "create": 1}]
		})
		doc.insert(ignore_permissions=True)
		print("Created Doctype: Color Master")
	else:
		print("Doctype Color Master already exists")

def create_size_set():
	if not frappe.db.exists("DocType", "Size Set"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Size Set",
			"module": "Manufacturing",
			"custom": 1,
			"autoname": "field:size_name",
			"fields": [
				{"fieldname": "size_name", "fieldtype": "Data", "label": "Size Name", "reqd": 1, "unique": 1},
				{"fieldname": "description", "fieldtype": "Small Text", "label": "Description"}
			],
			"permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
							{"role": "Manufacturing User", "read": 1, "write": 1, "create": 1},
							{"role": "Item Manager", "read": 1, "write": 1, "create": 1}]
		})
		doc.insert(ignore_permissions=True)
		print("Created Doctype: Size Set")
	else:
		print("Doctype Size Set already exists")

def create_style_master():
	if not frappe.db.exists("DocType", "Style Master"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Style Master",
			"module": "Manufacturing",
			"custom": 1,
			"autoname": "field:style_no",
			"fields": [
				{"fieldname": "style_no", "fieldtype": "Data", "label": "Style No", "reqd": 1, "unique": 1},
				{"fieldname": "garment_type", "fieldtype": "Select", "label": "Garment Type", "options": "\nShirt\nPant\nPanjabi\nKurti\nSaree\nSalwar Kameez\nT-Shirt\nPolo Shirt\nJacket"},
				{"fieldname": "season", "fieldtype": "Select", "label": "Season", "options": "\nSpring\nSummer\nAutumn\nWinter\nEid\nPuja\nBaishakh"},
				{"fieldname": "base_fabric", "fieldtype": "Data", "label": "Base Fabric"},
				{"fieldname": "wash_type", "fieldtype": "Data", "label": "Wash Type"},
				{"fieldname": "target_mrp", "fieldtype": "Currency", "label": "Target MRP"},
				{"fieldname": "images_section", "fieldtype": "Section Break", "label": "Images & Tech Pack"},
				{"fieldname": "front_image", "fieldtype": "Attach Image", "label": "Front Image"},
				{"fieldname": "column_break_1", "fieldtype": "Column Break"},
				{"fieldname": "back_image", "fieldtype": "Attach Image", "label": "Back Image"},
				{"fieldname": "section_break_2", "fieldtype": "Section Break"},
				{"fieldname": "tech_pack", "fieldtype": "Attach", "label": "Tech Pack / Spec Sheet"}
			],
			"permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
							{"role": "Manufacturing Manager", "read": 1, "write": 1, "create": 1},
							{"role": "Item Manager", "read": 1, "write": 1, "create": 1}],
			"title_field": "style_no",
			"search_fields": "garment_type, season"
		})
		doc.insert(ignore_permissions=True)
		print("Created Doctype: Style Master")
	else:
		print("Doctype Style Master already exists")

def create_item_custom_fields():
	custom_fields = {
		"Item": [
			{"fieldname": "fashion_section", "fieldtype": "Section Break", "label": "Fashion & Garments", "insert_after": "item_group"},
			{"fieldname": "custom_style", "fieldtype": "Link", "label": "Style", "options": "Style Master", "insert_after": "fashion_section"},
			{"fieldname": "custom_color", "fieldtype": "Link", "label": "Color", "options": "Color Master", "insert_after": "custom_style"},
			{"fieldname": "custom_size", "fieldtype": "Link", "label": "Size", "options": "Size Set", "insert_after": "custom_color"},
			{"fieldname": "custom_season", "fieldtype": "Select", "label": "Season", "options": "\nSpring\nSummer\nAutumn\nWinter\nEid\nPuja\nBaishakh", "insert_after": "custom_size"},
			{"fieldname": "custom_mrp", "fieldtype": "Currency", "label": "MRP (Maximum Retail Price)", "insert_after": "custom_season"}
		]
	}
	create_custom_fields(custom_fields)
	print("Created Custom Fields for Item")
