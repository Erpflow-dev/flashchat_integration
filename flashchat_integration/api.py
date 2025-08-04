
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
import requests
import json
import hmac
import hashlib
import base64
from frappe import _
from frappe.utils import now, add_to_date, cint, flt
from datetime import datetime, timedelta

@frappe.whitelist()
def send_sms_api(phone, message, reference_doctype=None, reference_name=None):
    """Send SMS via FlashChat API"""
    try:
        api = FlashChatAPI()
        result = api.send_sms(
            phone=phone,
            message=message,
            reference_doctype=reference_doctype,
            reference_name=reference_name
        )
        return result
    except Exception as e:
        frappe.log_error(f"SMS API Error: {str(e)}", "FlashChat SMS API")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def send_whatsapp_api(account, recipient, message, reference_doctype=None, reference_name=None):
    """Send WhatsApp message via FlashChat API"""
    try:
        api = FlashChatAPI()
        result = api.send_whatsapp(
            account=account,
            recipient=recipient,
            message=message,
            reference_doctype=reference_doctype,
            reference_name=reference_name
        )
        return result
    except Exception as e:
        frappe.log_error(f"WhatsApp API Error: {str(e)}", "FlashChat WhatsApp API")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def send_otp_api(phone, expire=300, reference_doctype=None, reference_name=None):
    """Send OTP via FlashChat API"""
    try:
        api = FlashChatAPI()
        result = api.send_otp(
            phone=phone,
            expire=expire,
            reference_doctype=reference_doctype,
            reference_name=reference_name
        )
        return result
    except Exception as e:
        frappe.log_error(f"OTP API Error: {str(e)}", "FlashChat OTP API")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def verify_otp_api(code):
    """Verify OTP code"""
    try:
        api = FlashChatAPI()
        result = api.verify_otp(code)
        return result
    except Exception as e:
        frappe.log_error(f"OTP Verify Error: {str(e)}", "FlashChat OTP Verify")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_whatsapp_accounts_api():
    """Get WhatsApp accounts"""
    try:
        api = FlashChatAPI()
        result = api.get_whatsapp_accounts()
        return result
    except Exception as e:
        frappe.log_error(f"WhatsApp Accounts Error: {str(e)}", "FlashChat WhatsApp Accounts")
        return {"success": False, "error": str(e)}

@frappe.whitelist(allow_guest=True)
def flashchat_webhook():
    """Handle FlashChat webhooks"""
    try:
        settings = frappe.get_single("FlashChat Settings")
        
        if not settings.enable_webhooks:
            frappe.throw(_("Webhooks are disabled"))
        
        # Get request data
        data = frappe.request.get_data()
        headers = frappe.request.headers
        
        # Verify webhook signature if secret is configured
        if settings.webhook_secret:
            signature = headers.get("X-Frappe-Webhook-Signature")
            if not verify_webhook_signature(data, signature, settings.webhook_secret):
                frappe.throw(_("Invalid webhook signature"))
        
        # Parse webhook data
        webhook_data = json.loads(data)
        event_type = webhook_data.get("event")
        
        if event_type == "message_status_update":
            handle_message_status_update(webhook_data)
        elif event_type == "message_received":
            handle_message_received(webhook_data)
        elif event_type == "campaign_update":
            handle_campaign_update(webhook_data)
        elif event_type == "device_status":
            handle_device_status(webhook_data)
        
        return {"success": True}
        
    except Exception as e:
        frappe.log_error(f"Webhook Error: {str(e)}", "FlashChat Webhook")
        return {"success": False, "error": str(e)}

