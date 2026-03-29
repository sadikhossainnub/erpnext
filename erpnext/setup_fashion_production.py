import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def setup_all():
	"""Fashion House Phase 3: Production Integration Setup"""
	frappe.flags.in_install = True

	# Phase 3A: Custom Fields & Child Tables
	create_size_breakdown_item()
	create_bom_custom_fields()
	create_work_order_custom_fields()
	create_job_card_custom_fields()

	# Phase 3B: Operations & Routing
	create_garment_operations()
	create_default_routing()

	# Phase 3C: Production Floor Tracking
	create_hourly_production_log()
	create_daily_production_summary()

	# Phase 3D: GCS → BOM Integration
	create_gcs_custom_fields()
	create_gcs_client_script()

	frappe.db.commit()
	print("=" * 60)
	print("Fashion House Phase 3: Production Integration Applied!")
	print("=" * 60)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 3A: Custom Fields & Child Tables
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def create_size_breakdown_item():
	"""Child table for size-wise quantity in Work Orders"""
	if frappe.db.exists("DocType", "Size Breakdown Item"):
		print("  ✓ Size Breakdown Item already exists")
		return

	doc = frappe.get_doc({
		"doctype": "DocType",
		"name": "Size Breakdown Item",
		"module": "Manufacturing",
		"custom": 1,
		"istable": 1,
		"fields": [
			{
				"fieldname": "size",
				"fieldtype": "Link",
				"label": "Size",
				"options": "Size Set",
				"reqd": 1,
				"in_list_view": 1,
				"columns": 2
			},
			{
				"fieldname": "quantity",
				"fieldtype": "Int",
				"label": "Quantity",
				"reqd": 1,
				"in_list_view": 1,
				"columns": 2
			},
			{
				"fieldname": "produced_qty",
				"fieldtype": "Int",
				"label": "Produced Qty",
				"read_only": 1,
				"in_list_view": 1,
				"columns": 2
			},
			{
				"fieldname": "rejected_qty",
				"fieldtype": "Int",
				"label": "Rejected Qty",
				"read_only": 1,
				"in_list_view": 1,
				"columns": 2
			},
			{
				"fieldname": "balance_qty",
				"fieldtype": "Int",
				"label": "Balance",
				"read_only": 1,
				"in_list_view": 1,
				"columns": 2
			}
		]
	})
	doc.insert(ignore_permissions=True)
	print("  ✓ Created: Size Breakdown Item (child table)")


def create_bom_custom_fields():
	"""Add garment-specific fields to BOM"""
	custom_fields = {
		"BOM": [
			# Fashion Section
			{
				"fieldname": "fashion_garment_section",
				"fieldtype": "Section Break",
				"label": "Garment Details",
				"insert_after": "project",
				"collapsible": 1
			},
			{
				"fieldname": "custom_style",
				"fieldtype": "Link",
				"label": "Style",
				"options": "Style Master",
				"insert_after": "fashion_garment_section"
			},
			{
				"fieldname": "custom_garment_costing_sheet",
				"fieldtype": "Link",
				"label": "Garment Costing Sheet",
				"options": "Garment Costing Sheet",
				"insert_after": "custom_style"
			},
			{
				"fieldname": "col_break_fashion_1",
				"fieldtype": "Column Break",
				"insert_after": "custom_garment_costing_sheet"
			},
			{
				"fieldname": "custom_sam",
				"fieldtype": "Float",
				"label": "SAM (Standard Allowed Minutes)",
				"insert_after": "col_break_fashion_1",
				"description": "Standard time to produce one piece"
			},
			{
				"fieldname": "custom_cm_cost",
				"fieldtype": "Currency",
				"label": "CM Cost (Cut & Make)",
				"insert_after": "custom_sam",
				"read_only": 1,
				"description": "Fetched from Garment Costing Sheet"
			},
			{
				"fieldname": "custom_garment_type",
				"fieldtype": "Data",
				"label": "Garment Type",
				"insert_after": "custom_cm_cost",
				"fetch_from": "custom_style.garment_type",
				"read_only": 1
			},
		]
	}
	create_custom_fields(custom_fields)
	print("  ✓ Created: BOM custom fields (Style, GCS, SAM, CM Cost)")


