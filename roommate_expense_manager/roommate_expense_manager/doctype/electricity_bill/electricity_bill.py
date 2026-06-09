import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ElectricityBill(Document):

    def validate(self):

        self.validate_month()
        self.validate_amount()
        self.validate_members()

        self.calculate_status()
        self.calculate_totals()

    def on_update(self):

        self.send_payment_notifications()

    def validate_month(self):

        if not self.bill_month:

            frappe.throw(
                "Bill Month is required"
            )

    def validate_amount(self):

        if flt(self.total_amount) <= 0:

            frappe.throw(
                "Total Amount must be greater than zero"
            )

    def validate_members(self):

        if not self.electricity_split:

            frappe.throw(
                "Electricity Split cannot be empty"
            )

        members = []

        for row in self.electricity_split:

            if not row.member:

                frappe.throw(
                    f"Row {row.idx}: Member is required"
                )

            if row.member in members:

                frappe.throw(
                    f"Duplicate Member: {row.member}"
                )

            if flt(row.paid_amount) < 0:

                frappe.throw(
                    f"{row.member}: Paid Amount cannot be negative"
                )

            if flt(row.paid_amount) > flt(row.bill_amount):

                frappe.throw(
                    f"{row.member}: Paid Amount cannot exceed Bill Amount"
                )

            members.append(
                row.member
            )

    def calculate_status(self):

        for row in self.electricity_split:

            row.balance = round(
                flt(row.bill_amount)
                - flt(row.paid_amount),
                2
            )

            if flt(row.paid_amount) == 0:

                row.status = "Pending"

            elif row.balance > 0.01:

                row.status = "Partial"

            else:

                row.balance = 0

                row.status = "Paid"

    def calculate_totals(self):

        collected = 0

        for row in self.electricity_split:

            collected += flt(
                row.paid_amount
            )

        self.collected_amount = round(
            collected,
            2
        )

        self.pending_amount = round(
            flt(self.total_amount)
            - collected,
            2
        )

        if self.collected_amount == 0:

            self.bill_status = "Pending"

        elif self.pending_amount > 0.01:

            self.bill_status = "Partial"

        else:

            self.bill_status = "Completed"

    def send_payment_notifications(self):

        for row in self.electricity_split:

            if row.status not in [
                "Partial",
                "Paid"
            ]:
                continue

            if row.email_sent:
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
                    "Partial Electricity Payment Received"
                )

                header_color = "#f59e0b"

                email_title = (
                    "Partial Electricity Payment Received"
                )

            else:

                subject = (
                    "Electricity Bill Paid Successfully"
                )

                header_color = "#16a34a"

                email_title = (
                    "Electricity Bill Paid Successfully"
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
                        Electricity Bill Update
                    </p>

                </div>

                <div style="
                    padding:30px;
                    background:white;
                    color:black;
                ">

                    <h2>
                        Hello {row.member},
                    </h2>

                    <p>
                        Your electricity payment has been updated.
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
                                ⚡ Bill Amount
                            </td>

                            <td style="
                                text-align:right;
                                font-weight:bold;
                                color:black;
                                border-bottom:1px solid #e5e7eb;
                            ">
                                ₹{row.bill_amount:.2f}
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
                                color:black;
                                border-bottom:1px solid #e5e7eb;
                            ">
                                ₹{row.paid_amount:.2f}
                            </td>
                        </tr>

                        <tr>
                            <td style="
                                padding:15px;
                                border-bottom:1px solid #e5e7eb;
                            ">
                                📌 Balance Amount
                            </td>

                            <td style="
                                text-align:right;
                                font-weight:bold;
                                color:black;
                                border-bottom:1px solid #e5e7eb;
                            ">
                                ₹{row.balance:.2f}
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

                    <p style="
                        margin-top:25px;
                        color:#374151;
                    ">
                        Thank you for your payment.
                    </p>

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

            row.email_sent = 1


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
