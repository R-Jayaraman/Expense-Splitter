frappe.ui.form.on('Room Member', {
    first_name: function(frm) {
        frm.set_value(
            'full_name',
            [frm.doc.first_name, frm.doc.last_name].filter(Boolean).join(' ')
        );
    },

    last_name: function(frm) {
        frm.set_value(
            'full_name',
            [frm.doc.first_name, frm.doc.last_name].filter(Boolean).join(' ')
        );
    }
});