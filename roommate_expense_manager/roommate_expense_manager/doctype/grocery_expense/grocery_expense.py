import frappe
from frappe.model.document import Document
from frappe.utils import flt


class GroceryExpense(Document):

    def validate(self):

        self.validate_amount()
        self.validate_budget_balance()

    def validate_amount(self):

        if flt(self.amount) <= 0:
            frappe.throw(
                "Expense Amount must be greater than zero"
            )

    def validate_budget_balance(self):

        if not self.grocery_budget:
            frappe.throw(
                "Grocery Budget is required"
            )

        budget = frappe.get_doc(
            "Grocery Budget",
            self.grocery_budget
        )

        if flt(self.amount) > flt(budget.available):

            frappe.throw(
                f"""
                Expense Amount ({self.amount})
                cannot exceed Available Balance ({budget.available})
                """
            )

    def on_submit(self):
        self.update_budget()

    def on_cancel(self):
        self.update_budget()

    def update_budget(self):

        budget = frappe.get_doc(
            "Grocery Budget",
            self.grocery_budget
        )

        budget.calculate_totals()

        budget.save(
            ignore_permissions=True
        )