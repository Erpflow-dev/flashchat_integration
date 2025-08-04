
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _

def before_install():
    """Runs before installing the app"""
    # Check ERPNext version compatibility
    if not hasattr(frappe, 'get_version'):
        frappe.throw(_("FlashChat Integration requires ERPNext v13 or higher"))

def after_install():
    """Runs after installing the app"""
    # Create default FlashChat Settings
    create_default_settings()
    
    # Add custom fields
    add_custom_fields()
    
    # Create sample data
    create_sample_data()

def create_default_settings():
    """Create default FlashChat Settings document"""
    if not frappe.db.exists("FlashChat Settings", "FlashChat Settings"):
        settings = frappe.get_doc({
            "doctype": "FlashChat Settings",
            "name": "FlashChat Settings",
            "settings_name": "FlashChat Settings",
            "base_url": "https://flashchat.xyz/api",
            "sms_rate_limit": 100,
            "whatsapp_rate_limit": 50,
            "otp_rate_limit": 20,
            "auto_sync_contacts": 1,
            "enable_webhooks": 1
        })
        settings.insert(ignore_permissions=True)
        frappe.db.commit()

def add_custom_fields():
    """Add custom fields to existing doctypes"""
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    
    custom_fields = {
        "Contact": [
            {
                "fieldname": "flashchat_id",
                "label": "FlashChat ID",
                "fieldtype": "Data",
                "read_only": 1,
                "insert_after": "mobile_no"
            },
            {
                "fieldname": "flashchat_sync_status",
                "label": "FlashChat Sync Status",
                "fieldtype": "Select",
                "options": "\nPending\nSynced\nFailed",
                "default": "Pending",
                "insert_after": "flashchat_id"
            }
        ],
        "Customer": [
            {
                "fieldname": "flashchat_id",
                "label": "FlashChat ID",
                "fieldtype": "Data",
                "read_only": 1,
                "insert_after": "mobile_no"
            }
        ],
        "Lead": [
            {
                "fieldname": "flashchat_id",
                "label": "FlashChat ID",
                "fieldtype": "Data",
                "read_only": 1,
                "insert_after": "mobile_no"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)

def create_sample_data():
    """Create sample message templates"""
    templates = [
        {
            "template_name": "Order Confirmation",
            "template_content": "Dear {customer_name}, your order {order_id} for {amount} has been confirmed. Thank you!",
            "message_type": "SMS"
        },
        {
            "template_name": "Delivery Notification",
            "template_content": "Hi {customer_name}, your order {order_id} has been delivered. Thank you for choosing us!",
            "message_type": "WhatsApp"
        }
    ]
    
    for template in templates:
        if not frappe.db.exists("Message Template", template["template_name"]):
            doc = frappe.get_doc({
                "doctype": "Message Template",
                **template
            })
            doc.insert(ignore_permissions=True)
    
    frappe.db.commit()