def verify_webhook_signature(data, signature, secret):
    """Verify webhook signature"""
    if not signature:
        return False
    
    expected_signature = base64.b64encode(
        hmac.new(
            secret.encode('utf-8'),
            data,
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    return hmac.compare_digest(signature, expected_signature)

def handle_message_status_update(data):
    """Handle message status update webhook"""
    message_id = data.get("message_id")
    status = data.get("status")
    
    if message_id:
        # Update message log status
        message_log = frappe.db.get_value(
            "FlashChat Message Log",
            {"flashchat_message_id": message_id},
            "name"
        )
        
        if message_log:
            frappe.db.set_value("FlashChat Message Log", message_log, "status", status)
            frappe.db.commit()

def handle_message_received(data):
    """Handle incoming message webhook"""
    # Log incoming message
    message_log = frappe.get_doc({
        "doctype": "FlashChat Message Log",
        "message_type": "Incoming",
        "phone_number": data.get("from"),
        "message_content": data.get("message"),
        "flashchat_message_id": data.get("message_id"),
        "status": "Received",
        "received_at": now()
    })
    message_log.insert(ignore_permissions=True)

def handle_campaign_update(data):
    """Handle campaign update webhook"""
    campaign_id = data.get("campaign_id")
    status = data.get("status")
    
    # Update campaign status if exists
    campaign = frappe.db.get_value(
        "FlashChat Campaign",
        {"flashchat_campaign_id": campaign_id},
        "name"
    )
    
    if campaign:
        frappe.db.set_value("FlashChat Campaign", campaign, "status", status)
        frappe.db.commit()

def handle_device_status(data):
    """Handle device status webhook"""
    # Log device status change
    frappe.log_error(
        f"Device Status Update: {json.dumps(data)}",
        "FlashChat Device Status"
    )

class FlashChatAPI:
    """FlashChat API wrapper class"""
    
    def __init__(self):
        self.settings = frappe.get_single("FlashChat Settings")
        self.base_url = self.settings.base_url.rstrip('/')
        self.api_secret = self.settings.get_password("api_secret")
        
        if not self.api_secret:
            frappe.throw(_("FlashChat API Secret not configured"))
    
    def _make_request(self, endpoint, method="POST", data=None, params=None):
        """Make HTTP request to FlashChat API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        headers = {
            "Authorization": f"Bearer {self.api_secret}",
            "Content-Type": "application/json"
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            else:
                response = requests.post(url, headers=headers, json=data, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            frappe.log_error(f"FlashChat API Error: {str(e)}", "FlashChat API Request")
            raise frappe.ValidationError(f"FlashChat API Error: {str(e)}")
    
    def send_sms(self, phone, message, reference_doctype=None, reference_name=None):
        """Send SMS message"""
        # Check rate limits
        if not self._check_rate_limit("SMS"):
            frappe.throw(_("SMS rate limit exceeded"))
        
        # Format phone number
        phone = self._format_phone_number(phone)
        
        data = {
            "phone": phone,
            "message": message,
            "sim": self.settings.default_sim or 1,
            "mode": self.settings.sms_mode or "devices"
        }
        
        try:
            response = self._make_request("send-sms", data=data)
            
            # Log message
            self._log_message(
                message_type="SMS",
                phone_number=phone,
                message_content=message,
                flashchat_message_id=response.get("message_id"),
                status="Sent",
                reference_doctype=reference_doctype,
                reference_name=reference_name,
                response_content=json.dumps(response)
            )
            
            return {
                "success": True,
                "message_id": response.get("message_id"),
                "response": response
            }
            
        except Exception as e:
            # Log failed message
            self._log_message(
                message_type="SMS",
                phone_number=phone,
                message_content=message,
                status="Failed",
                reference_doctype=reference_doctype,
                reference_name=reference_name,
                error_message=str(e)
            )
            raise
    
    def send_whatsapp(self, account, recipient, message, reference_doctype=None, reference_name=None):
        """Send WhatsApp message"""
        # Check rate limits
        if not self._check_rate_limit("WhatsApp"):
            frappe.throw(_("WhatsApp rate limit exceeded"))
        
        # Format phone number
        recipient = self._format_phone_number(recipient)
        
        data = {
            "account": account,
            "recipient": recipient,
            "message": message
        }
        
        try:
            response = self._make_request("send-whatsapp", data=data)
            
            # Log message
            self._log_message(
                message_type="WhatsApp",
                phone_number=recipient,
                message_content=message,
                flashchat_message_id=response.get("message_id"),
                status="Sent",
                reference_doctype=reference_doctype,
                reference_name=reference_name,
                response_content=json.dumps(response)
            )
            
            return {
                "success": True,
                "message_id": response.get("message_id"),
                "response": response
            }
            
        except Exception as e:
            # Log failed message
            self._log_message(
                message_type="WhatsApp",
                phone_number=recipient,
                message_content=message,
                status="Failed",
                reference_doctype=reference_doctype,
                reference_name=reference_name,
                error_message=str(e)
            )
            raise
    
    def send_otp(self, phone, expire=300, reference_doctype=None, reference_name=None):
        """Send OTP"""
        # Check rate limits
        if not self._check_rate_limit("OTP"):
            frappe.throw(_("OTP rate limit exceeded"))
        
        # Format phone number
        phone = self._format_phone_number(phone)
        
        data = {
            "phone": phone,
            "expire": expire
        }
        
        try:
            response = self._make_request("send-otp", data=data)
            
            # Log OTP
            self._log_message(
                message_type="OTP",
                phone_number=phone,
                message_content=f"OTP sent with {expire}s expiry",
                flashchat_message_id=response.get("otp_id"),
                status="Sent",
                reference_doctype=reference_doctype,
                reference_name=reference_name,
                response_content=json.dumps(response)
            )
            
            return {
                "success": True,
                "otp_id": response.get("otp_id"),
                "response": response
            }
            
        except Exception as e:
            # Log failed OTP
            self._log_message(
                message_type="OTP",
                phone_number=phone,
                message_content=f"OTP failed with {expire}s expiry",
                status="Failed",
                reference_doctype=reference_doctype,
                reference_name=reference_name,
                error_message=str(e)
            )
            raise
    
    def verify_otp(self, code):
        """Verify OTP code"""
        data = {"code": code}
        
        try:
            response = self._make_request("verify-otp", data=data)
            return {
                "success": True,
                "valid": response.get("valid", False),
                "response": response
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_whatsapp_accounts(self):
        """Get WhatsApp accounts"""
        try:
            response = self._make_request("whatsapp-accounts", method="GET")
            return {
                "success": True,
                "accounts": response.get("accounts", [])
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_phone_number(self, phone):
        """Format phone number to international format"""
        if not phone:
            return phone
        
        # Remove any non-digit characters except +
        phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Add + if not present
        if not phone.startswith('+'):
            phone = '+' + phone
        
        return phone
    
    def _check_rate_limit(self, message_type):
        """Check if rate limit is exceeded"""
        now_time = datetime.now()
        hour_ago = now_time - timedelta(hours=1)
        
        # Get rate limit from settings
        if message_type == "SMS":
            limit = self.settings.sms_rate_limit or 100
        elif message_type == "WhatsApp":
            limit = self.settings.whatsapp_rate_limit or 50
        elif message_type == "OTP":
            limit = self.settings.otp_rate_limit or 20
        else:
            return True
        
        # Count messages sent in last hour
        count = frappe.db.count(
            "FlashChat Message Log",
            {
                "message_type": message_type,
                "sent_at": [">=", hour_ago.strftime("%Y-%m-%d %H:%M:%S")],
                "status": ["in", ["Sent", "Delivered"]]
            }
        )
        
        return count < limit
    
    def _log_message(self, **kwargs):
        """Log message to FlashChat Message Log"""
        message_log = frappe.get_doc({
            "doctype": "FlashChat Message Log",
            "sent_at": now(),
            **kwargs
        })
        message_log.insert(ignore_permissions=True)
        frappe.db.commit()
