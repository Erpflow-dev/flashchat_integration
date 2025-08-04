# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    """Setup custom fields for FlashChat integration"""
    
    custom_fields = {
        "Contact": [
            {
                "fieldname": "flashchat_section",
                "label": "FlashChat Integration",
                "fieldtype": "Section Break",
                "insert_after": "mobile_no",
                "collapsible": 1
            },
            {
                "fieldname": "flashchat_id",
                "label": "FlashChat ID",
                "fieldtype": "Data",
                "read_only": 1,
                "insert_after": "flashchat_section",
                "description": "Unique ID assigned by FlashChat service"
            },
            {
                "fieldname": "flashchat_sync_status",
                "label": "Sync Status",
                "fieldtype": "Select",
                "options": "\nPending\nSynced\nFailed",
                "default": "Pending",
                "insert_after": "flashchat_id",
                "description": "Status of contact synchronization with FlashChat"
            },
            {
                "fieldname": "flashchat_column_break",
                "fieldtype": "Column Break",
                "insert_after": "flashchat_sync_status"
            },
            {
                "fieldname": "flashchat_last_sync",
                "label": "Last Sync",
                "fieldtype": "Datetime",
                "read_only": 1,
                "insert_after": "flashchat_column_break",
                "description": "Last successful synchronization timestamp"
            },
            {
                "fieldname": "flashchat_sync_error",
                "label": "Sync Error",
                "fieldtype": "Text",
                "read_only": 1,
                "insert_after": "flashchat_last_sync",
                "depends_on": "eval:doc.flashchat_sync_status == 'Failed'",
                "description": "Error message if sync failed"
            }
        ],
        "Customer": [
            {
                "fieldname": "flashchat_section",
                "label": "FlashChat Integration",
                "fieldtype": "Section Break",
                "insert_after": "mobile_no",
                "collapsible": 1
            },
            {
                "fieldname": "flashchat_id",
                "label": "FlashChat ID",
                "fieldtype": "Data",
                "read_only": 1,
                "insert_after": "flashchat_section",
                "description": "Unique ID assigned by FlashChat service"
            },
            {
                "fieldname": "flashchat_sync_status",
                "label": "Sync Status",
                "fieldtype": "Select",
                "options": "\nPending\nSynced\nFailed",
                "default": "Pending",
                "insert_after": "flashchat_id"
            },
            {
                "fieldname": "flashchat_column_break",
                "fieldtype": "Column Break",
                "insert_after": "flashchat_sync_status"
            },
            {
                "fieldname": "flashchat_last_sync",
                "label": "Last Sync",
                "fieldtype": "Datetime",
                "read_only": 1,
                "insert_after": "flashchat_column_break"
            },
            {
                "fieldname": "flashchat_marketing_consent",
                "label": "Marketing Consent",
                "fieldtype": "Check",
                "insert_after": "flashchat_last_sync",
                "description": "Customer has consented to receive marketing messages"
            }
        ],
        "Lead": [
            {
                "fieldname": "flashchat_section",
                "label": "FlashChat Integration",
                "fieldtype": "Section Break",
                "insert_after": "mobile_no",
                "collapsible": 1
            },
            {
                "fieldname": "flashchat_id",
                "label": "FlashChat ID",
                "fieldtype": "Data",
                "read_only": 1,
                "insert_after": "flashchat_section",
                "description": "Unique ID assigned by FlashChat service"
            },
            {
                "fieldname": "flashchat_sync_status",
                "label": "Sync Status",
                "fieldtype": "Select",
                "options": "\nPending\nSynced\nFailed",
                "default": "Pending",
                "insert_after": "flashchat_id"
            },
            {
                "fieldname": "flashchat_column_break",
                "fieldtype": "Column Break",
                "insert_after": "flashchat_sync_status"
            },
            {
                "fieldname": "flashchat_last_sync",
                "label": "Last Sync",
                "fieldtype": "Datetime",
                "read_only": 1,
                "insert_after": "flashchat_column_break"
            },
            {
                "fieldname": "flashchat_lead_source_campaign",
                "label": "Source Campaign",
                "fieldtype": "Link",
                "options": "FlashChat Campaign",
                "insert_after": "flashchat_last_sync",
                "description": "FlashChat campaign that generated this lead"
            }
        ],
        "Sales Order": [
            {
                "fieldname": "flashchat_section",
                "label": "FlashChat Notifications",
                "fieldtype": "Section Break",
                "insert_after": "contact_mobile",
                "collapsible": 1
            },
            {
                "fieldname": "flashchat_send_confirmation",
                "label": "Send Order Confirmation",
                "fieldtype": "Check",
                "default": 1,
                "insert_after": "flashchat_section",
                "description": "Send SMS/WhatsApp confirmation when order is submitted"
            },
            {
                "fieldname": "flashchat_confirmation_sent",
                "label": "Confirmation Sent",
                "fieldtype": "Check",
                "read_only": 1,
                "insert_after": "flashchat_send_confirmation"
            },
            {
                "fieldname": "flashchat_column_break",
                "fieldtype": "Column Break",
                "insert_after": "flashchat_confirmation_sent"
            },
            {
                "fieldname": "flashchat_confirmation_message_id",
                "label": "Confirmation Message ID",
                "fieldtype": "Data",
                "read_only": 1,
                "insert_after": "flashchat_column_break",
                "description": "FlashChat message ID for order confirmation"
            }
        ],
        "Delivery Note": [
            {
                "fieldname": "flashchat_section",
                "label": "FlashChat Notifications",
                "fieldtype": "Section Break",
                "insert_after": "contact_mobile",
                "collapsible": 1
            },
            {
                "fieldname": "flashchat_send_delivery_notification",
                "label": "Send Delivery Notification",
                "fieldtype": "Check",
                "default": 1,
                "insert_after": "flashchat_section",
                "description": "Send SMS/WhatsApp notification when delivered"
            },
            {
                "fieldname": "flashchat_notification_sent",
                "label": "Notification Sent",
                "fieldtype": "Check",
                "read_only": 1,
                "insert_after": "flashchat_send_delivery_notification"
            },
            {
                "fieldname": "flashchat_column_break",
                "fieldtype": "Column Break",
                "insert_after": "flashchat_notification_sent"
            },
            {
                "fieldname": "flashchat_notification_message_id",
                "label": "Notification Message ID",
                "fieldtype": "Data",
                "read_only": 1,
                "insert_after": "flashchat_column_break"
            }
        ],
        "Sales Invoice": [
            {
                "fieldname": "flashchat_section",
                "label": "FlashChat Notifications",
                "fieldtype": "Section Break",
                "insert_after": "contact_mobile",
                "collapsible": 1
            },
            {
                "fieldname": "flashchat_send_invoice_notification",
                "label": "Send Invoice Notification",
                "fieldtype": "Check",
                "insert_after": "flashchat_section",
                "description": "Send SMS/WhatsApp when invoice is submitted"
            },
            {
                "fieldname": "flashchat_send_payment_reminder",
                "label": "Send Payment Reminder",
                "fieldtype": "Check",
                "insert_after": "flashchat_send_invoice_notification",
                "description": "Send payment reminder for overdue invoices"
            },
            {
                "fieldname": "flashchat_column_break",
                "fieldtype": "Column Break",
                "insert_after": "flashchat_send_payment_reminder"
            },
            {
                "fieldname": "flashchat_invoice_notification_sent",
                "label": "Invoice Notification Sent",
                "fieldtype": "Check",
                "read_only": 1,
                "insert_after": "flashchat_column_break"
            },
            {
                "fieldname": "flashchat_payment_reminder_sent",
                "label": "Payment Reminder Sent",
                "fieldtype": "Check",
                "read_only": 1,
                "insert_after": "flashchat_invoice_notification_sent"
            }
        ],
        "Payment Entry": [
            {
                "fieldname": "flashchat_section",
                "label": "FlashChat Notifications",
                "fieldtype": "Section Break",
                "insert_after": "contact_mobile",
                "collapsible": 1
            },
            {
                "fieldname": "flashchat_send_payment_confirmation",
                "label": "Send Payment Confirmation",
                "fieldtype": "Check",
                "insert_after": "flashchat_section",
                "description": "Send SMS/WhatsApp payment confirmation"
            },
            {
                "fieldname": "flashchat_confirmation_sent",
                "label": "Confirmation Sent",
                "fieldtype": "Check",
                "read_only": 1,
                "insert_after": "flashchat_send_payment_confirmation"
            },
            {
                "fieldname": "flashchat_column_break",
                "fieldtype": "Column Break",
                "insert_after": "flashchat_confirmation_sent"
            },
            {
                "fieldname": "flashchat_confirmation_message_id",
                "label": "Confirmation Message ID",
                "fieldtype": "Data",
                "read_only": 1,
                "insert_after": "flashchat_column_break"
            }
        ]
    }
    
    try:
        # Create custom fields
        create_custom_fields(custom_fields, update=True)
        
        # Log successful creation
        frappe.logger().info("FlashChat custom fields created successfully")
        
        # Create property setters for better field organization
        create_property_setters()
        
        print("FlashChat Integration: Custom fields setup completed successfully")
        
    except Exception as e:
        frappe.logger().error(f"Error creating FlashChat custom fields: {str(e)}")
        print(f"FlashChat Integration: Error setting up custom fields - {str(e)}")
        raise

