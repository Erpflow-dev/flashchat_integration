// flashchat_integration/public/js/contact_integration.js
frappe.ui.form.on('Contact', {
    refresh: function(frm) {
        if (frm.doc.phone_nos && frm.doc.phone_nos.length > 0) {
            // Add FlashChat button group
            frm.add_custom_button(__('Send SMS'), function() {
                send_sms_dialog(frm);
            }, __('FlashChat'));
            
            frm.add_custom_button(__('Send WhatsApp'), function() {
                send_whatsapp_dialog(frm);
            }, __('FlashChat'));
            
            frm.add_custom_button(__('Send OTP'), function() {
                send_otp_dialog(frm);
            }, __('FlashChat'));
        }
        
        // Add message history button
        frm.add_custom_button(__('Message History'), function() {
            frappe.route_options = {
                "reference_doctype": "Contact",
                "reference_name": frm.doc.name
            };
            frappe.set_route("List", "FlashChat Message Log");
        }, __('FlashChat'));
        
        // Add sync status indicator
        if (frm.doc.flashchat_synced) {
            frm.dashboard.add_indicator(__('Synced to FlashChat'), 'green');
        }
    }
});

frappe.ui.form.on('Customer', {
    refresh: function(frm) {
        if (frm.doc.mobile_no) {
            frm.add_custom_button(__('Send SMS'), function() {
                send_sms_to_customer(frm);
            }, __('FlashChat'));
            
            frm.add_custom_button(__('Send WhatsApp'), function() {
                send_whatsapp_to_customer(frm);
            }, __('FlashChat'));
        }
        
        // Add message history
        frm.add_custom_button(__('Message History'), function() {
            frappe.route_options = {
                "reference_doctype": "Customer",
                "reference_name": frm.doc.name
            };
            frappe.set_route("List", "FlashChat Message Log");
        }, __('FlashChat'));
    }
});

frappe.ui.form.on('Lead', {
    refresh: function(frm) {
        if (frm.doc.mobile_no) {
            frm.add_custom_button(__('Send SMS'), function() {
                send_sms_to_lead(frm);
            }, __('FlashChat'));
            
            frm.add_custom_button(__('Send WhatsApp'), function() {
                send_whatsapp_to_lead(frm);
            }, __('FlashChat'));
        }
    }
});

frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1 && !frm.doc.confirmation_sms_sent) {
            frm.add_custom_button(__('Send Confirmation SMS'), function() {
                send_order_confirmation_sms(frm);
            }, __('FlashChat'));
        }
    }
});

// Helper functions for form integrations
function send_sms_dialog(frm) {
    let phone = get_primary_phone(frm);
    if (!phone) {
        frappe.msgprint(__('No phone number found'));
        return;
    }
    
    let dialog = new frappe.ui.Dialog({
        title: __('Send SMS'),
        fields: [
            {
                fieldtype: 'Data',
                fieldname: 'phone',
                label: __('Phone Number'),
                default: phone,
                reqd: 1
            },
            {
                fieldtype: 'Long Text',
                fieldname: 'message',
                label: __('Message'),
                reqd: 1
            },
            {
                fieldtype: 'Select',
                fieldname: 'sim',
                label: __('SIM'),
                options: '1\n2',
                default: '1'
            }
        ],
        primary_action_label: __('Send'),
        primary_action: function(values) {
            frappe.call({
                method: 'flashchat_integration.api.flashchat_api.send_sms_api',
                args: {
                    phone: values.phone,
                    message: values.message,
                    sim: values.sim,
                    reference_doctype: frm.doc.doctype,
                    reference_name: frm.doc.name
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: __('SMS sent successfully'),
                            indicator: 'green'
                        });
                        dialog.hide();
                        frm.reload_doc();
                    } else {
                        frappe.msgprint(__('Failed to send SMS: ') + (r.message.error || 'Unknown error'));
                    }
                }
            });
        }
    });
    
    dialog.show();
}

