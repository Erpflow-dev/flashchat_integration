### Additional Patch: flashchat_integration/patches/v1_0/create_default_templates.py

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

def execute():
    """Create default message templates"""
    
    templates = [
        {
            'template_name': 'Order Confirmation',
            'message_type': 'SMS',
            'description': 'SMS sent when sales order is confirmed',
            'template_content': 'Dear {customer_name}, your order {order_id} for {amount} has been confirmed. Thank you for choosing {company_name}!'
        },
        {
            'template_name': 'Delivery Notification',
            'message_type': 'WhatsApp',
            'description': 'WhatsApp message sent when order is delivered',
            'template_content': 'Hi {customer_name}! 🚚 Your order {order_id} has been delivered successfully. Thank you for shopping with {company_name}!'
        },
        {
            'template_name': 'Payment Reminder',
            'message_type': 'SMS',
            'description': 'SMS reminder for overdue payments',
            'template_content': 'Dear {customer_name}, invoice {invoice_number} due on {due_date} is overdue. Please make payment at your earliest convenience.'
        },
        {
            'template_name': 'Welcome Message',
            'message_type': 'WhatsApp',
            'description': 'Welcome message for new customers',
            'template_content': 'Welcome to {company_name}, {customer_name}! 🎉 We\'re excited to serve you. For any assistance, feel free to contact us.'
        },
        {
            'template_name': 'Appointment Reminder',
            'message_type': 'SMS',
            'description': 'Reminder for upcoming appointments',
            'template_content': 'Hi {customer_name}, this is a reminder for your appointment scheduled on {date}. See you soon!'
        }
    ]
    
    for template_data in templates:
        if not frappe.db.exists('Message Template', template_data['template_name']):
            template = frappe.get_doc({
                'doctype': 'Message Template',
                **template_data
            })
            template.insert(ignore_permissions=True)
            print(f"Created template: {template_data['template_name']}")
    
    frappe.db.commit()
    print("Default message templates created successfully")
