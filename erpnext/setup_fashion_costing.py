import frappe

def setup_all():
	frappe.flags.in_install = True
	create_monthly_factory_costing()
	create_costing_child_tables()
	create_garment_costing_sheet()
	create_client_scripts()
	frappe.db.commit()
	print("Fashion House Phase 2: Costing Setup Applied Successfully!")

def create_monthly_factory_costing():
	if not frappe.db.exists("DocType", "Monthly Factory Costing"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Monthly Factory Costing",
			"module": "Manufacturing",
			"custom": 1,
			"autoname": "format:MFC-{YYYY}-{MM}-{#####}",
			"fields": [
				{"fieldname": "month", "fieldtype": "Select", "label": "Month", "options": "\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember", "reqd": 1, "in_list_view": 1},
				{"fieldname": "year", "fieldtype": "Data", "label": "Year", "reqd": 1, "in_list_view": 1},
				
				{"fieldname": "sb_expenses", "fieldtype": "Section Break", "label": "Monthly Expenses"},
				{"fieldname": "wages", "fieldtype": "Currency", "label": "Total Wages"},
				{"fieldname": "power_and_utilities", "fieldtype": "Currency", "label": "Power & Utilities"},
				{"fieldname": "factory_rent", "fieldtype": "Currency", "label": "Factory Rent"},
				{"fieldname": "overheads_and_admin", "fieldtype": "Currency", "label": "Overheads & Admin"},
				{"fieldname": "total_monthly_expense", "fieldtype": "Currency", "label": "Total Monthly Expense", "read_only": 1, "in_list_view": 1},
				
				{"fieldname": "sb_capacity", "fieldtype": "Section Break", "label": "Capacity Details"},
				{"fieldname": "working_days", "fieldtype": "Int", "label": "Working Days", "default": "26"},
				{"fieldname": "total_lines", "fieldtype": "Int", "label": "Total Lines"},
				{"fieldname": "workers_per_line", "fieldtype": "Int", "label": "Workers per Line"},
				{"fieldname": "daily_working_hours", "fieldtype": "Float", "label": "Daily Working Hours", "default": "8"},
				{"fieldname": "target_efficiency", "fieldtype": "Percent", "label": "Target Efficiency %", "default": "100"},
				{"fieldname": "total_available_minutes", "fieldtype": "Int", "label": "Total Available Minutes", "read_only": 1},
				
				{"fieldname": "sb_output", "fieldtype": "Section Break", "label": "Outputs"},
				{"fieldname": "cost_per_minute", "fieldtype": "Currency", "label": "Cost Per Minute (CPM)", "read_only": 1, "in_list_view": 1}
			],
			"permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
							{"role": "Manufacturing Manager", "read": 1, "write": 1, "create": 1}]
		})
		doc.insert(ignore_permissions=True)
		print("Created Doctype: Monthly Factory Costing")
	else:
		print("Doctype Monthly Factory Costing already exists")


def create_costing_child_tables():
	if not frappe.db.exists("DocType", "Garment Costing Fabric Item"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Garment Costing Fabric Item",
			"module": "Manufacturing",
			"custom": 1,
			"istable": 1,
			"fields": [
				{"fieldname": "item", "fieldtype": "Link", "label": "Fabric Item", "options": "Item", "reqd": 1, "in_list_view": 1},
				{"fieldname": "consumption", "fieldtype": "Float", "label": "Consumption (per Dozen/Pc)", "in_list_view": 1},
				{"fieldname": "wastage_percent", "fieldtype": "Percent", "label": "Wastage %", "in_list_view": 1},
				{"fieldname": "rate", "fieldtype": "Currency", "label": "Rate", "in_list_view": 1},
				{"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "read_only": 1, "in_list_view": 1}
			]
		})
		doc.insert(ignore_permissions=True)
		print("Created Child Table: Garment Costing Fabric Item")
		
	if not frappe.db.exists("DocType", "Garment Costing Trim Item"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Garment Costing Trim Item",
			"module": "Manufacturing",
			"custom": 1,
			"istable": 1,
			"fields": [
				{"fieldname": "item", "fieldtype": "Link", "label": "Trim Item", "options": "Item", "reqd": 1, "in_list_view": 1},
				{"fieldname": "quantity", "fieldtype": "Float", "label": "Quantity", "in_list_view": 1},
				{"fieldname": "rate", "fieldtype": "Currency", "label": "Rate", "in_list_view": 1},
				{"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "read_only": 1, "in_list_view": 1}
			]
		})
		doc.insert(ignore_permissions=True)
		print("Created Child Table: Garment Costing Trim Item")


