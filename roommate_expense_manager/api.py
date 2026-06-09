import frappe
from frappe.utils import flt


@frappe.whitelist()
def send_all_pending_reminders():

    members = frappe.get_all(
        "Room Member",
        filters={
            "active": 1
        },
        fields=[
            "name",
            "email"
        ]
    )

    sent_count = 0

    for member in members:

        rent_pending = get_rent_pending(
            member.name
        )

        electricity_pending = (
            get_electricity_pending(
                member.name
            )
        )

        grocery_pending = (
            get_grocery_pending(
                member.name
            )
        )

        total_pending = (
            rent_pending
            + electricity_pending
            + grocery_pending
        )

        if total_pending <= 0:
            continue

        if not member.email:
            continue

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

            <!-- Header -->

            <div style="
                background:#dc2626;
                padding:30px;
                text-align:center;
            ">

                <h1 style="
                    color:white;
                    margin:0;
                    font-size:28px;
                ">
                    Roommate Expense Reminder
                </h1>

                <p style="
                    color:white;
                    margin-top:10px;
                    font-size:15px;
                ">
                    Monthly Pending Bill Summary
                </p>

            </div>

            <!-- Body -->

            <div style="
                padding:30px;
                background:white;
                color:black;
            ">

                <h2>
                    Hello {member.name},
                </h2>

                <p>
                    Below is your pending payment summary.
                </p>

                <table style="
                    width:100%;
                    border-collapse:collapse;
                    margin-top:25px;
                ">

                    <tr>
                        <td style="
                            padding:15px;
                            font-size:16px;
                            border-bottom:1px solid #e5e7eb;
                        ">
                            🏠 Room Rent
                        </td>

                        <td style="
                            text-align:right;
                            font-size:18px;
                            font-weight:bold;
                            color:black;
                            border-bottom:1px solid #e5e7eb;
                        ">
                            ₹{rent_pending:.2f}
                        </td>
                    </tr>

                    <tr>
                        <td style="
                            padding:15px;
                            font-size:16px;
                            border-bottom:1px solid #e5e7eb;
                        ">
                            ⚡ Electricity Bill
                        </td>

                        <td style="
                            text-align:right;
                            font-size:18px;
                            font-weight:bold;
                            color:black;
                            border-bottom:1px solid #e5e7eb;
                        ">
                            ₹{electricity_pending:.2f}
                        </td>
                    </tr>

                    <tr>
                        <td style="
                            padding:15px;
                            font-size:16px;
                            border-bottom:1px solid #e5e7eb;
                        ">
                            🛒 Grocery Contribution
                        </td>

                        <td style="
                            text-align:right;
                            font-size:18px;
                            font-weight:bold;
                            color:black;
                            border-bottom:1px solid #e5e7eb;
                        ">
                            ₹{grocery_pending:.2f}
                        </td>
                    </tr>

                </table>

                <!-- Total -->

                <div style="
                    margin-top:30px;
                    background:#fef2f2;
                    border-left:6px solid #dc2626;
                    padding:20px;
                    border-radius:8px;
                ">

                    <h2 style="
                        margin:0;
                        color:#dc2626;
                    ">
                        Total Pending
                    </h2>

                    <h1 style="
                        margin-top:10px;
                        color:black;
                    ">
                        ₹{total_pending:.2f}
                    </h1>

                </div>

                <a href="upi://pay?pa=test@upi&pn=Test Merchant&am=100&cu=INR">
                            Pay with Google Pay
                        </a>

                <p style="
                    margin-top:30px;
                    color:#374151;
                    line-height:1.8;
                ">
                    Please complete your pending payment at the earliest to keep all shared expenses up to date.
                </p>

            </div>

            <!-- Footer -->

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

                Automated Monthly Reminder

            </div>

        </div>
        """

        frappe.sendmail(
            recipients=[member.email],
            subject="Roommate Expense Reminder",
            message=message
        )

        sent_count += 1

    frappe.msgprint(
        f"{sent_count} reminder emails sent successfully."
    )

    return sent_count


def get_rent_pending(member):

    rows = frappe.get_all(
        "Room Rent Split",
        filters={
            "member": member
        },
        fields=[
            "balance"
        ]
    )

    return sum(
        flt(row.balance)
        for row in rows
    )


def get_electricity_pending(member):

    rows = frappe.get_all(
        "Electricity Split",
        filters={
            "member": member
        },
        fields=[
            "balance"
        ]
    )

    return sum(
        flt(row.balance)
        for row in rows
    )


def get_grocery_pending(member):

    rows = frappe.get_all(
        "Grocery Contributors",
        filters={
            "member": member
        },
        fields=[
            "remaining_amount"
        ]
    )

    return sum(
        flt(row.remaining_amount)
        for row in rows
    )