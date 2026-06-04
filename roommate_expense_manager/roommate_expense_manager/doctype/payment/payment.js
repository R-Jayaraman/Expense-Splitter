frappe.ui.form.on("Payment", {

    refresh(frm) {
        fetch_expense_configuration(frm);
    },

    expense_type(frm) {
        fetch_expense_amount(frm);
    },

    total_amount(frm) {
        calculate_split(frm);
    }
});


function fetch_expense_configuration(frm) {

    frappe.db.get_doc(
        "Expense Configuration",
        "Entery-0001"
    ).then(doc => {

        frm.set_value(
            "actual_amount",
            doc.actual_amount || 0
        );

    });
}


function fetch_expense_amount(frm) {

    if (!frm.doc.expense_type) return;

    frappe.db.get_doc(
        "Expense Configuration",
        "Entery-0001"
    ).then(doc => {

        let amount = 0;

        switch (frm.doc.expense_type) {

            case "Room Rent":
                amount = doc.room_rent || 0;
                break;

            case "Grocery":
                amount = doc.grocery || 0;
                break;

        }

        frm.set_value("total_amount", amount);

        calculate_split(frm);
    });
}


frappe.ui.form.on("Room Member", {

    member_name(frm) {
        calculate_split(frm);
    },

    room_members_add(frm) {
        calculate_split(frm);
    },

    room_members_remove(frm) {
        calculate_split(frm);
    }

});


function calculate_split(frm) {

    let total = flt(frm.doc.total_amount || 0);

    let selected_members = (frm.doc.room_members || []).filter(
        row => row.member_name
    );

    let count = selected_members.length;

    if (!count) {

        (frm.doc.room_members || []).forEach(row => {
            row.amount = 0;
        });

        frm.refresh_field("room_members");
        return;
    }

    let share = total / count;

    (frm.doc.room_members || []).forEach(row => {

        if (row.member_name) {
            row.amount = share;
        } else {
            row.amount = 0;
        }

    });

    frm.refresh_field("room_members");
}