def create_garment_costing_sheet():
	if not frappe.db.exists("DocType", "Garment Costing Sheet"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Garment Costing Sheet",
			"module": "Manufacturing",
			"custom": 1,
			"autoname": "format:GCS-{YYYY}-{#####}",
			"fields": [
				{"fieldname": "style", "fieldtype": "Link", "label": "Style", "options": "Style Master", "reqd": 1, "in_list_view": 1},
				{"fieldname": "monthly_costing", "fieldtype": "Link", "label": "Monthly Routing Ref (CPM)", "options": "Monthly Factory Costing", "reqd": 1},
				{"fieldname": "cost_per_minute", "fieldtype": "Currency", "label": "Cost Per Minute", "fetch_from": "monthly_costing.cost_per_minute", "read_only": 1},
				{"fieldname": "sam", "fieldtype": "Float", "label": "Standard Allowed Minutes (SAM)", "reqd": 1},
				{"fieldname": "target_efficiency", "fieldtype": "Percent", "label": "Expected Efficiency %", "default": "70", "reqd": 1},
				{"fieldname": "cm_cost", "fieldtype": "Currency", "label": "Calculated CM Cost", "read_only": 1, "in_list_view": 1},
				
				{"fieldname": "sb_fabric", "fieldtype": "Section Break", "label": "Fabric Costs"},
				{"fieldname": "fabric_items", "fieldtype": "Table", "label": "Fabrics", "options": "Garment Costing Fabric Item"},
				
				{"fieldname": "sb_trims", "fieldtype": "Section Break", "label": "Trims & Accessories"},
				{"fieldname": "trim_items", "fieldtype": "Table", "label": "Trims", "options": "Garment Costing Trim Item"},
				
				{"fieldname": "sb_processing", "fieldtype": "Section Break", "label": "Value Additions & Processing"},
				{"fieldname": "embroidery_cost", "fieldtype": "Currency", "label": "Embroidery Cost"},
				{"fieldname": "print_cost", "fieldtype": "Currency", "label": "Print/Block/Screen Cost"},
				{"fieldname": "wash_cost", "fieldtype": "Currency", "label": "Wash/Dye Cost"},
				{"fieldname": "other_costs", "fieldtype": "Currency", "label": "Testing/Other Costs"},
				
				{"fieldname": "sb_summary", "fieldtype": "Section Break", "label": "Cost Summary & Retail Price"},
				{"fieldname": "total_material_cost", "fieldtype": "Currency", "label": "Total Material Cost (Fabric + Trims)", "read_only": 1},
				{"fieldname": "total_processing_cost", "fieldtype": "Currency", "label": "Total Processing Cost", "read_only": 1},
				{"fieldname": "total_manufacturing_cost", "fieldtype": "Currency", "label": "Total Manufacturing Cost", "read_only": 1},
				{"fieldname": "target_retail_margin", "fieldtype": "Percent", "label": "Target Retail Margin %", "default": "40", "reqd": 1},
				{"fieldname": "calculated_retail_mrp", "fieldtype": "Currency", "label": "Target Retail MRP", "read_only": 1, "in_list_view": 1}
			],
			"permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
							{"role": "Manufacturing Manager", "read": 1, "write": 1, "create": 1}]
		})
		doc.insert(ignore_permissions=True)
		print("Created Doctype: Garment Costing Sheet")
	else:
		print("Doctype Garment Costing Sheet already exists")