def create_property_setters():
    """Create property setters for field customizations"""
    
    property_setters = [
        # Contact customizations
        {
            "doctype": "Contact",
            "property": "depends_on",
            "field_name": "flashchat_section",
            "value": "eval:doc.mobile_no"
        },
        
        # Customer customizations
        {
            "doctype": "Customer",
            "property": "depends_on", 
            "field_name": "flashchat_section",
            "value": "eval:doc.mobile_no"
        },
        
        # Lead customizations
        {
            "doctype": "Lead",
            "property": "depends_on",
            "field_name": "flashchat_section", 
            "value": "eval:doc.mobile_no"
        },
        
        # Sales Order customizations
        {
            "doctype": "Sales Order",
            "property": "depends_on",
            "field_name": "flashchat_section",
            "value": "eval:doc.contact_mobile"
        }
    ]
    
    for prop in property_setters:
        try:
            # Check if property setter already exists
            existing = frappe.db.get_value(
                "Property Setter",
                {
                    "doc_type": prop["doctype"],
                    "field_name": prop["field_name"],
                    "property": prop["property"]
                },
                "name"
            )
            
            if not existing:
                property_setter = frappe.get_doc({
                    "doctype": "Property Setter",
                    "doc_type": prop["doctype"],
                    "field_name": prop["field_name"],
                    "property": prop["property"],
                    "value": prop["value"],
                    "property_type": "Text"
                })
                property_setter.insert(ignore_permissions=True)
                
        except Exception as e:
            frappe.logger().error(f"Error creating property setter: {str(e)}")
            continue