def create_work_order_custom_fields():
	"""Add garment-specific fields to Work Order"""
	custom_fields = {
		"Work Order": [
			# Fashion Section
			{
				"fieldname": "fashion_production_section",
				"fieldtype": "Section Break",
				"label": "Garment Production Details",
				"insert_after": "project",
				"collapsible": 0
			},
			{
				"fieldname": "custom_style",
				"fieldtype": "Link",
				"label": "Style",
				"options": "Style Master",
				"insert_after": "fashion_production_section",
				"fetch_from": "bom_no.custom_style"
			},
			{
				"fieldname": "custom_garment_type",
				"fieldtype": "Data",
				"label": "Garment Type",
				"insert_after": "custom_style",
				"fetch_from": "custom_style.garment_type",
				"read_only": 1
			},
			{
				"fieldname": "custom_color",
				"fieldtype": "Link",
				"label": "Color",
				"options": "Color Master",
				"insert_after": "custom_garment_type"
			},
			{
				"fieldname": "col_break_fashion_wo_1",
				"fieldtype": "Column Break",
				"insert_after": "custom_color"
			},
			{
				"fieldname": "custom_season",
				"fieldtype": "Data",
				"label": "Season",
				"insert_after": "col_break_fashion_wo_1",
				"fetch_from": "custom_style.season",
				"read_only": 1
			},
			{
				"fieldname": "custom_factory_line",
				"fieldtype": "Data",
				"label": "Sewing Line",
				"insert_after": "custom_season",
				"description": "Production floor line assignment"
			},
			{
				"fieldname": "custom_embellishment_type",
				"fieldtype": "Select",
				"label": "Embellishment Type",
				"insert_after": "custom_factory_line",
				"options": "\nNone\nEmbroidery\nScreen Print\nBlock Print\nHand Work\nWash/Dye\nEmbroidery + Print\nEmbroidery + Wash\nPrint + Wash\nAll"
			},
			{
				"fieldname": "custom_sam",
				"fieldtype": "Float",
				"label": "SAM",
				"insert_after": "custom_embellishment_type",
				"fetch_from": "bom_no.custom_sam",
				"read_only": 1
			},
			# Size Breakdown Section
			{
				"fieldname": "size_breakdown_section",
				"fieldtype": "Section Break",
				"label": "Size-wise Breakdown",
				"insert_after": "custom_sam",
				"collapsible": 1
			},
			{
				"fieldname": "custom_size_breakdown",
				"fieldtype": "Table",
				"label": "Size Breakdown",
				"options": "Size Breakdown Item",
				"insert_after": "size_breakdown_section"
			},
			{
				"fieldname": "custom_total_order_pcs",
				"fieldtype": "Int",
				"label": "Total Order Pieces",
				"insert_after": "custom_size_breakdown",
				"read_only": 1,
				"description": "Sum of all sizes"
			},
		]
	}
	create_custom_fields(custom_fields)
	print("  ✓ Created: Work Order custom fields (Style, Color, Size, Line)")


def create_job_card_custom_fields():
	"""Add garment-specific fields to Job Card"""
	custom_fields = {
		"Job Card": [
			# Fashion Section
			{
				"fieldname": "fashion_jc_section",
				"fieldtype": "Section Break",
				"label": "Garment Tracking",
				"insert_after": "project",
				"collapsible": 0
			},
			{
				"fieldname": "custom_style",
				"fieldtype": "Link",
				"label": "Style",
				"options": "Style Master",
				"insert_after": "fashion_jc_section",
				"fetch_from": "work_order.custom_style",
				"read_only": 1
			},
			{
				"fieldname": "custom_color",
				"fieldtype": "Link",
				"label": "Color",
				"options": "Color Master",
				"insert_after": "custom_style",
				"fetch_from": "work_order.custom_color",
				"read_only": 1
			},
			{
				"fieldname": "custom_garment_type",
				"fieldtype": "Data",
				"label": "Garment Type",
				"insert_after": "custom_color",
				"fetch_from": "custom_style.garment_type",
				"read_only": 1
			},
			{
				"fieldname": "col_break_fashion_jc_1",
				"fieldtype": "Column Break",
				"insert_after": "custom_garment_type"
			},
			{
				"fieldname": "custom_line_no",
				"fieldtype": "Data",
				"label": "Sewing Line",
				"insert_after": "col_break_fashion_jc_1",
				"fetch_from": "work_order.custom_factory_line"
			},
			{
				"fieldname": "custom_target_pcs",
				"fieldtype": "Int",
				"label": "Target Pieces (Shift)",
				"insert_after": "custom_line_no",
				"description": "Production target for this shift"
			},
			{
				"fieldname": "custom_achieved_pcs",
				"fieldtype": "Int",
				"label": "Achieved Pieces",
				"insert_after": "custom_target_pcs",
				"read_only": 1,
				"description": "Auto-calculated from Hourly Logs"
			},
			{
				"fieldname": "custom_rejected_pcs",
				"fieldtype": "Int",
				"label": "Rejected Pieces",
				"insert_after": "custom_achieved_pcs",
				"read_only": 1
			},
			{
				"fieldname": "custom_dhu",
				"fieldtype": "Float",
				"label": "DHÜ (Defects per 100 Units)",
				"insert_after": "custom_rejected_pcs",
				"read_only": 1,
				"precision": 2,
				"description": "(Rejected / Achieved) × 100"
			},
		]
	}
	create_custom_fields(custom_fields)
	print("  ✓ Created: Job Card custom fields (Style, Color, Line, DHÜ)")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 3B: Garment Operations & Routing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


