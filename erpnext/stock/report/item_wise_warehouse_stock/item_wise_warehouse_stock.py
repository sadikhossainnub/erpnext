import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []

	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_columns():
	return [
		{
			"fieldname": "warehouse",
			"label": _("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 200
		},
		{
			"fieldname": "actual_qty",
			"label": _("Actual Qty"),
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "reserved_qty",
			"label": _("Reserved Qty"),
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "available_qty",
			"label": _("Available Qty"),
			"fieldtype": "Float",
			"width": 120
		}
	]

def get_data(filters):
	if not filters.get("item_code"):
		return []

	return frappe.db.sql("""
		SELECT
			warehouse,
			actual_qty,
			reserved_qty,
			(actual_qty - reserved_qty) as available_qty
		FROM
			`tabBin`
		WHERE
			item_code = %s
			AND actual_qty > 0
	""", filters.get("item_code"), as_dict=1)
