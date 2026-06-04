# Copyright (c) 2026, Ram and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ExpenseConfiguration(Document):
    def validate(self):
            self.actual_amount = (
				(self.room_rent or 0)
				+ (self.electricity or 0)
				+ (self.grocery or 0)
            )
