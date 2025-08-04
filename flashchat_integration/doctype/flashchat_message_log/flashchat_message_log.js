// flashchat_integration/doctype/flashchat_message_log/flashchat_message_log.js
frappe.ui.form.on('FlashChat Message Log', {
    refresh: function(frm) {
        // Add retry button for failed messages
        if (frm.doc.status === 'Failed' && frm.doc.message_type !== 'OTP') {
            frm.add_custom_button(__('Retry Send'), function() {
                retry_send_message(frm);
            });
        }
        
        // Add view reference button
        if (frm.doc.reference_doctype && frm.doc.reference_name) {
            frm.add_custom_button(__('View Reference'), function() {
                frappe.set_route('Form', frm.doc.reference_doctype, frm.doc.reference_name);
            });
        }
        
        // Add status indicator
        add_status_indicator(frm);
        
        // Show delivery info
        if (frm.doc.delivered_at) {
            frm.add_custom_button(__('Delivery Info'), function() {
                show_delivery_info(frm);
            }, __('Info'));
        }
        
        // Show response data
        if (frm.doc.response_data) {
            frm.add_custom_button(__('API Response'), function() {
                show_api_response(frm);
            }, __('Info'));
        }
    },
    
    phone_number: function(frm) {
        // Auto-format phone number
        if (frm.doc.phone_number && !frm.doc.phone_number.startsWith('+')) {
            frappe.msgprint(__('Phone number should start with country code (+)'));
        }
    }
});

function retry_send_message(frm) {
    frappe.confirm(
        __('Are you sure you want to retry sending this message?'),
        function() {
            let method;
            let args = {
                phone: frm.doc.phone_number,
                message: frm.doc.message_content,
                reference_doctype: frm.doc.reference_doctype,
                reference_name: frm.doc.reference_name
            };
            
            if (frm.doc.message_type === 'SMS') {
                method = 'flashchat_integration.api.flashchat_api.send_sms_api';
                if (frm.doc.sim_used) {
                    args.sim = frm.doc.sim_used;
                }
            } else if (frm.doc.message_type === 'WhatsApp') {
                method = 'flashchat_integration.api.flashchat_api.send_whatsapp_api';
                args.account = frm.doc.whatsapp_unique_id;
                args.recipient = args.phone;
                delete args.phone;
            }
            
            frappe.call({
                method: method,
                args: args,
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: __('Message sent successfully'),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    } else {
                        frappe.msgprint(__('Failed to send message: ') + (r.message.error || 'Unknown error'));
                    }
                }
            });
        }
    );
}

function add_status_indicator(frm) {
    const status = frm.doc.status;
    let indicator_class = 'blue';
    
    switch(status) {
        case 'Sent':
            indicator_class = 'green';
            break;
        case 'Delivered':
            indicator_class = 'darkgreen';
            break;
        case 'Failed':
            indicator_class = 'red';
            break;
        case 'Pending':
            indicator_class = 'orange';
            break;
    }
    
    frm.dashboard.add_indicator(__('Status: {0}', [status]), indicator_class);
}

function show_delivery_info(frm) {
    const sent_time = frm.doc.sent_at ? frappe.datetime.str_to_user(frm.doc.sent_at) : 'N/A';
    const delivered_time = frm.doc.delivered_at ? frappe.datetime.str_to_user(frm.doc.delivered_at) : 'N/A';
    
    const info_html = `
        <table class="table table-bordered">
            <tr><td><strong>Sent At:</strong></td><td>${sent_time}</td></tr>
            <tr><td><strong>Delivered At:</strong></td><td>${delivered_time}</td></tr>
            <tr><td><strong>Phone:</strong></td><td>${frm.doc.phone_number}</td></tr>
            <tr><td><strong>Cost:</strong></td><td>${frm.doc.cost || 'N/A'}</td></tr>
            <tr><td><strong>Retry Count:</strong></td><td>${frm.doc.retry_count || 0}</td></tr>
        </table>
    `;
    
    frappe.msgprint({
        title: __('Delivery Information'),
        message: info_html,
        wide: true
    });
}

function show_api_response(frm) {
    if (frm.doc.response_data) {
        try {
            const response = JSON.parse(frm.doc.response_data);
            const formatted = JSON.stringify(response, null, 2);
            
            frappe.msgprint({
                title: __('API Response'),
                message: `<pre>${formatted}</pre>`,
                wide: true
            });
        } catch (e) {
            frappe.msgprint({
                title: __('API Response'),
                message: `<pre>${frm.doc.response_data}</pre>`,
                wide: true
            });
        }
    }
}