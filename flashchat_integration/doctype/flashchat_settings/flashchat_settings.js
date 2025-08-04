// flashchat_integration/doctype/flashchat_settings/flashchat_settings.js
frappe.ui.form.on('FlashChat Settings', {
    refresh: function(frm) {
        // Add test connection button
        frm.add_custom_button(__('Test Connection'), function() {
            if (!frm.doc.api_secret) {
                frappe.msgprint(__('Please enter API Secret first'));
                return;
            }
            
            frappe.call({
                method: 'test_api_connection',
                doc: frm.doc,
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: __('Connection test successful!'),
                            indicator: 'green'
                        });
                    } else {
                        frappe.msgprint(__('Connection failed: ') + (r.message.error || 'Unknown error'));
                    }
                }
            });
        });
        
        // Add sync contacts button
        frm.add_custom_button(__('Sync All Contacts'), function() {
            frappe.confirm(
                __('This will sync all contacts with phone numbers to FlashChat. Continue?'),
                function() {
                    frappe.call({
                        method: 'flashchat_integration.api.utils.sync_all_contacts',
                        callback: function(r) {
                            if (r.message) {
                                frappe.msgprint(__('Synced {0} contacts successfully', [r.message]));
                            }
                        }
                    });
                }
            );
        });
        
        // Add get devices button
        frm.add_custom_button(__('Get Devices'), function() {
            frappe.call({
                method: 'flashchat_integration.api.flashchat_api.get_devices_api',
                callback: function(r) {
                    if (r.message && r.message.success) {
                        show_devices_dialog(r.message.data);
                    } else {
                        frappe.msgprint(__('Failed to get devices'));
                    }
                }
            });
        });
        
        // Add get WhatsApp accounts button
        frm.add_custom_button(__('Get WhatsApp Accounts'), function() {
            frappe.call({
                method: 'flashchat_integration.api.flashchat_api.get_whatsapp_accounts_api',
                callback: function(r) {
                    if (r.message && r.message.success) {
                        show_whatsapp_accounts_dialog(r.message.data);
                    } else {
                        frappe.msgprint(__('Failed to get WhatsApp accounts'));
                    }
                }
            });
        });
        
        // Show webhook URL
        if (frm.doc.webhook_enabled) {
            let webhook_url = window.location.origin + '/api/method/flashchat_integration.api.webhooks.flashchat_webhook';
            frm.dashboard.add_comment(__('Webhook URL: ') + webhook_url, 'blue', true);
        }
    },
    
    enable_sms: function(frm) {
        if (frm.doc.enable_sms) {
            frm.set_df_property('sms_rate_limit', 'reqd', 1);
        } else {
            frm.set_df_property('sms_rate_limit', 'reqd', 0);
        }
    },
    
    enable_whatsapp: function(frm) {
        if (frm.doc.enable_whatsapp) {
            frm.set_df_property('whatsapp_rate_limit', 'reqd', 1);
        } else {
            frm.set_df_property('whatsapp_rate_limit', 'reqd', 0);
        }
    },
    
    enable_otp: function(frm) {
        if (frm.doc.enable_otp) {
            frm.set_df_property('otp_rate_limit', 'reqd', 1);
        } else {
            frm.set_df_property('otp_rate_limit', 'reqd', 0);
        }
    }
});

function show_devices_dialog(devices) {
    let device_html = '<table class="table table-bordered"><thead><tr><th>Name</th><th>Manufacturer</th><th>Version</th><th>Status</th></tr></thead><tbody>';
    
    devices.forEach(device => {
        const status = device.partner ? 'Partner' : 'Active';
        device_html += `
            <tr>
                <td>${device.name || 'Unknown'}</td>
                <td>${device.manufacturer || 'Unknown'}</td>
                <td>${device.version || 'Unknown'}</td>
                <td><span class="label label-success">${status}</span></td>
            </tr>
        `;
    });
    
    device_html += '</tbody></table>';
    
    frappe.msgprint({
        title: __('Connected Devices'),
        message: device_html,
        wide: true
    });
}

function show_whatsapp_accounts_dialog(accounts) {
    let account_html = '<table class="table table-bordered"><thead><tr><th>Phone</th><th>Status</th><th>Created</th></tr></thead><tbody>';
    
    accounts.forEach(account => {
        const status_class = account.status === 'connected' ? 'label-success' : 'label-warning';
        account_html += `
            <tr>
                <td>${account.phone}</td>
                <td><span class="label ${status_class}">${account.status}</span></td>
                <td>${frappe.datetime.str_to_user(new Date(account.created * 1000))}</td>
            </tr>
        `;
    });
    
    account_html += '</tbody></table>';
    
    frappe.msgprint({
        title: __('WhatsApp Accounts'),
        message: account_html,
        wide: true
    });
}