def create_client_scripts():
	# 1. MFC Script
	if not frappe.db.exists("Client Script", "Monthly Factory Costing Math"):
		doc = frappe.get_doc({
			"doctype": "Client Script",
			"dt": "Monthly Factory Costing",
			"name": "Monthly Factory Costing Math",
			"module": "Manufacturing",
			"script": """
frappe.ui.form.on('Monthly Factory Costing', {
	wages: function(frm) { calc_mfc(frm); },
	power_and_utilities: function(frm) { calc_mfc(frm); },
	factory_rent: function(frm) { calc_mfc(frm); },
	overheads_and_admin: function(frm) { calc_mfc(frm); },
	working_days: function(frm) { calc_mfc(frm); },
	total_lines: function(frm) { calc_mfc(frm); },
	workers_per_line: function(frm) { calc_mfc(frm); },
	daily_working_hours: function(frm) { calc_mfc(frm); }
});

function calc_mfc(frm) {
	let expenses = (frm.doc.wages || 0) + (frm.doc.power_and_utilities || 0) + (frm.doc.factory_rent || 0) + (frm.doc.overheads_and_admin || 0);
	frm.set_value('total_monthly_expense', expenses);
	
	let minutes = (frm.doc.working_days || 0) * (frm.doc.total_lines || 0) * (frm.doc.workers_per_line || 0) * (frm.doc.daily_working_hours || 0) * 60;
	frm.set_value('total_available_minutes', minutes);
	
	if (minutes > 0) {
		frm.set_value('cost_per_minute', expenses / minutes);
	} else {
		frm.set_value('cost_per_minute', 0);
	}
}
			"""
		})
		doc.insert(ignore_permissions=True)
		print("Created Client Script: Monthly Factory Costing Math")

	# 2. Garment Costing Script
	if not frappe.db.exists("Client Script", "Garment Costing Sheet Math"):
		doc = frappe.get_doc({
			"doctype": "Client Script",
			"dt": "Garment Costing Sheet",
			"name": "Garment Costing Sheet Math",
			"module": "Manufacturing",
			"script": """
frappe.ui.form.on('Garment Costing Sheet', {
	sam: function(frm) { calc_gcs(frm); },
	cost_per_minute: function(frm) { calc_gcs(frm); },
	target_efficiency: function(frm) { calc_gcs(frm); },
	target_retail_margin: function(frm) { calc_gcs(frm); },
	embroidery_cost: function(frm) { calc_gcs(frm); },
	print_cost: function(frm) { calc_gcs(frm); },
	wash_cost: function(frm) { calc_gcs(frm); },
	other_costs: function(frm) { calc_gcs(frm); }
});

frappe.ui.form.on('Garment Costing Fabric Item', {
	consumption: function(frm, cdt, cdn) { calc_fabric(frm, cdt, cdn); },
	wastage_percent: function(frm, cdt, cdn) { calc_fabric(frm, cdt, cdn); },
	rate: function(frm, cdt, cdn) { calc_fabric(frm, cdt, cdn); },
	fabric_items_remove: function(frm) { calc_gcs(frm); }
});

frappe.ui.form.on('Garment Costing Trim Item', {
	quantity: function(frm, cdt, cdn) { calc_trim(frm, cdt, cdn); },
	rate: function(frm, cdt, cdn) { calc_trim(frm, cdt, cdn); },
	trim_items_remove: function(frm) { calc_gcs(frm); }
});

function calc_fabric(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let w_factor = 1 + ((row.wastage_percent || 0) / 100);
	frappe.model.set_value(cdt, cdn, 'amount', (row.consumption || 0) * w_factor * (row.rate || 0));
	calc_gcs(frm);
}

function calc_trim(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, 'amount', (row.quantity || 0) * (row.rate || 0));
	calc_gcs(frm);
}

function calc_gcs(frm) {
	// 1. CM Cost
	let eff = (frm.doc.target_efficiency || 100) / 100;
	if (eff <= 0) eff = 1;
	let cm = ((frm.doc.sam || 0) * (frm.doc.cost_per_minute || 0)) / eff;
	frm.set_value('cm_cost', cm);
	
	// 2. Material Cost
	let mat_cost = 0;
	(frm.doc.fabric_items || []).forEach(r => mat_cost += (r.amount || 0));
	(frm.doc.trim_items || []).forEach(r => mat_cost += (r.amount || 0));
	frm.set_value('total_material_cost', mat_cost);
	
	// 3. Processing Cost
	let proc_cost = (frm.doc.embroidery_cost || 0) + (frm.doc.print_cost || 0) + (frm.doc.wash_cost || 0) + (frm.doc.other_costs || 0);
	frm.set_value('total_processing_cost', proc_cost);
	
	// 4. Total Manufacturing
	let total_mfg = cm + mat_cost + proc_cost;
	frm.set_value('total_manufacturing_cost', total_mfg);
	
	// 5. Retail MRP
	let margin = (frm.doc.target_retail_margin || 0) / 100;
	if (margin >= 1) margin = 0.99; // Prevent division by zero/negative
	let retail = total_mfg / (1 - margin);
	frm.set_value('calculated_retail_mrp', retail);
}
			"""
		})
		doc.insert(ignore_permissions=True)
		print("Created Client Script: Garment Costing Sheet Math")
