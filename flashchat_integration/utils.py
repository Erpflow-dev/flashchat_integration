## 12. flashchat_integration/utils.py

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import now, add_to_date
from .api import FlashChatAPI

def sync_contact_to_flashchat(doc, method):
    """Sync contact to FlashChat when created/updated"""
    settings = frappe.get_single("FlashChat Settings")
    
    if not settings.auto_sync_contacts or not doc.mobile_no:
        return
    
    try:
        # Add to sync queue or sync immediately
        sync_contact_data = {
            "name": doc.get_full_name(),
            "phone": doc.mobile_no,
            "email": doc.email_id,
            "company": doc.company
        }
        
        # Log sync attempt
        frappe.log_error(
            f"Contact sync initiated for {doc.name}: {sync_contact_data}",
            "FlashChat Contact Sync"
        )
        
        # Update sync status
        frappe.db.set_value("Contact", doc.name, "flashchat_sync_status", "Synced")
        
    except Exception as e:
        frappe.log_error(f"Contact sync failed for {doc.name}: {str(e)}", "FlashChat Contact Sync Error")
        frappe.db.set_value("Contact", doc.name, "flashchat_sync_status", "Failed")

def sync_customer_to_flashchat(doc, method):
    """Sync customer to FlashChat when created/updated"""
    settings = frappe.get_single("FlashChat Settings")
    
    if not settings.auto_sync_contacts or not doc.mobile_no:
        return
    
    try:
        sync_customer_data = {
            "name": doc.customer_name,
            "phone": doc.mobile_no,
            "customer_group": doc.customer_group,
            "territory": doc.territory
        }
        
        frappe.log_error(
            f"Customer sync initiated for {doc.name}: {sync_customer_data}",
            "FlashChat Customer Sync"
        )
        
    except Exception as e:
        frappe.log_error(f"Customer sync failed for {doc.name}: {str(e)}", "FlashChat Customer Sync Error")

def sync_lead_to_flashchat(doc, method):
    """Sync lead to FlashChat when created/updated"""
    settings = frappe.get_single("FlashChat Settings")
    
    if not settings.auto_sync_contacts or not doc.mobile_no:
        return
    
    try:
        sync_lead_data = {
            "name": doc.lead_name,
            "phone": doc.mobile_no,
            "email": doc.email_id,
            "source": doc.source,
            "status": doc.status
        }
        
        frappe.log_error(
            f"Lead sync initiated for {doc.name}: {sync_lead_data}",
            "FlashChat Lead Sync"
        )
        
    except Exception as e:
        frappe.log_error(f"Lead sync failed for {doc.name}: {str(e)}", "FlashChat Lead Sync Error")

def send_order_confirmation(doc, method):
    """Send order confirmation SMS/WhatsApp"""
    settings = frappe.get_single("FlashChat Settings")
    
    if not settings.enable_order_notifications:
        return
    
    # Get customer mobile number
    mobile_no = None
    if doc.contact_mobile:
        mobile_no = doc.contact_mobile
    elif doc.customer:
        customer = frappe.get_doc("Customer", doc.customer)
        mobile_no = customer.mobile_no
    
    if not mobile_no:
        return
    
    try:
        api = FlashChatAPI()
        
        message = f"Dear {doc.customer_name}, your order {doc.name} for {doc.currency} {doc.grand_total} has been confirmed. Thank you!"
        
        result = api.send_sms(
            phone=mobile_no,
            message=message,
            reference_doctype="Sales Order",
            reference_name=doc.name
        )
        
        frappe.msgprint(_("Order confirmation sent successfully"))
        
    except Exception as e:
        frappe.log_error(f"Order confirmation failed for {doc.name}: {str(e)}", "FlashChat Order Confirmation")

def send_order_cancellation(doc, method):
    """Send order cancellation notification"""
    settings = frappe.get_single("FlashChat Settings")
    
    if not settings.enable_order_notifications:
        return
    
    # Get customer mobile number
    mobile_no = None
    if doc.contact_mobile:
        mobile_no = doc.contact_mobile
    elif doc.customer:
        customer = frappe.get_doc("Customer", doc.customer)
        mobile_no = customer.mobile_no
    
    if not mobile_no:
        return
    
    try:
        api = FlashChatAPI()
        
        message = f"Dear {doc.customer_name}, your order {doc.name} has been cancelled. If you have any questions, please contact us."
        
        result = api.send_sms(
            phone=mobile_no,
            message=message,
            reference_doctype="Sales Order",
            reference_name=doc.name
        )
        
    except Exception as e:
        frappe.log_error(f"Order cancellation notification failed for {doc.name}: {str(e)}", "FlashChat Order Cancellation")

def send_delivery_notification(doc, method):
    """Send delivery notification"""
    settings = frappe.get_single("FlashChat Settings")
    
    if not settings.enable_delivery_notifications:
        return
    
    # Get customer mobile number
    mobile_no = None
    customer = frappe.get_doc("Customer", doc.customer)
    mobile_no = customer.mobile_no
    
    if not mobile_no:
        return
    
    try:
        api = FlashChatAPI()
        
        message = f"Hi {customer.customer_name}, your order {doc.name} has been delivered. Thank you for choosing us!"
        
        # Try WhatsApp first, fallback to SMS
        try:
            accounts = api.get_whatsapp_accounts()
            if accounts.get("success") and accounts.get("accounts"):
                account_id = accounts["accounts"][0]["id"]
                result = api.send_whatsapp(
                    account=account_id,
                    recipient=mobile_no,
                    message=message,
                    reference_doctype="Delivery Note",
                    reference_name=doc.name
                )
            else:
                raise Exception("No WhatsApp accounts available")
        except:
            # Fallback to SMS
            result = api.send_sms(
                phone=mobile_no,
                message=message,
                reference_doctype="Delivery Note",
                reference_name=doc.name
            )
        
    except Exception as e:
        frappe.log_error(f"Delivery notification failed for {doc.name}: {str(e)}", "FlashChat Delivery Notification")

