frappe.ui.form.on("Grocery Budget", {

    refresh(frm) {

        if (!frm.is_new()) {

            frm.add_custom_button(
                "Payment Reminders",
                () => {

                    frappe.call({
                        method:
                            "roommate_expense_manager.api.send_all_pending_reminders",

                        callback() {

                            frappe.msgprint(
                                "Pending Bill Reminders Sent"
                            );

                        }
                    });

                }
            );

        }

    },

    budget_amount(frm) {

        if (!frm.doc.budget_amount) {
            return;
        }

        frappe.call({
            method:
                "roommate_expense_manager.roommate_expense_manager.doctype.grocery_budget.grocery_budget.get_active_members",

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
                    "contributors"
                );

                let share =
                    flt(frm.doc.budget_amount)
                    / r.message.length;

                r.message.forEach(member => {

                    let row =
                        frm.add_child(
                            "contributors"
                        );

                    row.member =
                        member.name;

                    row.expected_amount =
                        share;

                    row.paid_amount = 0;

                    row.new_payment = 0;

                    row.remaining_amount =
                        share;

                    row.status =
                        "Pending";

                    row.last_email_status = "";

                });

                frm.refresh_field(
                    "contributors"
                );

            }
        });

    }

});


frappe.ui.form.on(
    "Grocery Contributors",
    {

        new_payment(
            frm,
            cdt,
            cdn
        ) {

            let row =
                locals[cdt][cdn];

            if (
                flt(row.new_payment) <= 0
            ) {
                return;
            }

            let remaining =
                flt(row.expected_amount)
                -
                flt(row.paid_amount);

            if (
                remaining <= 0
            ) {

                frappe.msgprint(
                    `${row.member} has already paid the full amount.`
                );

                row.new_payment = 0;

                frm.refresh_field(
                    "contributors"
                );

                return;
            }

            if (
                flt(row.new_payment)
                > remaining
            ) {

                frappe.msgprint(
                    `${row.member} can pay only ₹${remaining.toFixed(2)}. Payment exceeds the expected amount.`
                );

                row.new_payment = 0;

                frm.refresh_field(
                    "contributors"
                );

                return;
            }

        }

    }
);
