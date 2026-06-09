frappe.ui.form.on("Electricity Bill", {

    total_amount(frm) {

        if (!frm.doc.total_amount) {
            return;
        }

        frappe.call({
            method:
                "roommate_expense_manager.roommate_expense_manager.doctype.electricity_bill.electricity_bill.get_active_members",

            callback(r) {

                if (
                    !r.message ||
                    !r.message.length
                ) {

                    frappe.msgprint(
                        "No Active Members Found"
                    );

                    return;
                }

                frm.clear_table(
                    "electricity_split"
                );

                let total_amount =
                    flt(frm.doc.total_amount);

                let count =
                    r.message.length;

                let share =
                    Math.floor(
                        (total_amount / count) * 100
                    ) / 100;

                let assigned =
                    share * count;

                let difference =
                    Math.round(
                        (
                            total_amount
                            - assigned
                        ) * 100
                    ) / 100;

                r.message.forEach(
                    (member, index) => {

                        let row =
                            frm.add_child(
                                "electricity_split"
                            );

                        row.member =
                            member.name;

                        row.bill_amount =
                            share;

                        if (
                            index === count - 1
                        ) {

                            row.bill_amount =
                                share +
                                difference;
                        }

                        row.paid_amount = 0;

                        row.balance =
                            row.bill_amount;

                        row.status =
                            "Pending";
                    }
                );

                frm.refresh_field(
                    "electricity_split"
                );
            }
        });
    }
});


frappe.ui.form.on(
    "Electricity Split",
    {

        paid_amount(
            frm,
            cdt,
            cdn
        ) {

            let row =
                locals[cdt][cdn];

            row.balance =
                Math.round(
                    (
                        flt(row.bill_amount)
                        -
                        flt(row.paid_amount)
                    ) * 100
                ) / 100;

            if (
                flt(row.paid_amount) === 0
            ) {

                row.status =
                    "Pending";
            }

            else if (
                row.balance > 0.01
            ) {

                row.status =
                    "Partial";
            }

            else {

                row.balance = 0;

                row.status =
                    "Paid";
            }

            let collected = 0;

            (frm.doc.electricity_split || [])
                .forEach(r => {

                    collected += flt(
                        r.paid_amount
                    );

                });

            collected =
                Math.round(
                    collected * 100
                ) / 100;

            frm.set_value(
                "collected_amount",
                collected
            );

            let pending =
                Math.round(
                    (
                        flt(frm.doc.total_amount)
                        - collected
                    ) * 100
                ) / 100;

            frm.set_value(
                "pending_amount",
                pending
            );

            if (
                collected === 0
            ) {

                frm.set_value(
                    "bill_status",
                    "Pending"
                );
            }

            else if (
                pending > 0.01
            ) {

                frm.set_value(
                    "bill_status",
                    "Partial"
                );
            }

            else {

                frm.set_value(
                    "bill_status",
                    "Completed"
                );
            }

            frm.refresh_field(
                "electricity_split"
            );
        }
    }
);