def sync_message_status():
    """Scheduled task to sync message status"""
    # Get pending messages from last 24 hours
    pending_messages = frappe.get_all(
        "FlashChat Message Log",
        filters={
            "status": "Sent",
            "sent_at": [">=", add_to_date(now(), days=-1)]
        },
        fields=["name", "flashchat_message_id"]
    )
    
    # TODO: Implement status sync logic
    for message in pending_messages:
        try:
            # Call FlashChat API to get message status
            # Update status in FlashChat Message Log
            pass
        except Exception as e:
            frappe.log_error(f"Status sync failed for {message.name}: {str(e)}", "FlashChat Status Sync")

def process_pending_campaigns():
    """Process pending campaigns"""
    # Get scheduled campaigns
    campaigns = frappe.get_all(
        "FlashChat Campaign",
        filters={
            "status": "Scheduled",
            "send_at": ["<=", now()]
        },
        fields=["name"]
    )
    
    for campaign in campaigns:
        try:
            # TODO: Implement campaign processing
            campaign_doc = frappe.get_doc("FlashChat Campaign", campaign.name)
            # Process campaign
            campaign_doc.status = "Processing"
            campaign_doc.save()
        except Exception as e:
            frappe.log_error(f"Campaign processing failed for {campaign.name}: {str(e)}", "FlashChat Campaign Processing")

def cleanup_old_logs():
    """Cleanup old message logs"""
    settings = frappe.get_single("FlashChat Settings")
    retention_days = settings.log_retention_days or 90
    
    cutoff_date = add_to_date(now(), days=-retention_days)
    
    # Delete old logs
    frappe.db.delete("FlashChat Message Log", {
        "sent_at": ["<", cutoff_date]
    })
    
    frappe.db.commit()

def sync_all_contacts():
    """Sync all contacts to FlashChat"""
    settings = frappe.get_single("FlashChat Settings")
    
    if not settings.auto_sync_contacts:
        return
    
    # Get contacts with mobile numbers that need syncing
    contacts = frappe.get_all(
        "Contact",
        filters={
            "mobile_no": ["!=", ""],
            "flashchat_sync_status": ["in", ["Pending", "Failed"]]
        },
        fields=["name", "mobile_no"]
    )
    
    for contact in contacts:
        try:
            contact_doc = frappe.get_doc("Contact", contact.name)
            sync_contact_to_flashchat(contact_doc, "sync_all")
        except Exception as e:
            frappe.log_error(f"Contact sync failed for {contact.name}: {str(e)}", "FlashChat Contact Sync")

def generate_weekly_report():
    """Generate weekly messaging report"""
    # TODO: Implement weekly report generation
    pass

@frappe.whitelist()
def get_dashboard_data():
    """Get dashboard data for FlashChat widget"""
    # Messages sent this week
    week_start = add_to_date(now(), days=-7)
    
    data = {
        "messages_this_week": frappe.db.count(
            "FlashChat Message Log",
            {"sent_at": [">=", week_start]}
        ),
        "sms_sent": frappe.db.count(
            "FlashChat Message Log",
            {
                "message_type": "SMS",
                "sent_at": [">=", week_start],
                "status": ["in", ["Sent", "Delivered"]]
            }
        ),
        "whatsapp_sent": frappe.db.count(
            "FlashChat Message Log",
            {
                "message_type": "WhatsApp",
                "sent_at": [">=", week_start],
                "status": ["in", ["Sent", "Delivered"]]
            }
        ),
        "failed_messages": frappe.db.count(
            "FlashChat Message Log",
            {
                "sent_at": [">=", week_start],
                "status": "Failed"
            }
        )
    }
    
    # Calculate success rate
    total_messages = data["messages_this_week"]
    successful_messages = data["sms_sent"] + data["whatsapp_sent"]
    
    if total_messages > 0:
        data["success_rate"] = round((successful_messages / total_messages) * 100, 2)
    else:
        data["success_rate"] = 0
    
    return data

    
# Add to existing utils.py

def get_workflow_stats():
    """Get workflow statistics for dashboard"""
    today = frappe.utils.today()
    
    stats = {
        "active_workflows": frappe.db.count("FlashChat Workflow", {"is_active": 1}),
        "total_workflows": frappe.db.count("FlashChat Workflow"),
        "executions_today": frappe.db.count("FlashChat Workflow Log", {
            "execution_time": [">=", today]
        }),
        "success_today": frappe.db.count("FlashChat Workflow Log", {
            "execution_time": [">=", today],
            "status": "Success"
        })
    }
    
    if stats["executions_today"] > 0:
        stats["success_rate"] = round((stats["success_today"] / stats["executions_today"]) * 100, 1)
    else:
        stats["success_rate"] = 0
    
    return stats

def cleanup_workflow_logs():
    """Cleanup old workflow logs"""
    settings = frappe.get_single("FlashChat Settings")
    retention_days = getattr(settings, 'workflow_log_retention_days', 30)
    
    cutoff_date = add_to_date(now(), days=-retention_days)
    
    frappe.db.delete("FlashChat Workflow Log", {
        "execution_time": ["<", cutoff_date]
    })
    
    frappe.db.commit()

def generate_workflow_analytics():
    """Generate weekly workflow analytics"""
    # TODO: Implement comprehensive workflow analytics
    pass
