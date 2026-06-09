import frappe
from frappe.model.document import Document
from frappe.utils import flt


class RoomRent(Document):

    def validate(self):

        self.validate_month()
        self.validate_rent()
        self.validate_members()

        self.calculate_status()
        self.calculate_totals()

    def on_update(self):

        self.send_payment_notifications()

    def validate_month(self):

        if not self.rent_month:

            frappe.throw(
                "Rent Month is required"
            )

    def validate_rent(self):

        if flt(self.total_rent) <= 0:

            frappe.throw(
                "Total Rent must be greater than zero"
            )

    def validate_members(self):

        if not self.rent_split:

            frappe.throw(
                "Rent Split cannot be empty"
            )

        members = []

        for row in self.rent_split:

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

            if flt(row.paid_amount) > flt(row.rent_amount):

                frappe.throw(
                    f"{row.member}: Paid Amount cannot exceed Rent Amount"
                )

            members.append(
                row.member
            )

    def calculate_status(self):

        for row in self.rent_split:

            row.balance = round(
                flt(row.rent_amount)
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

        for row in self.rent_split:

            collected += flt(
                row.paid_amount
            )

        self.collected_amount = round(
            collected,
            2
        )

        self.pending_amount = round(
            flt(self.total_rent)
            - collected,
            2
        )

        if self.collected_amount == 0:

            self.rent_status = "Pending"

        elif self.pending_amount > 0.01:

            self.rent_status = "Partial"

        else:

            self.rent_status = "Completed"

    def send_payment_notifications(self):

        for row in self.rent_split:

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
                    "Partial Room Rent Payment Received"
                )

                header_color = "#f59e0b"

            else:

                subject = (
                    "Room Rent Paid Successfully"
                )

                header_color = "#16a34a"

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
                    color:white;
                ">

                    <h1>
                        Room Rent Payment Update
                    </h1>

                </div>

                <div style="
                    padding:30px;
                    color:black;
                ">

                    <h2>
                        Hello {row.member},
                    </h2>

                    <p>
                        Your room rent payment status has been updated.
                    </p>

                    <table style="
                        width:100%;
                        border-collapse:collapse;
                        margin-top:20px;
                    ">

                        <tr>
                            <td style="padding:12px;">
                                Rent Amount
                            </td>

                            <td align="right">
                                ₹{row.rent_amount:.2f}
                            </td>
                        </tr>

                        <tr>
                            <td style="padding:12px;">
                                Paid Amount
                            </td>

                            <td align="right">
                                ₹{row.paid_amount:.2f}
                            </td>
                        </tr>

                        <tr>
                            <td style="padding:12px;">
                                Balance Amount
                            </td>

                            <td align="right">
                                ₹{row.balance:.2f}
                            </td>
                        </tr>

                        <tr>
                            <td style="padding:12px;">
                                Payment Status
                            </td>

                            <td align="right">
                                {row.status}
                            </td>
                        </tr>

                    </table>

                    <div style="
                        margin-top:25px;
                        padding:20px;
                        background:#f9fafb;
                        border-radius:10px;
                    ">

                        <strong>
                            Current Status:
                        </strong>

                        {row.status}
                        <a href="upi://pay?pa=test@upi&pn=Test Merchant&am=100&cu=INR">
                            Pay with Google Pay
                        </a>

                    </div>

                    <p style="
                        margin-top:25px;
                    ">
                        Thank you for your payment.
                    </p>

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
