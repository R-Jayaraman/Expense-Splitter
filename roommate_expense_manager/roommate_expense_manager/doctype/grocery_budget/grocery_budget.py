import frappe
from frappe.model.document import Document
from frappe.utils import flt


class GroceryBudget(Document):

    def validate(self):

        self.validate_budget()
        self.apply_new_payments()
        self.calculate_totals()

    def on_update(self):

        self.send_payment_notifications()

    def validate_budget(self):

        if flt(self.budget_amount) <= 0:
            frappe.throw(
                "Budget Amount must be greater than zero"
            )

        active_members = frappe.get_all(
            "Room Member",
            filters={"active": 1}
        )

        if not active_members:
            frappe.throw(
                "No Active Members Found"
            )


    def apply_new_payments(self):
        for row in self.contributors:
            if flt(row.new_payment) <= 0:
                continue

            remaining = (
                flt(row.expected_amount)
                - flt(row.paid_amount)
            )

            if remaining <= 0:

                frappe.throw(
                    f"{row.member} has already paid the full amount."
                )

            if flt(row.new_payment) > remaining:

                frappe.throw(
                    f"{row.member} can pay only ₹{remaining:.2f}. "
                    f"Payment exceeds the expected amount."
                )

            row.paid_amount = (
                flt(row.paid_amount)
                + flt(row.new_payment)
            )

            row.new_payment = 0


    def calculate_totals(self):

        collected = 0

        for row in self.contributors:

            expected = flt(row.expected_amount)
            paid = flt(row.paid_amount)

            if paid > expected:
                frappe.throw(
                    f"{row.member} paid more than expected amount"
                )

            row.remaining_amount = round(
                expected - paid,
                2
            )

            collected += paid

            if paid == 0:
                row.status = "Pending"

            elif paid < expected:
                row.status = "Partial"

            else:
                row.status = "Paid"

        self.collected_amount = round(
            collected,
            2
        )

        self.pending_collection = round(
            flt(self.budget_amount)
            - self.collected_amount,
            2
        )

        if self.name:

            total_expense = frappe.db.sql(
                """
                SELECT COALESCE(
                    SUM(amount),
                    0
                )
                FROM `tabGrocery Expense`
                WHERE grocery_budget = %s
                AND docstatus != 2
                """,
                (self.name,)
            )[0][0]

        else:

            total_expense = 0

        self.total_expense = flt(
            total_expense
        )

        self.available = round(
            self.collected_amount
            - self.total_expense,
            2
        )

    def send_payment_notifications(self):

        for row in self.contributors:

            if row.status not in [
                "Partial",
                "Paid"
            ]:
                continue

            if row.last_email_status == row.status:
                continue

            member_email = frappe.db.get_value(
                "Room Member",
                row.member,
                "email"
            )

            if not member_email:
                continue

            if row.status == "Partial":

                subject = (
                    "Partial Grocery Contribution Received"
                )

                header_color = "#f59e0b"

                email_title = (
                    "Partial Grocery Payment Received"
                )

            else:

                subject = (
                    "Grocery Bill Paid Successfully"
                )

                header_color = "#16a34a"

                email_title = (
                    "Grocery Bill Paid Successfully"
                )

            message = f"""
            <div style="
                max-width:650px;
                margin:auto;
                background:#ffffff;
                font-family:Arial,sans-serif;
                border-radius:15px;
                overflow:hidden;
                border:1px solid #e5e7eb;
            ">

                <div style="
                    background:{header_color};
                    padding:30px;
                    text-align:center;
                ">
                    <h1 style="
                        color:white;
                        margin:0;
                        font-size:28px;
                    ">
                        {email_title}
                    </h1>

                    <p style="
                        color:white;
                        margin-top:10px;
                        font-size:15px;
                    ">
                        Grocery Contribution Update
                    </p>
                </div>

                <div style="
                    padding:30px;
                    background:white;
                    color:black;
                ">

                    <h2>Hello {row.member},</h2>

                    <p>
                        Your grocery contribution has been updated.
                    </p>

                    <table style="
                        width:100%;
                        border-collapse:collapse;
                        margin-top:25px;
                    ">

                        <tr>
                            <td style="
                                padding:15px;
                                border-bottom:1px solid #e5e7eb;
                            ">
                                🛒 Expected Amount
                            </td>

                            <td style="
                                text-align:right;
                                font-weight:bold;
                                border-bottom:1px solid #e5e7eb;
                            ">
                                ₹{flt(row.expected_amount):.2f}
                            </td>
                        </tr>

                        <tr>
                            <td style="
                                padding:15px;
                                border-bottom:1px solid #e5e7eb;
                            ">
                                💰 Paid Amount
                            </td>

                            <td style="
                                text-align:right;
                                font-weight:bold;
                                border-bottom:1px solid #e5e7eb;
                            ">
                                ₹{flt(row.paid_amount):.2f}
                            </td>
                        </tr>

                        <tr>
                            <td style="
                                padding:15px;
                                border-bottom:1px solid #e5e7eb;
                            ">
                                📌 Remaining Amount
                            </td>

                            <td style="
                                text-align:right;
                                font-weight:bold;
                                border-bottom:1px solid #e5e7eb;
                            ">
                                ₹{flt(row.remaining_amount):.2f}
                            </td>
                        </tr>

                    </table>

                    <div style="
                        margin-top:30px;
                        background:#f9fafb;
                        padding:20px;
                        border-radius:8px;
                    ">
                        <h2 style="
                            margin:0;
                            color:{header_color};
                        ">
                            Status : {row.status}
                        </h2>
                    </div>

                </div>

                <div style="
                    background:#111827;
                    color:white;
                    padding:20px;
                    text-align:center;
                ">
                    <strong>
                        Roommate Expense Manager
                    </strong>

                    <br><br>

                    Automated Payment Notification
                </div>

            </div>
            """

            frappe.sendmail(
                recipients=[member_email],
                subject=subject,
                message=message
            )
            row.last_email_status = row.status


@frappe.whitelist()
def get_active_members():

    return frappe.get_all(
        "Room Member",
        filters={
            "active": 1
        },
        fields=[
            "name"
        ]
    )