GARMENT_OPERATIONS = [
	{
		"name": "Fabric Inspection & Cutting",
		"description": "Inspect incoming fabric for defects, lay and cut patterns using markers",
		"workstation": None,
		"batch_size": 0,
		"sub_operations": []
	},
	{
		"name": "Embroidery",
		"description": "Machine or hand embroidery work on garment panels",
		"workstation": None,
		"batch_size": 0,
		"is_corrective_operation": 0,
		"sub_operations": [
			{"operation": "Karchupi Work", "time_in_mins": 30},
			{"operation": "Zari / Zardozi Work", "time_in_mins": 45},
			{"operation": "Thread Embroidery", "time_in_mins": 20},
			{"operation": "Sequence / Bead Work", "time_in_mins": 25},
		]
	},
	{
		"name": "Screen Print / Block Print",
		"description": "Screen printing, block printing, or digital printing on fabric/garment",
		"workstation": None,
		"batch_size": 0,
		"sub_operations": [
			{"operation": "Placement Print", "time_in_mins": 10},
			{"operation": "All Over Print", "time_in_mins": 15},
			{"operation": "Discharge Print", "time_in_mins": 12},
		]
	},
	{
		"name": "Sewing / Stitching",
		"description": "Main sewing operation - assembly of cut panels into finished garment",
		"workstation": None,
		"batch_size": 0,
		"sub_operations": [
			{"operation": "Front Panel Assembly", "time_in_mins": 8},
			{"operation": "Back Panel Assembly", "time_in_mins": 6},
			{"operation": "Side Seam & Shoulder Attach", "time_in_mins": 5},
			{"operation": "Collar / Neck Finish", "time_in_mins": 7},
			{"operation": "Sleeve Attach", "time_in_mins": 5},
			{"operation": "Hem & Bottom Finish", "time_in_mins": 4},
			{"operation": "Button / Zip Attach", "time_in_mins": 3},
		]
	},
	{
		"name": "Washing / Dyeing",
		"description": "Garment wash, enzyme wash, stone wash, or dyeing process",
		"workstation": None,
		"batch_size": 0,
		"sub_operations": []
	},
	{
		"name": "Quality Check & Trimming",
		"description": "Inline and endline quality inspection, thread trimming, defect marking",
		"workstation": None,
		"batch_size": 0,
		"is_corrective_operation": 0,
		"quality_inspection_template": None,
		"sub_operations": []
	},
	{
		"name": "Ironing & Finishing",
		"description": "Steam press, ironing, and final finishing touches",
		"workstation": None,
		"batch_size": 0,
		"sub_operations": []
	},
	{
		"name": "Packing & Tagging",
		"description": "Price tagging, poly packing, carton packing, and dispatch preparation",
		"workstation": None,
		"batch_size": 0,
		"sub_operations": []
	},
]

# Default time in minutes for each operation in the routing
ROUTING_OPERATIONS = [
	{"operation": "Fabric Inspection & Cutting", "time_in_mins": 5, "sequence_id": 1},
	{"operation": "Embroidery", "time_in_mins": 30, "sequence_id": 2},
	{"operation": "Screen Print / Block Print", "time_in_mins": 15, "sequence_id": 2},  # Parallel with embroidery
	{"operation": "Sewing / Stitching", "time_in_mins": 25, "sequence_id": 3},
	{"operation": "Washing / Dyeing", "time_in_mins": 20, "sequence_id": 4},
	{"operation": "Quality Check & Trimming", "time_in_mins": 5, "sequence_id": 5},
	{"operation": "Ironing & Finishing", "time_in_mins": 3, "sequence_id": 6},
	{"operation": "Packing & Tagging", "time_in_mins": 2, "sequence_id": 7},
]


