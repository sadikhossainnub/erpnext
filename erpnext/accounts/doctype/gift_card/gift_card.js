// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gift Card", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Check Balance"), function () {
				frappe.msgprint(
					__("Current Balance: {0}", [format_currency(frm.doc.balance, frm.doc.currency)])
				);
			});
		}
	},
	amount(frm) {
		if (frm.is_new()) {
			frm.set_value("balance", frm.doc.amount);
		}
	},
});
