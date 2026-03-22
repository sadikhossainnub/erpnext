# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import random
import string

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class GiftCard(Document):
	def validate(self):
		if self.amount <= 0:
			frappe.throw(_("Gift Card amount must be greater than zero."))

		if self.is_new():
			self.balance = self.amount

		if self.balance < 0:
			frappe.throw(_("Gift Card balance cannot be negative."))

		if self.expiry_date and getdate(self.expiry_date) < getdate(nowdate()):
			if self.is_new():
				frappe.throw(_("Expiry date cannot be in the past."))


@frappe.whitelist()
def validate_gift_card(code):
	"""Validate a gift card code and return its details."""
	if not frappe.db.exists("Gift Card", code):
		frappe.throw(_("Gift Card {0} does not exist.").format(code))

	gift_card = frappe.get_doc("Gift Card", code)

	if not gift_card.is_active:
		frappe.throw(_("Gift Card {0} is not active.").format(code))

	if gift_card.expiry_date and getdate(gift_card.expiry_date) < getdate(nowdate()):
		frappe.throw(_("Gift Card {0} has expired.").format(code))

	if gift_card.balance <= 0:
		frappe.throw(_("Gift Card {0} has no remaining balance.").format(code))

	return {
		"gift_card_code": gift_card.gift_card_code,
		"amount": gift_card.amount,
		"balance": gift_card.balance,
		"customer": gift_card.customer,
		"expiry_date": gift_card.expiry_date,
		"is_active": gift_card.is_active,
	}


@frappe.whitelist()
def redeem_gift_card(code, amount, invoice_name=None):
	"""Deduct amount from gift card balance."""
	amount = float(amount)

	if amount <= 0:
		frappe.throw(_("Redemption amount must be greater than zero."))

	gift_card = frappe.get_doc("Gift Card", code)

	if not gift_card.is_active:
		frappe.throw(_("Gift Card {0} is not active.").format(code))

	if gift_card.expiry_date and getdate(gift_card.expiry_date) < getdate(nowdate()):
		frappe.throw(_("Gift Card {0} has expired.").format(code))

	if amount > gift_card.balance:
		frappe.throw(
			_("Redemption amount {0} exceeds the gift card balance {1}.").format(
				frappe.format_value(amount, {"fieldtype": "Currency"}),
				frappe.format_value(gift_card.balance, {"fieldtype": "Currency"}),
			)
		)

	gift_card.balance -= amount
	gift_card.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"gift_card_code": gift_card.gift_card_code,
		"new_balance": gift_card.balance,
		"redeemed_amount": amount,
	}


@frappe.whitelist()
def restore_gift_card_balance(code, amount):
	"""Restore balance to gift card (used on invoice cancellation)."""
	amount = float(amount)

	if amount <= 0:
		return

	gift_card = frappe.get_doc("Gift Card", code)
	gift_card.balance += amount

	if gift_card.balance > gift_card.amount:
		gift_card.balance = gift_card.amount

	gift_card.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"gift_card_code": gift_card.gift_card_code,
		"new_balance": gift_card.balance,
	}


@frappe.whitelist()
def create_gift_card(amount, customer=None, expiry_date=None):
	"""Create a new gift card with a random code."""
	amount = float(amount)

	if amount <= 0:
		frappe.throw(_("Gift Card amount must be greater than zero."))

	code = generate_gift_card_code()

	gift_card = frappe.get_doc(
		{
			"doctype": "Gift Card",
			"gift_card_code": code,
			"amount": amount,
			"balance": amount,
			"customer": customer,
			"expiry_date": expiry_date,
			"is_active": 1,
		}
	)
	gift_card.insert(ignore_permissions=True)
	frappe.db.commit()

	return {
		"gift_card_code": gift_card.gift_card_code,
		"amount": gift_card.amount,
		"balance": gift_card.balance,
	}


def generate_gift_card_code(length=12):
	"""Generate a unique gift card code."""
	while True:
		code = "GC-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
		if not frappe.db.exists("Gift Card", code):
			return code