def create_garment_operations():
	"""Create standard garment manufacturing operations with sub-operations"""
	# First create all sub-operations as standalone Operations
	all_sub_ops = set()
	for op_data in GARMENT_OPERATIONS:
		for sub_op in op_data.get("sub_operations", []):
			all_sub_ops.add(sub_op["operation"])

	for sub_op_name in all_sub_ops:
		if not frappe.db.exists("Operation", sub_op_name):
			doc = frappe.get_doc({
				"doctype": "Operation",
				"name": sub_op_name,
				"description": sub_op_name,
			})
			doc.insert(ignore_permissions=True)
			print(f"    → Sub-operation: {sub_op_name}")

	# Now create main operations with sub-op references
	for op_data in GARMENT_OPERATIONS:
		if frappe.db.exists("Operation", op_data["name"]):
			print(f"  ✓ Operation already exists: {op_data['name']}")
			continue

		doc = frappe.get_doc({
			"doctype": "Operation",
			"name": op_data["name"],
			"description": op_data["description"],
			"batch_size": op_data.get("batch_size", 0),
			"is_corrective_operation": op_data.get("is_corrective_operation", 0),
		})

		for sub_op in op_data.get("sub_operations", []):
			doc.append("sub_operations", {
				"operation": sub_op["operation"],
				"time_in_mins": sub_op["time_in_mins"],
			})

		doc.insert(ignore_permissions=True)
		print(f"  ✓ Created Operation: {op_data['name']} ({len(op_data.get('sub_operations', []))} sub-ops)")

	print("  ✓ All garment operations created")