def create_custom_scripts():
    """Create custom client scripts for FlashChat integration"""
    
    scripts = [
        {
            "dt": "Contact",
            "script_type": "Client",
            "script": """
frappe.ui.form.on('Contact', {
    refresh: function(frm) {
        if (frm.doc.mobile_no && !frm.doc.__islocal) {
            // Add FlashChat sync button
            frm.add_custom_button(__('Sync to FlashChat'), function() {
                frappe.call({
                    method: 'flashchat_integration.utils.sync_contact_manually',
                    args: {
                        contact_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frappe.msgprint(__('Contact synced successfully'));
                            frm.reload_doc();
                        } else {
                            frappe.msgprint(__('Sync failed: ') + (r.message.error || 'Unknown error'));
                        }
                    }
                });
            }, __('FlashChat'));
        }
        
        // Show sync status indicator
        if (frm.doc.flashchat_sync_status) {
            let color = {
                'Synced': 'green',
                'Failed': 'red', 
                'Pending': 'orange'
            }[frm.doc.flashchat_sync_status] || 'gray';
            
            frm.dashboard.add_indicator(__('FlashChat: {0}', [frm.doc.flashchat_sync_status]), color);
        }
    }
});
            """
        }
    ]
    
    for script in scripts:
        try:
            existing = frappe.db.get_value(
                "Client Script",
                {
                    "dt": script["dt"],
                    "script_type": script["script_type"]
                },
                "name"
            )
            
            if not existing:
                client_script = frappe.get_doc({
                    "doctype": "Client Script",
                    "dt": script["dt"],
                    "script_type": script["script_type"],
                    "script": script["script"],
                    "enabled": 1
                })
                client_script.insert(ignore_permissions=True)
                
        except Exception as e:
            frappe.logger().error(f"Error creating client script: {str(e)}")
            continue

def add_custom_permissions():
    """Add custom permissions for FlashChat doctypes"""
    
    permissions = [
        {
            "doctype": "FlashChat Message Log",
            "role": "Sales User",
            "permlevel": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0
        },
        {
            "doctype": "FlashChat Campaign", 
            "role": "Sales User",
            "permlevel": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0
        },
        {
            "doctype": "FlashChat Settings",
            "role": "Sales Manager",
            "permlevel": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0
        }
    ]
    
    for perm in permissions:
        try:
            # Check if permission already exists
            existing = frappe.db.get_value(
                "Custom DocPerm",
                {
                    "parent": perm["doctype"],
                    "role": perm["role"],
                    "permlevel": perm["permlevel"]
                },
                "name"
            )
            
            if not existing:
                doc_perm = frappe.get_doc({
                    "doctype": "Custom DocPerm",
                    "parent": perm["doctype"],
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    **perm
                })
                doc_perm.insert(ignore_permissions=True)
                
        except Exception as e:
            frappe.logger().error(f"Error creating custom permission: {str(e)}")
            continue

if __name__ == "__main__":
    execute()