function send_whatsapp_dialog(frm) {
    let phone = get_primary_phone(frm);
    if (!phone) {
        frappe.msgprint(__('No phone number found'));
        return;
    }
    
    frappe.call({
        method: 'flashchat_integration.api.flashchat_api.get_whatsapp_accounts_api',
        callback: function(r) {
            if (r.message && r.message.success && r.message.data.length > 0) {
                let accounts = r.message.data;
                let account_options = accounts.map(acc => acc.unique + ' - ' + acc.phone);
                
                let dialog = new frappe.ui.Dialog({
                    title: __('Send WhatsApp'),
                    fields: [
                        {
                            fieldtype: 'Select',
                            fieldname: 'account',
                            label: __('WhatsApp Account'),
                            options: account_options,
                            reqd: 1
                        },
                        {
                            fieldtype: 'Data',
                            fieldname: 'phone',
                            label: __('Phone Number'),
                            default: phone,
                            reqd: 1
                        },
                        {
                            fieldtype: 'Long Text',
                            fieldname: 'message',
                            label: __('Message'),
                            reqd: 1
                        }
                    ],
                    primary_action_label: __('Send'),
                    primary_action: function(values) {
                        let account_id = values.account.split(' - ')[0];
                        
                        frappe.call({
                            method: 'flashchat_integration.api.flashchat_api.send_whatsapp_api',
                            args: {
                                account: account_id,
                                recipient: values.phone,
                                message: values.message,
                                reference_doctype: frm.doc.doctype,
                                reference_name: frm.doc.name
                            },
                            callback: function(r) {
                                if (r.message && r.message.success) {
                                    frappe.show_alert({
                                        message: __('WhatsApp message sent successfully'),
                                        indicator: 'green'
                                    });
                                    dialog.hide();
                                    frm.reload_doc();
                                } else {
                                    frappe.msgprint(__('Failed to send WhatsApp: ') + (r.message.error || 'Unknown error'));
                                }
                            }
                        });
                    }
                });
                
                dialog.show();
            } else {
                frappe.msgprint(__('No WhatsApp accounts configured'));
            }
        }
    });
}

function send_otp_dialog(frm) {
    let phone = get_primary_phone(frm);
    if (!phone) {
        frappe.msgprint(__('No phone number found'));
        return;
    }
    
    let dialog = new frappe.ui.Dialog({
        title: __('Send OTP'),
        fields: [
            {
                fieldtype: 'Data',
                fieldname: 'phone',
                label: __('Phone Number'),
                default: phone,
                reqd: 1
            },
            {
                fieldtype: 'Int',
                fieldname: 'expire',
                label: __('Expire (seconds)'),
                default: 300,
                reqd: 1
            }
        ],
        primary_action_label: __('Send OTP'),
        primary_action: function(values) {
            frappe.call({
                method: 'flashchat_integration.api.flashchat_api.send_otp_api',
                args: {
                    phone: values.phone,
                    expire: values.expire,
                    reference_doctype: frm.doc.doctype,
                    reference_name: frm.doc.name
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        let otp = r.message.data.otp_code;
                        frappe.show_alert({
                            message: __('OTP sent successfully. OTP: ') + otp,
                            indicator: 'green'
                        });
                        dialog.hide();
                        
                        // Show OTP verification dialog
                        show_otp_verification_dialog(otp);
                    } else {
                        frappe.msgprint(__('Failed to send OTP: ') + (r.message.error || 'Unknown error'));
                    }
                }
            });
        }
    });
    
    dialog.show();
}

function show_otp_verification_dialog(sent_otp) {
    let verify_dialog = new frappe.ui.Dialog({
        title: __('Verify OTP'),
        fields: [
            {
                fieldtype: 'Data',
                fieldname: 'otp_code',
                label: __('Enter OTP'),
                reqd: 1
            }
        ],
        primary_action_label: __('Verify'),
        primary_action: function(values) {
            frappe.call({
                method: 'flashchat_integration.api.flashchat_api.verify_otp_api',
                args: {
                    otp_code: values.otp_code
                },
                callback: function(r) {
                    if (r.message && r.message.success && r.message.valid) {
                        frappe.show_alert({
                            message: __('OTP verified successfully!'),
                            indicator: 'green'
                        });
                        verify_dialog.hide();
                    } else {
                        frappe.msgprint(__('Invalid OTP. Please try again.'));
                    }
                }
            });
        }
    });
    
    verify_dialog.show();
}

function send_sms_to_customer(frm) {
    send_generic_sms(frm, frm.doc.mobile_no, 'Customer');
}

function send_whatsapp_to_customer(frm) {
    send_generic_whatsapp(frm, frm.doc.mobile_no, 'Customer');
}

function send_sms_to_lead(frm) {
    send_generic_sms(frm, frm.doc.mobile_no, 'Lead');
}

function send_whatsapp_to_lead(frm) {
    send_generic_whatsapp(frm, frm.doc.mobile_no, 'Lead');
}

