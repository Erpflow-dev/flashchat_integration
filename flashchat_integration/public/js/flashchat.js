// flashchat_integration/public/js/flashchat.js
frappe.ready(function() {
    // Add FlashChat dashboard widget if on desk
    if (frappe.get_route()[0] === 'desk' || window.location.pathname === '/app') {
        setTimeout(add_flashchat_dashboard_widget, 1000);
    }
});

function add_flashchat_dashboard_widget() {
    // Check if widget already exists
    if (document.querySelector('.flashchat-dashboard-widget')) {
        document.querySelector('.flashchat-dashboard-widget').remove();
    }
    
    frappe.call({
        method: 'flashchat_integration.api.utils.get_dashboard_stats_api',
        callback: function(r) {
            if (r.message && r.message.success) {
                render_flashchat_widget(r.message.data);
            }
        }
    });
}

function render_flashchat_widget(stats) {
    const widget_html = `
        <div class="flashchat-dashboard-widget">
            <div class="widget-header">
                <h4><i class="fa fa-mobile"></i> FlashChat Messages</h4>
                <div class="widget-refresh" onclick="add_flashchat_dashboard_widget()">
                    <i class="fa fa-refresh"></i>
                </div>
            </div>
            <div class="widget-content">
                <div class="flashchat-stats-row">
                    <div class="flashchat-stat-item">
                        <div class="flashchat-stat-number success">${stats.this_week.total_sent || 0}</div>
                        <div class="flashchat-stat-label">Sent This Week</div>
                    </div>
                    <div class="flashchat-stat-item">
                        <div class="flashchat-stat-number primary">${stats.this_week.total_delivered || 0}</div>
                        <div class="flashchat-stat-label">Delivered</div>
                    </div>
                    <div class="flashchat-stat-item">
                        <div class="flashchat-stat-number danger">${stats.this_week.total_failed || 0}</div>
                        <div class="flashchat-stat-label">Failed</div>
                    </div>
                </div>
                <div class="flashchat-stats-row">
                    <div class="flashchat-stat-item">
                        <div class="flashchat-stat-number">${stats.today.total_sent || 0}</div>
                        <div class="flashchat-stat-label">Today</div>
                    </div>
                    <div class="flashchat-stat-item">
                        <div class="flashchat-stat-number warning">${(stats.this_week.total_cost || 0).toFixed(2)}</div>
                        <div class="flashchat-stat-label">Week Cost</div>
                    </div>
                    <div class="flashchat-stat-item">
                        <div class="flashchat-stat-number">${calculate_success_rate(stats)}%</div>
                        <div class="flashchat-stat-label">Success Rate</div>
                    </div>
                </div>
                <div class="flashchat-widget-actions">
                    <a href="/app/flashchat-settings" class="flashchat-quick-action">
                        <i class="fa fa-cog"></i> Settings
                    </a>
                    <a href="/app/flashchat-message-log" class="flashchat-quick-action">
                        <i class="fa fa-list"></i> Message Logs
                    </a>
                    <button class="flashchat-quick-action primary" onclick="show_quick_send_dialog()">
                        <i class="fa fa-paper-plane"></i> Quick Send
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Find the best place to insert the widget
    const container = document.querySelector('.layout-main .page-content') || 
                     document.querySelector('.desk-body') ||
                     document.querySelector('.main-wrapper');
    
    if (container) {
        const widgetDiv = document.createElement('div');
        widgetDiv.innerHTML = widget_html;
        container.insertBefore(widgetDiv.firstElementChild, container.firstChild);
    }
}

function calculate_success_rate(stats) {
    const total = stats.this_week.total_sent || 0;
    const delivered = stats.this_week.total_delivered || 0;
    
    if (total === 0) return 0;
    return Math.round((delivered / total) * 100);
}

function show_quick_send_dialog() {
    let dialog = new frappe.ui.Dialog({
        title: __('Quick Send Message'),
        fields: [
            {
                fieldtype: 'Select',
                fieldname: 'message_type',
                label: __('Message Type'),
                options: 'SMS\nWhatsApp\nOTP',
                default: 'SMS',
                reqd: 1
            },
            {
                fieldtype: 'Data',
                fieldname: 'phone',
                label: __('Phone Number'),
                description: __('Include country code (e.g. +966501234567)'),
                reqd: 1
            },
            {
                fieldtype: 'Long Text',
                fieldname: 'message',
                label: __('Message'),
                depends_on: 'eval:doc.message_type != "OTP"'
            },
            {
                fieldtype: 'Select',
                fieldname: 'whatsapp_account',
                label: __('WhatsApp Account'),
                depends_on: 'eval:doc.message_type == "WhatsApp"'
            },
            {
                fieldtype: 'Int',
                fieldname: 'otp_expire',
                label: __('OTP Expiry (seconds)'),
                default: 300,
                depends_on: 'eval:doc.message_type == "OTP"'
            }
        ],
        primary_action_label: __('Send'),
        primary_action: function(values) {
            if (values.message_type === 'SMS') {
                send_quick_sms(values, dialog);
            } else if (values.message_type === 'WhatsApp') {
                send_quick_whatsapp(values, dialog);
            } else if (values.message_type === 'OTP') {
                send_quick_otp(values, dialog);
            }
        }
    });
    
    // Load WhatsApp accounts when dialog opens
    dialog.fields_dict.message_type.$input.on('change', function() {
        if (dialog.get_value('message_type') === 'WhatsApp') {
            load_whatsapp_accounts(dialog);
        }
    });
    
    dialog.show();
}

function load_whatsapp_accounts(dialog) {
    frappe.call({
        method: 'flashchat_integration.api.flashchat_api.get_whatsapp_accounts_api',
        callback: function(r) {
            if (r.message && r.message.success) {
                const accounts = r.message.data;
                const options = accounts.map(acc => acc.unique + ' - ' + acc.phone).join('\n');
                dialog.fields_dict.whatsapp_account.df.options = options;
                dialog.fields_dict.whatsapp_account.refresh();
            }
        }
    });
}

function send_quick_sms(values, dialog) {
    frappe.call({
        method: 'flashchat_integration.api.flashchat_api.send_sms_api',
        args: {
            phone: values.phone,
            message: values.message
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.show_alert({
                    message: __('SMS sent successfully'),
                    indicator: 'green'
                });
                dialog.hide();
                setTimeout(add_flashchat_dashboard_widget, 1000);
            } else {
                frappe.msgprint(__('Failed to send SMS: ') + (r.message.error || 'Unknown error'));
            }
        }
    });
}

function send_quick_whatsapp(values, dialog) {
    const account_id = values.whatsapp_account.split(' - ')[0];
    
    frappe.call({
        method: 'flashchat_integration.api.flashchat_api.send_whatsapp_api',
        args: {
            account: account_id,
            recipient: values.phone,
            message: values.message
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.show_alert({
                    message: __('WhatsApp message sent successfully'),
                    indicator: 'green'
                });
                dialog.hide();
                setTimeout(add_flashchat_dashboard_widget, 1000);
            } else {
                frappe.msgprint(__('Failed to send WhatsApp: ') + (r.message.error || 'Unknown error'));
            }
        }
    });
}

function send_quick_otp(values, dialog) {
    frappe.call({
        method: 'flashchat_integration.api.flashchat_api.send_otp_api',
        args: {
            phone: values.phone,
            expire: values.otp_expire || 300
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                const otp = r.message.data.otp_code;
                frappe.show_alert({
                    message: __('OTP sent successfully. OTP: ') + otp,
                    indicator: 'green'
                });
                dialog.hide();
                setTimeout(add_flashchat_dashboard_widget, 1000);
            } else {
                frappe.msgprint(__('Failed to send OTP: ') + (r.message.error || 'Unknown error'));
            }
        }
    });
}

// Auto-refresh widget every 5 minutes
setInterval(function() {
    if (document.querySelector('.flashchat-dashboard-widget')) {
        add_flashchat_dashboard_widget();
    }
}, 300000);