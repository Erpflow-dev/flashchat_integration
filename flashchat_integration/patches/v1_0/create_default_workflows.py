
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

def execute():
    """Create default workflow templates"""
    
    workflows = [
        {
            "workflow_name": "Order Confirmation SMS",
            "workflow_type": "Event Based",
            "trigger_doctype": "Sales Order",
            "trigger_event": "on_submit",
            "message_type": "SMS",
            "recipient_field": "contact_mobile",
            "fallback_recipient": "",
            "custom_message": "Dear {customer_name}, your order {name} for {currency} {grand_total} has been confirmed. Order will be processed shortly. Thank you for choosing {company_name}!",
            "conditions": "doc.docstatus == 1 and doc.contact_mobile",
            "is_active": 1,
            "retry_attempts": 3,
            "enable_logging": 1,
            "rate_limit_check": 1,
            "respect_dnd": 1
        },
        {
            "workflow_name": "Payment Received Notification",
            "workflow_type": "Event Based", 
            "trigger_doctype": "Payment Entry",
            "trigger_event": "on_submit",
            "message_type": "SMS",
            "recipient_field": "contact_mobile",
            "custom_message": "Dear {party_name}, we have received your payment of {currency} {paid_amount} for {reference_no}. Thank you!",
            "conditions": "doc.docstatus == 1 and doc.payment_type == 'Receive' and doc.contact_mobile",
            "is_active": 1,
            "retry_attempts": 2,
            "enable_logging": 1
        },
        {
            "workflow_name": "Delivery Notification WhatsApp",
            "workflow_type": "Event Based",
            "trigger_doctype": "Delivery Note", 
            "trigger_event": "on_submit",
            "message_type": "WhatsApp",
            "recipient_field": "contact_mobile",
            "custom_message": "🚚 Hi {customer_name}! Your order {name} has been delivered successfully. We hope you enjoy your purchase! 😊\n\nThank you for choosing {company_name}.",
            "conditions": "doc.docstatus == 1 and doc.contact_mobile",
            "is_active": 1,
            "delay_duration": 30,
            "delay_unit": "Minutes",
            "enable_logging": 1
        },
        {
            "workflow_name": "Lead Follow-up SMS",
            "workflow_type": "Event Based",
            "trigger_doctype": "Lead",
            "trigger_event": "after_insert", 
            "message_type": "SMS",
            "recipient_field": "mobile_no",
            "custom_message": "Hi {lead_name}, thank you for your interest in {company_name}. Our team will contact you shortly to discuss your requirements.",
            "conditions": "doc.mobile_no and doc.status == 'Lead'",
            "is_active": 1,
            "delay_duration": 5,
            "delay_unit": "Minutes",
            "enable_logging": 1
        },
        {
            "workflow_name": "Invoice Overdue Reminder",
            "workflow_type": "Scheduled",
            "trigger_doctype": "Sales Invoice",
            "message_type": "SMS", 
            "recipient_field": "contact_mobile",
            "custom_message": "Dear {customer_name}, your invoice {name} due on {due_date} is overdue. Amount: {currency} {outstanding_amount}. Please make payment at your earliest convenience.",
            "conditions": "doc.docstatus == 1 and doc.outstanding_amount > 0 and frappe.utils.getdate(doc.due_date) < frappe.utils.getdate()",
            "is_active": 0,  # Disabled by default
            "working_hours_only": 1,
            "respect_dnd": 1,
            "enable_logging": 1
        },
        {
            "workflow_name": "Welcome New Customer",
            "workflow_type": "Event Based",
            "trigger_doctype": "Customer",
            "trigger_event": "after_insert",
            "message_type": "WhatsApp",
            "recipient_field": "mobile_no",
            "custom_message": "🎉 Welcome to {company_name}, {customer_name}! We're excited to serve you. For any assistance, feel free to contact us. Thank you for choosing us!",
            "conditions": "doc.mobile_no",
            "is_active": 1,
            "delay_duration": 1,
            "delay_unit": "Hours", 
            "enable_logging": 1
        },
        {
            "workflow_name": "Quotation Follow-up",
            "workflow_type": "Event Based",
            "trigger_doctype": "Quotation",
            "trigger_event": "on_submit",
            "message_type": "SMS",
            "recipient_field": "contact_mobile",
            "custom_message": "Hi {customer_name}, we've sent you a quotation {name} for {currency} {grand_total}. Valid until {valid_till}. Contact us for any questions!",
            "conditions": "doc.docstatus == 1 and doc.contact_mobile",
            "is_active": 1,
            "delay_duration": 2,
            "delay_unit": "Hours",
            "enable_logging": 1
        },
        {
            "workflow_name": "Appointment Reminder",
            "workflow_type": "Scheduled",
            "trigger_doctype": "Event",
            "message_type": "SMS",
            "recipient_field": "contact_mobile", 
            "custom_message": "Reminder: You have an appointment '{subject}' scheduled for {starts_on} at {location}. See you soon!",
            "conditions": "doc.event_type == 'Public' and doc.contact_mobile and frappe.utils.get_datetime(doc.starts_on) > frappe.utils.now_datetime()",
            "is_active": 0,  # Disabled by default
            "delay_duration": -24,  # 24 hours before
            "delay_unit": "Hours",
            "enable_logging": 1
        }
    ]
    
    for workflow_data in workflows:
        if not frappe.db.exists("FlashChat Workflow", workflow_data["workflow_name"]):
            try:
                workflow = frappe.get_doc({
                    "doctype": "FlashChat Workflow",
                    **workflow_data
                })
                workflow.insert(ignore_permissions=True)
                print(f"Created workflow: {workflow_data['workflow_name']}")
            except Exception as e:
                print(f"Failed to create workflow {workflow_data['workflow_name']}: {str(e)}")
    
    frappe.db.commit()
    print("Default workflows created successfully")
