frappe.ui.form.on('Breeding Cycle', {
    refresh(frm) {
        // Show status indicator
        if (frm.doc.status) {
            let color = {
                'Draft': 'orange',
                'In Progress': 'blue',
                'Spawning Complete': 'purple',
                'Nursery': 'cyan',
                'Fingerlings Ready': 'green',
                'Completed': 'darkgrey',
                'Closed': 'green'
            };
            frm.page.set_indicator(frm.doc.status, color[frm.doc.status] || 'grey');
        }

        // Record Spawning button
        if (frm.doc.status === 'In Progress' && !frm.doc.fry_collected) {
            frm.add_custom_button(__('Record Spawning'), () => {
                let d = new frappe.ui.Dialog({
                    title: __('Record Spawning'),
                    fields: [
                        {fieldname: 'eggs_collected', fieldtype: 'Int', label: __('Eggs Collected'), reqd: 1},
                        {fieldname: 'hatching_rate', fieldtype: 'Percent', label: __('Hatching Rate %'), default: 85, reqd: 1},
                        {fieldname: 'nursery_tank', fieldtype: 'Link', label: __('Nursery Tank'), options: 'Location', reqd: 1},
                    ],
                    primary_action_label: __('Create'),
                    primary_action(values) {
                        frappe.call({
                            method: 'frappe.client.insert',
                            args: {
                                doc: {
                                    doctype: 'Spawning Record',
                                    breeding_cycle: frm.doc.name,
                                    spawning_date: frappe.datetime.get_today(),
                                    eggs_collected: values.eggs_collected,
                                    hatching_rate: values.hatching_rate,
                                    nursery_tank: values.nursery_tank,
                                    treatment_start_date: frappe.datetime.add_days(frappe.datetime.get_today(), 5),
                                    treatment_end_date: frappe.datetime.add_days(frappe.datetime.get_today(), 33),
                                }
                            },
                            callback(r) {
                                if (r.message) {
                                    frm.reload_doc();
                                    frappe.show_alert(__('Spawning Record {0} created', [r.message.name]));
                                }
                            }
                        });
                        d.hide();
                    }
                });
                d.show();
            }, __('Actions'));
        }

        // Produce Fingerlings button
        if (frm.doc.status === 'Spawning Complete' || frm.doc.status === 'Nursery') {
            frm.add_custom_button(__('Produce Fingerlings'), () => {
                let d = new frappe.ui.Dialog({
                    title: __('Produce Fingerlings'),
                    fields: [
                        {fieldname: 'count', fieldtype: 'Int', label: __('Fingerlings Count'), reqd: 1},
                        {fieldname: 'avg_weight', fieldtype: 'Float', label: __('Avg Weight (g)'), reqd: 1},
                    ],
                    primary_action_label: __('Produce'),
                    primary_action(values) {
                        frappe.call({
                            method: 'frappe.client.set_value',
                            args: {
                                doctype: 'Breeding Cycle',
                                name: frm.doc.name,
                                fieldname: {
                                    fingerlings_produced: values.count,
                                    avg_weight_grams: values.avg_weight,
                                    status: 'Fingerlings Ready'
                                }
                            },
                            callback(r) {
                                if (r.message) {
                                    // Auto-create batch and stock entry
                                    frappe.call({
                                        method: 'fish_production.breeding_cycle.produce_fingerlings',
                                        args: { cycle_name: frm.doc.name },
                                        callback(r2) {
                                            frm.reload_doc();
                                            frappe.show_alert(__('Fingerlings produced and batch created'));
                                        }
                                    });
                                }
                            }
                        });
                        d.hide();
                    }
                });
                d.show();
            }, __('Actions'));
        }

        // Record Sampling button
        if (frm.doc.status !== 'Draft' && frm.doc.output_batch) {
            frm.add_custom_button(__('Record Growth Sampling'), () => {
                frappe.new_doc('Growth Sampling', {
                    batch_no: frm.doc.output_batch || frm.doc.parent_batch,
                    sampling_date: frappe.datetime.get_today(),
                    location: frm.doc.pond || frm.doc.nursery_tank,
                });
            }, __('Actions'));
        }

        // Link to Batch
        if (frm.doc.output_batch) {
            frm.add_custom_button(__('Open Batch'), () => {
                frappe.set_route('Form', 'Batch', frm.doc.output_batch);
            }, __('View'));
        }

        // Link to Work Order
        if (frm.doc.work_order) {
            frm.add_custom_button(__('Open Work Order'), () => {
                frappe.set_route('Form', 'Work Order', frm.doc.work_order);
            }, __('View'));
        }
    },

    male_count(frm) {
        calculate_total_broodstock(frm);
    },

    female_count(frm) {
        calculate_total_broodstock(frm);
    },

    eggs_collected(frm) {
        calculate_fry(frm);
    },

    hatching_rate(frm) {
        calculate_fry(frm);
    }
});

function calculate_total_broodstock(frm) {
    frm.set_value('total_broodstock', (frm.doc.male_count || 0) + (frm.doc.female_count || 0));
}

function calculate_fry(frm) {
    if (frm.doc.eggs_collected && frm.doc.hatching_rate) {
        frm.set_value('fry_collected', Math.floor(frm.doc.eggs_collected * frm.doc.hatching_rate / 100));
    }
}
