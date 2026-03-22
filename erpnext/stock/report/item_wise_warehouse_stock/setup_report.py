import sys
import frappe

def create_report():
	frappe.init(site="erpnext.localhost")
	frappe.connect()

	try:
		if not frappe.db.exists("Report", "Item Wise Warehouse Stock"):
			report = frappe.get_doc({
				"doctype": "Report",
				"report_name": "Item Wise Warehouse Stock",
				"ref_doctype": "Bin",
				"report_type": "Script Report",
				"is_standard": "Yes",
				"module": "Stock"
			})
			report.insert()
			frappe.db.commit()
			print("Report 'Item Wise Warehouse Stock' created successfully.")
		else:
			print("Report already exists.")
	except Exception as e:
		print(f"Error: {e}")
	finally:
		frappe.destroy()

if __name__ == "__main__":
	create_report()