function send_generic_sms(frm, phone, doctype) {
    let dialog = new frappe.ui.Dialog({
        title: __('Send SMS to ') + doctype,
        fields: [
            {
                fieldtype: 'Data',
                fieldname: 'phone',
                label: __('Phone Number'),
                default: phone,
                reqd: 1
            },
            {
                fieldtype: 'Long Text',
                fieldname: 'message',
                label: __('Message'),
                reqd: 1
            }
        ],
        primary_action_label: __('Send'),
        primary_action: function(values) {
            frappe.call({
                method: 'flashchat_integration.api.flashchat_api.send_sms_api',
                args: {
                    phone: values.phone,
                    message: values.message,
                    reference_doctype: doctype,
                    reference_name: frm.doc.name
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: __('SMS sent successfully'),
                            indicator: 'green'
                        });
                        dialog.hide();
                    } else {
                        frappe.msgprint(__('Failed to send SMS: ') + (r.message.error || 'Unknown error'));
                    }
                }
            });
        }
    });
    
    dialog.show();
}

function send_generic_whatsapp(frm, phone, doctype) {
    frappe.call({
        method: 'flashchat_integration.api.flashchat_api.get_whatsapp_accounts_api',
        callback: function(r) {
            if (r.message && r.message.success && r.message.data.length > 0) {
                let accounts = r.message.data;
                let account_options = accounts.map(acc => acc.unique + ' - ' + acc.phone);
                
                let dialog = new frappe.ui.Dialog({
                    title: __('Send WhatsApp to ') + doctype,
                    fields: [
                        {
                            fieldtype: 'Select',
                            fieldname: 'account',
                            label: __('WhatsApp Account'),
                            options: account_options,
                            reqd: 1
                        },
                        {
                            fieldtype: 'Data',
                            fieldname: 'phone',
                            label: __('Phone Number'),
                            default: phone,
                            reqd: 1
                        },
                        {
                            fieldtype: 'Long Text',
                            fieldname: 'message',
                            label: __('Message'),
                            reqd: 1
                        }
                    ],
                    primary_action_label: __('Send'),
                    primary_action: function(values) {
                        let account_id = values.account.split(' - ')[0];
                        
                        frappe.call({
                            method: 'flashchat_integration.api.flashchat_api.send_whatsapp_api',
                            args: {
                                account: account_id,
                                recipient: values.phone,
                                message: values.message,
                                reference_doctype: doctype,
                                reference_name: frm.doc.name
                            },
                            callback: function(r) {
                                if (r.message && r.message.success) {
                                    frappe.show_alert({
                                        message: __('WhatsApp message sent successfully'),
                                        indicator: 'green'
                                    });
                                    dialog.hide();
                                } else {
                                    frappe.msgprint(__('Failed to send WhatsApp: ') + (r.message.error || 'Unknown error'));
                                }
                            }
                        });
                    }
                });
                
                dialog.show();
            } else {
                frappe.msgprint(__('No WhatsApp accounts configured'));
            }
        }
    });
}

function get_primary_phone(frm) {
    if (frm.doc.phone_nos && frm.doc.phone_nos.length > 0) {
        for (let phone_entry of frm.doc.phone_nos) {
            if (phone_entry.is_primary_phone && phone_entry.phone) {
                return phone_entry.phone;
            }
        }
        return frm.doc.phone_nos[0].phone;
    }
    return null;
}

function send_order_confirmation_sms(frm) {
    if (!frm.doc.contact_mobile) {
        frappe.msgprint(__('No mobile number found for customer'));
        return;
    }
    
    let message = `Your order ${frm.doc.name} has been confirmed. Total: ${frm.doc.currency} ${frm.doc.grand_total}. Thank you for your business!`;
    
    frappe.call({
        method: 'flashchat_integration.api.flashchat_api.send_sms_api',
        args: {
            phone: frm.doc.contact_mobile,
            message: message,
            reference_doctype: 'Sales Order',
            reference_name: frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.show_alert({
                    message: __('Confirmation SMS sent successfully'),
                    indicator: 'green'
                });
                
                // Mark SMS as sent
                frappe.call({
                    method: 'frappe.client.set_value',
                    args: {
                        doctype: 'Sales Order',
                        name: frm.doc.name,
                        fieldname: 'confirmation_sms_sent',
                        value: 1
                    },
                    callback: function() {
                        frm.reload_doc();
                    }
                });
            } else {
                frappe.msgprint(__('Failed to send SMS: ') + (r.message.error || 'Unknown error'));
            }
        }
    });
}