def create_default_routing():
	"""Create the default garment production routing"""
	routing_name = "Standard Garment Production"

	if frappe.db.exists("Routing", routing_name):
		print(f"  ✓ Routing already exists: {routing_name}")
		return

	doc = frappe.get_doc({
		"doctype": "Routing",
		"routing_name": routing_name,
		"name": routing_name,
	})

	for idx, op in enumerate(ROUTING_OPERATIONS, 1):
		doc.append("operations", {
			"operation": op["operation"],
			"time_in_mins": op["time_in_mins"],
			"sequence_id": op["sequence_id"],
			"idx": idx,
		})

	doc.insert(ignore_permissions=True)
	print(f"  ✓ Created Routing: {routing_name} ({len(ROUTING_OPERATIONS)} operations)")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 3C: Production Floor Tracking
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def create_hourly_production_log():
	"""Track hourly production output per sewing line"""
	if frappe.db.exists("DocType", "Hourly Production Log"):
		print("  ✓ Hourly Production Log already exists")
		return

	doc = frappe.get_doc({
		"doctype": "DocType",
		"name": "Hourly Production Log",
		"module": "Manufacturing",
		"custom": 1,
		"autoname": "format:HPL-{YYYY}-{MM}-{DD}-{#####}",
		"title_field": "style",
		"search_fields": "work_order, style, line_no, date",
		"sort_field": "date",
		"sort_order": "DESC",
		"fields": [
			# Header
			{
				"fieldname": "date",
				"fieldtype": "Date",
				"label": "Date",
				"reqd": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"default": "Today",
				"columns": 1
			},
			{
				"fieldname": "hour_slot",
				"fieldtype": "Select",
				"label": "Hour Slot",
				"options": "\n8:00 - 9:00\n9:00 - 10:00\n10:00 - 11:00\n11:00 - 12:00\n12:00 - 1:00\n1:00 - 2:00\n2:00 - 3:00\n3:00 - 4:00\n4:00 - 5:00\n5:00 - 6:00\n6:00 - 7:00\n7:00 - 8:00\nOvertime",
				"reqd": 1,
				"in_list_view": 1,
				"columns": 2
			},
			{
				"fieldname": "work_order",
				"fieldtype": "Link",
				"label": "Work Order",
				"options": "Work Order",
				"reqd": 1,
				"in_standard_filter": 1
			},
			{
				"fieldname": "job_card",
				"fieldtype": "Link",
				"label": "Job Card",
				"options": "Job Card",
			},
			# Style & Line Info
			{
				"fieldname": "sb_line_info",
				"fieldtype": "Section Break",
				"label": "Line Details"
			},
			{
				"fieldname": "style",
				"fieldtype": "Link",
				"label": "Style",
				"options": "Style Master",
				"fetch_from": "work_order.custom_style",
				"read_only": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"columns": 2
			},
			{
				"fieldname": "color",
				"fieldtype": "Link",
				"label": "Color",
				"options": "Color Master",
				"fetch_from": "work_order.custom_color",
				"read_only": 1,
			},
			{
				"fieldname": "line_no",
				"fieldtype": "Data",
				"label": "Sewing Line",
				"reqd": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"columns": 1
			},
			{
				"fieldname": "cb_line_1",
				"fieldtype": "Column Break",
			},
			{
				"fieldname": "operator",
				"fieldtype": "Link",
				"label": "Line Supervisor",
				"options": "Employee"
			},
			{
				"fieldname": "operation",
				"fieldtype": "Link",
				"label": "Operation",
				"options": "Operation",
				"in_standard_filter": 1,
				"description": "Sewing / Cutting / Embroidery etc."
			},
			{
				"fieldname": "garment_type",
				"fieldtype": "Data",
				"label": "Garment Type",
				"fetch_from": "style.garment_type",
				"read_only": 1
			},
			# Production Numbers
			{
				"fieldname": "sb_production",
				"fieldtype": "Section Break",
				"label": "Production Output"
			},
			{
				"fieldname": "target_pcs",
				"fieldtype": "Int",
				"label": "Target (pcs)",
				"reqd": 1,
				"in_list_view": 1,
				"columns": 1
			},
			{
				"fieldname": "produced_pcs",
				"fieldtype": "Int",
				"label": "Produced (pcs)",
				"reqd": 1,
				"in_list_view": 1,
				"columns": 1
			},
			{
				"fieldname": "rejected_pcs",
				"fieldtype": "Int",
				"label": "Rejected (pcs)",
				"default": "0",
				"in_list_view": 1,
				"columns": 1
			},
			{
				"fieldname": "cb_prod_1",
				"fieldtype": "Column Break",
			},
			{
				"fieldname": "good_pcs",
				"fieldtype": "Int",
				"label": "Good Output (pcs)",
				"read_only": 1,
				"description": "Produced - Rejected"
			},
			{
				"fieldname": "efficiency_percent",
				"fieldtype": "Percent",
				"label": "Efficiency %",
				"read_only": 1,
				"in_list_view": 1,
				"columns": 1,
				"description": "(Produced / Target) × 100"
			},
			{
				"fieldname": "dhu",
				"fieldtype": "Float",
				"label": "DHÜ",
				"read_only": 1,
				"precision": 2,
				"description": "(Rejected / Produced) × 100"
			},
			# Remarks
			{
				"fieldname": "sb_remarks",
				"fieldtype": "Section Break",
				"label": "Remarks",
				"collapsible": 1
			},
			{
				"fieldname": "defect_type",
				"fieldtype": "Select",
				"label": "Main Defect Type",
				"options": "\nNone\nBroken Stitch\nSkip Stitch\nOpen Seam\nUneven Seam\nFabric Defect\nColor Shade Issue\nEmbroidery Defect\nPrint Misalignment\nIron Mark\nStain\nMeasurement Issue\nOther"
			},
			{
				"fieldname": "remarks",
				"fieldtype": "Small Text",
				"label": "Remarks"
			},
		],
		"permissions": [
			{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
			{"role": "Manufacturing Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
			{"role": "Manufacturing User", "read": 1, "write": 1, "create": 1},
		]
	})
	doc.insert(ignore_permissions=True)
	print("  ✓ Created: Hourly Production Log")

	# Create Client Script for auto-calculations
	if not frappe.db.exists("Client Script", "Hourly Production Log Calc"):
		cs = frappe.get_doc({
			"doctype": "Client Script",
			"dt": "Hourly Production Log",
			"name": "Hourly Production Log Calc",
			"module": "Manufacturing",
			"script": """
frappe.ui.form.on('Hourly Production Log', {
	produced_pcs: function(frm) { calc_hpl(frm); },
	target_pcs: function(frm) { calc_hpl(frm); },
	rejected_pcs: function(frm) { calc_hpl(frm); }
});

function calc_hpl(frm) {
	let produced = frm.doc.produced_pcs || 0;
	let target = frm.doc.target_pcs || 0;
	let rejected = frm.doc.rejected_pcs || 0;

	frm.set_value('good_pcs', produced - rejected);

	if (target > 0) {
		frm.set_value('efficiency_percent', ((produced / target) * 100).toFixed(2));
	} else {
		frm.set_value('efficiency_percent', 0);
	}

	if (produced > 0) {
		frm.set_value('dhu', ((rejected / produced) * 100).toFixed(2));
	} else {
		frm.set_value('dhu', 0);
	}
}
			"""
		})
		cs.insert(ignore_permissions=True)
		print("  ✓ Created: Hourly Production Log Client Script")


def create_daily_production_summary():
	"""Aggregated daily production view"""
	if frappe.db.exists("DocType", "Daily Production Summary"):
		print("  ✓ Daily Production Summary already exists")
		return

	doc = frappe.get_doc({
		"doctype": "DocType",
		"name": "Daily Production Summary",
		"module": "Manufacturing",
		"custom": 1,
		"autoname": "format:DPS-{YYYY}-{MM}-{DD}-{#####}",
		"title_field": "style",
		"search_fields": "work_order, style, line_no, date",
		"sort_field": "date",
		"sort_order": "DESC",
		"fields": [
			# Header
			{
				"fieldname": "date",
				"fieldtype": "Date",
				"label": "Date",
				"reqd": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"default": "Today"
			},
			{
				"fieldname": "work_order",
				"fieldtype": "Link",
				"label": "Work Order",
				"options": "Work Order",
				"reqd": 1,
				"in_standard_filter": 1
			},
			{
				"fieldname": "style",
				"fieldtype": "Link",
				"label": "Style",
				"options": "Style Master",
				"fetch_from": "work_order.custom_style",
				"read_only": 1,
				"in_list_view": 1,
				"in_standard_filter": 1
			},
			{
				"fieldname": "color",
				"fieldtype": "Link",
				"label": "Color",
				"options": "Color Master",
				"fetch_from": "work_order.custom_color",
				"read_only": 1
			},
			{
				"fieldname": "line_no",
				"fieldtype": "Data",
				"label": "Sewing Line",
				"reqd": 1,
				"in_list_view": 1,
				"in_standard_filter": 1
			},
			# Summary Numbers
			{
				"fieldname": "sb_summary",
				"fieldtype": "Section Break",
				"label": "Day Summary"
			},
			{
				"fieldname": "total_target",
				"fieldtype": "Int",
				"label": "Total Target",
				"read_only": 1,
				"in_list_view": 1
			},
			{
				"fieldname": "total_produced",
				"fieldtype": "Int",
				"label": "Total Produced",
				"read_only": 1,
				"in_list_view": 1
			},
			{
				"fieldname": "total_good",
				"fieldtype": "Int",
				"label": "Total Good",
				"read_only": 1
			},
			{
				"fieldname": "cb_sum_1",
				"fieldtype": "Column Break",
			},
			{
				"fieldname": "total_rejected",
				"fieldtype": "Int",
				"label": "Total Rejected",
				"read_only": 1,
				"in_list_view": 1
			},
			{
				"fieldname": "overall_efficiency",
				"fieldtype": "Percent",
				"label": "Overall Efficiency %",
				"read_only": 1,
				"in_list_view": 1
			},
			{
				"fieldname": "dhu",
				"fieldtype": "Float",
				"label": "DHÜ",
				"read_only": 1,
				"precision": 2
			},
			# Hourly breakdown reference
			{
				"fieldname": "sb_hourly",
				"fieldtype": "Section Break",
				"label": "Actions",
				"collapsible": 1
			},
			{
				"fieldname": "aggregate_button_html",
				"fieldtype": "HTML",
				"label": "",
				"options": "<button class='btn btn-xs btn-primary' onclick=\"cur_frm.call('aggregate_from_hourly_logs')\">📊 Aggregate from Hourly Logs</button>"
			},
			{
				"fieldname": "sam",
				"fieldtype": "Float",
				"label": "SAM (Ref)",
				"fetch_from": "work_order.custom_sam",
				"read_only": 1
			},
			{
				"fieldname": "actual_minutes_per_pc",
				"fieldtype": "Float",
				"label": "Actual Minutes/Piece",
				"read_only": 1,
				"precision": 2,
				"description": "Available minutes / Total produced"
			},
		],
		"permissions": [
			{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
			{"role": "Manufacturing Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
			{"role": "Manufacturing User", "read": 1, "write": 1, "create": 1},
		]
	})
	doc.insert(ignore_permissions=True)
	print("  ✓ Created: Daily Production Summary")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 3D: GCS → BOM Integration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def create_gcs_custom_fields():
	"""Add BOM reference and Create BOM button to Garment Costing Sheet"""
	custom_fields = {
		"Garment Costing Sheet": [
			{
				"fieldname": "custom_linked_bom",
				"fieldtype": "Link",
				"label": "Linked BOM",
				"options": "BOM",
				"insert_after": "calculated_retail_mrp",
				"read_only": 1,
				"description": "Auto-generated BOM from this costing sheet"
			},
			{
				"fieldname": "custom_bom_status",
				"fieldtype": "Select",
				"label": "BOM Status",
				"options": "\nNot Created\nDraft\nSubmitted",
				"insert_after": "custom_linked_bom",
				"read_only": 1,
				"default": "Not Created"
			},
		]
	}
	create_custom_fields(custom_fields)
	print("  ✓ Created: Garment Costing Sheet custom fields (BOM link)")


def create_gcs_client_script():
	"""Add Create BOM button to Garment Costing Sheet"""
	script_name = "GCS Create BOM Button"
	if frappe.db.exists("Client Script", script_name):
		print(f"  ✓ Client Script already exists: {script_name}")
		return

	cs = frappe.get_doc({
		"doctype": "Client Script",
		"dt": "Garment Costing Sheet",
		"name": script_name,
		"module": "Manufacturing",
		"script": """
frappe.ui.form.on('Garment Costing Sheet', {
	refresh: function(frm) {
		if (frm.doc.style && frm.doc.total_manufacturing_cost > 0) {
			if (!frm.doc.custom_linked_bom || frm.doc.custom_bom_status === 'Not Created') {
				frm.add_custom_button(__('Create BOM'), function() {
					create_bom_from_gcs(frm);
				}, __('Actions'));
			} else {
				frm.add_custom_button(__('View BOM'), function() {
					frappe.set_route('Form', 'BOM', frm.doc.custom_linked_bom);
				}, __('Actions'));
			}
		}

		// Add button for Work Order creation shortcut
		if (frm.doc.custom_linked_bom && frm.doc.custom_bom_status === 'Submitted') {
			frm.add_custom_button(__('Create Work Order'), function() {
				frappe.new_doc('Work Order', {
					'production_item': get_item_from_style(frm),
					'bom_no': frm.doc.custom_linked_bom,
				});
			}, __('Actions'));
		}
	}
});

function create_bom_from_gcs(frm) {
	frappe.call({
		method: 'erpnext.setup_fashion_production.create_bom_from_garment_costing_sheet',
		args: { gcs_name: frm.doc.name },
		freeze: true,
		freeze_message: __('Creating BOM from Costing Sheet...'),
		callback: function(r) {
			if (r.message) {
				frm.reload_doc();
				frappe.show_alert({
					message: __('BOM {0} created successfully!', [r.message]),
					indicator: 'green'
				});
			}
		}
	});
}

function get_item_from_style(frm) {
	// Return the item linked to this style (if exists)
	return '';
}
		"""
	})
	cs.insert(ignore_permissions=True)
	print("  ✓ Created: GCS Create BOM Button client script")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WHITELISTED API METHODS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@frappe.whitelist()
def create_bom_from_garment_costing_sheet(gcs_name):
	"""Server method: Create a BOM from a Garment Costing Sheet"""
	gcs = frappe.get_doc("Garment Costing Sheet", gcs_name)

	if not gcs.style:
		frappe.throw("Please set a Style in the Garment Costing Sheet first.")

	# Get the item linked to style (first Item matching this style)
	item_code = frappe.db.get_value("Item", {"custom_style": gcs.style}, "name")

	if not item_code:
		frappe.throw(
			f"No Item found with Style '{gcs.style}'. "
			f"Please create an Item first and set the Style field to '{gcs.style}'."
		)

	# Check if BOM already exists for this GCS
	existing_bom = frappe.db.get_value(
		"BOM",
		{"custom_garment_costing_sheet": gcs_name, "docstatus": ["!=", 2]},
		"name"
	)
	if existing_bom:
		frappe.throw(f"BOM {existing_bom} already exists for this Costing Sheet.")

	# Create BOM
	bom = frappe.new_doc("BOM")
	bom.item = item_code
	bom.quantity = 1
	bom.company = frappe.defaults.get_user_default("Company")

	# Set garment custom fields
	bom.custom_style = gcs.style
	bom.custom_garment_costing_sheet = gcs_name
	bom.custom_sam = gcs.sam or 0
	bom.custom_cm_cost = gcs.cm_cost or 0

	# Use FG-based operating cost (CM cost)
	bom.fg_based_operating_cost = 1
	bom.operating_cost_per_bom_quantity = gcs.cm_cost or 0

	# Add Fabric Items as raw materials
	for fabric in gcs.get("fabric_items", []):
		if fabric.item:
			w_factor = 1 + ((fabric.wastage_percent or 0) / 100)
			stock_qty = (fabric.consumption or 0) * w_factor
			bom.append("items", {
				"item_code": fabric.item,
				"qty": stock_qty,
				"rate": fabric.rate or 0,
			})

	# Add Trim Items as raw materials
	for trim in gcs.get("trim_items", []):
		if trim.item:
			bom.append("items", {
				"item_code": trim.item,
				"qty": trim.quantity or 0,
				"rate": trim.rate or 0,
			})

	# Set routing if available
	if frappe.db.exists("Routing", "Standard Garment Production"):
		bom.routing = "Standard Garment Production"
		bom.with_operations = 1
		bom.transfer_material_against = "Work Order"

	bom.insert(ignore_permissions=True)

	# Update GCS with BOM reference
	frappe.db.set_value("Garment Costing Sheet", gcs_name, {
		"custom_linked_bom": bom.name,
		"custom_bom_status": "Draft"
	})

	frappe.msgprint(
		f"BOM <b>{bom.name}</b> created as Draft. Review and Submit it to start production.",
		title="BOM Created",
		indicator="green"
	)

	return bom.name


@frappe.whitelist()
def aggregate_daily_production(daily_summary_name):
	"""Aggregate hourly logs into a Daily Production Summary"""
	dps = frappe.get_doc("Daily Production Summary", daily_summary_name)

	logs = frappe.get_all(
		"Hourly Production Log",
		filters={
			"date": dps.date,
			"work_order": dps.work_order,
			"line_no": dps.line_no,
		},
		fields=["target_pcs", "produced_pcs", "rejected_pcs"]
	)

	if not logs:
		frappe.throw("No Hourly Production Logs found for this date, work order, and line.")

	total_target = sum(l.target_pcs or 0 for l in logs)
	total_produced = sum(l.produced_pcs or 0 for l in logs)
	total_rejected = sum(l.rejected_pcs or 0 for l in logs)

	dps.total_target = total_target
	dps.total_produced = total_produced
	dps.total_good = total_produced - total_rejected
	dps.total_rejected = total_rejected
	dps.overall_efficiency = (total_produced / total_target * 100) if total_target > 0 else 0
	dps.dhu = (total_rejected / total_produced * 100) if total_produced > 0 else 0

	# Calculate actual minutes per piece (assumes 8-hour shift, adjustable)
	working_minutes = len(logs) * 60  # each log = 1 hour = 60 minutes
	dps.actual_minutes_per_pc = (working_minutes / total_produced) if total_produced > 0 else 0

	dps.save(ignore_permissions=True)
	frappe.msgprint(
		f"Aggregated {len(logs)} hourly logs. Efficiency: {dps.overall_efficiency:.1f}%",
		indicator="green"
	)
	return dps.name


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Work Order Size Breakdown Client Script
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def create_wo_size_breakdown_script():
	"""Client script for auto-summing size breakdown in Work Order"""
	script_name = "WO Size Breakdown Sum"
	if frappe.db.exists("Client Script", script_name):
		return

	cs = frappe.get_doc({
		"doctype": "Client Script",
		"dt": "Work Order",
		"name": script_name,
		"module": "Manufacturing",
		"script": """
frappe.ui.form.on('Size Breakdown Item', {
	quantity: function(frm) {
		calc_total_pcs(frm);
	},
	custom_size_breakdown_remove: function(frm) {
		calc_total_pcs(frm);
	}
});

function calc_total_pcs(frm) {
	let total = 0;
	(frm.doc.custom_size_breakdown || []).forEach(function(row) {
		total += (row.quantity || 0);
	});
	frm.set_value('custom_total_order_pcs', total);
}
		"""
	})
	cs.insert(ignore_permissions=True)
	print("  ✓ Created: WO Size Breakdown Sum client script")
