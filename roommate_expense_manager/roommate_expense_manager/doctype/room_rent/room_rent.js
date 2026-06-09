frappe.ui.form.on("Room Rent", {

    refresh(frm) {

        if (!frm.is_new()) {

            frm.add_custom_button(
                "Payment Reminders",
                () => {

                    frappe.call({
                        method:
                            "roommate_expense_manager.api.send_all_pending_reminders",

                        callback(r) {

                            frappe.msgprint(
                                "Pending Bill Reminders Sent"
                            );

                        }
                    });

                }
            );

        }

    },

    total_rent(frm) {

        if (!frm.doc.total_rent) {
            return;
        }

        frappe.call({
            method:
                "roommate_expense_manager.roommate_expense_manager.doctype.room_rent.room_rent.get_active_members",

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
                    "rent_split"
                );

                let total_rent =
                    flt(frm.doc.total_rent);

                let count =
                    r.message.length;

                let share =
                    Math.floor(
                        (total_rent / count) * 100
                    ) / 100;

                let assigned =
                    share * count;

                let difference =
                    Math.round(
                        (
                            total_rent - assigned
                        ) * 100
                    ) / 100;

                r.message.forEach(
                    (member, index) => {

                        let row =
                            frm.add_child(
                                "rent_split"
                            );

                        row.member =
                            member.name;

                        row.rent_amount =
                            share;

                        if (
                            index === count - 1
                        ) {

                            row.rent_amount =
                                share +
                                difference;

                        }

                        row.paid_amount = 0;

                        row.balance =
                            row.rent_amount;

                        row.status =
                            "Pending";

                    }
                );

                frm.refresh_field(
                    "rent_split"
                );

            }
        });

    }

});


frappe.ui.form.on(
    "Room Rent Split",
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
                        flt(row.rent_amount)
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

            (frm.doc.rent_split || [])
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
                        flt(frm.doc.total_rent)
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
                    "rent_status",
                    "Pending"
                );

            }

            else if (
                pending > 0.01
            ) {

                frm.set_value(
                    "rent_status",
                    "Partial"
                );

            }

            else {

                frm.set_value(
                    "rent_status",
                    "Completed"
                );

            }

            frm.refresh_field(
                "rent_split"
            );

        }

    }
);