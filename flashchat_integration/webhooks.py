# flashchat_integration/api/webhooks.py
import frappe
from frappe import _
import json
import hmac
import hashlib
from frappe.utils import now

@frappe.whitelist(allow_guest=True)
def flashchat_webhook():
    """Handle FlashChat webhook notifications"""
    try:
        if frappe.request.method != "POST":
            frappe.throw(_("Only POST method allowed"))
        
        # Get webhook data
        webhook_data = json.loads(frappe.request.data.decode('utf-8'))
        
        # Verify webhook if secret is configured
        if not verify_webhook_signature():
            frappe.log_error("Invalid webhook signature", "FlashChat Webhook")
            frappe.local.response.http_status_code = 401
            return {"status": "error", "message": "Invalid signature"}
        
        # Process webhook based on event type
        event_type = webhook_data.get('event')
        
        if event_type == 'message_status_update':
            handle_message_status_update(webhook_data)
        elif event_type == 'message_received':
            handle_message_received(webhook_data)
        elif event_type == 'campaign_update':
            handle_campaign_update(webhook_data)
        elif event_type == 'device_status':
            handle_device_status_update(webhook_data)
        else:
            frappe.log_error(f"Unknown webhook event: {event_type}", "FlashChat Webhook")
        
        return {"status": "success"}
        
    except Exception as e:
        frappe.log_error(f"FlashChat webhook error: {str(e)}", "FlashChat Webhook Error")
        frappe.local.response.http_status_code = 400
        return {"status": "error", "message": str(e)}

def verify_webhook_signature():
    """Verify webhook signature if configured"""
    try:
        settings = frappe.get_single("FlashChat Settings")
        
        if not settings.webhook_enabled or not settings.webhook_secret:
            return True  # Skip verification if not configured
        
        signature = frappe.request.headers.get('X-FlashChat-Signature')
        if not signature:
            return False
        
        # Calculate expected signature
        webhook_secret = settings.get_password("webhook_secret")
        expected_signature = hmac.new(
            webhook_secret.encode(),
            frappe.request.data,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
        
    except Exception as e:
        frappe.log_error(f"Webhook signature verification failed: {str(e)}")
        return False

def handle_message_status_update(webhook_data):
    """Handle message status update from FlashChat"""
    try:
        message_id = webhook_data.get('message_id')
        new_status = webhook_data.get('status')
        delivered_at = webhook_data.get('delivered_at')
        
        if not message_id or not new_status:
            return
        
        # Find message logs with this FlashChat ID
        message_logs = frappe.get_all("FlashChat Message Log",
                                    filters={"flashchat_id": message_id},
                                    fields=["name", "status"])
        
        for log in message_logs:
            if log.status != new_status.title():
                update_data = {"status": new_status.title()}
                
                if new_status.lower() == "delivered" and delivered_at:
                    update_data["delivered_at"] = delivered_at
                elif new_status.lower() == "delivered" and not delivered_at:
                    update_data["delivered_at"] = now()
                
                frappe.db.set_value("FlashChat Message Log", log.name, update_data)
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Error handling message status update: {str(e)}")

def handle_message_received(webhook_data):
    """Handle incoming message from FlashChat"""
    try:
        phone = webhook_data.get('phone')
        message = webhook_data.get('message')
        message_type = webhook_data.get('type', 'SMS')
        received_at = webhook_data.get('received_at', now())
        device_id = webhook_data.get('device_id')
        
        if not phone or not message:
            return
        
        # Create message log for received message
        message_log = frappe.get_doc({
            'doctype': 'FlashChat Message Log',
            'message_type': message_type,
            'phone_number': phone,
            'message_content': message,
            'status': 'Received',
            'direction': 'Inbound',
            'device_id': device_id,
            'sent_at': received_at
        })
        
        # Try to link to existing contact/customer/lead
        link_message_to_contact(message_log, phone)
        
        message_log.insert(ignore_permissions=True)
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Error handling received message: {str(e)}")

def handle_campaign_update(webhook_data):
    """Handle campaign status update"""
    try:
        campaign_id = webhook_data.get('campaign_id')
        status = webhook_data.get('status')
        statistics = webhook_data.get('statistics', {})
        
        if not campaign_id:
            return
        
        # Log campaign update (placeholder for future campaign feature)
        frappe.log_error(f"Campaign update received: {campaign_id} - {status}", "FlashChat Campaign Update")
        
    except Exception as e:
        frappe.log_error(f"Error handling campaign update: {str(e)}")

def handle_device_status_update(webhook_data):
    """Handle device status update"""
    try:
        device_id = webhook_data.get('device_id')
        status = webhook_data.get('status')
        
        if device_id and status:
            # Log device status change
            frappe.log_error(f"Device status update: {device_id} - {status}", "FlashChat Device Status")
            
    except Exception as e:
        frappe.log_error(f"Error handling device status update: {str(e)}")

def link_message_to_contact(message_log, phone):
    """Link received message to existing contact/customer/lead"""
    try:
        # Search for contact with this phone number
        contacts = frappe.db.sql("""
            SELECT c.name
            FROM `tabContact` c
            INNER JOIN `tabContact Phone` cp ON cp.parent = c.name
            WHERE cp.phone = %s
            LIMIT 1
        """, [phone], as_dict=True)
        
        if contacts:
            message_log.reference_doctype = "Contact"
            message_log.reference_name = contacts[0].name
            return
        
        # Search for customer with mobile number
        customers = frappe.get_all("Customer", 
                                 filters={"mobile_no": phone},
                                 fields=["name"],
                                 limit=1)
        
        if customers:
            message_log.reference_doctype = "Customer"
            message_log.reference_name = customers[0].name
            return
        
        # Search for lead with mobile number
        leads = frappe.get_all("Lead", 
                             filters={"mobile_no": phone},
                             fields=["name"],
                             limit=1)
        
        if leads:
            message_log.reference_doctype = "Lead"
            message_log.reference_name = leads[0].name
    
    except Exception as e:
        frappe.log_error(f"Error linking message to contact: {str(e)}")