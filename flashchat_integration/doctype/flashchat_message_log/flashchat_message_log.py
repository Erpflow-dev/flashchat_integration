# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now, format_datetime

class FlashChatMessageLog(Document):
    def validate(self):
        """Validate message log"""
        self.validate_phone_number()
        self.set_timestamps()
    
    def validate_phone_number(self):
        """Validate phone number format"""
        if self.phone_number and not self.phone_number.startswith('+'):
            frappe.throw("Phone number must be in international format (+country code)")
    
    def set_timestamps(self):
        """Set timestamps"""
        if not self.sent_at and self.status in ['Sent', 'Delivered', 'Read']:
            self.sent_at = now()
        
        if not self.received_at and self.status == 'Received':
            self.received_at = now()
    
    def retry_send(self):
        """Retry sending failed message"""
        if self.status != 'Failed':
            frappe.throw("Only failed messages can be retried")
        
        try:
            from flashchat_integration.api import FlashChatAPI
            api = FlashChatAPI()
            
            if self.message_type == 'SMS':
                result = api.send_sms(
                    phone=self.phone_number,
                    message=self.message_content,
                    reference_doctype=self.reference_doctype,
                    reference_name=self.reference_name
                )
            elif self.message_type == 'WhatsApp':
                # Get WhatsApp account
                accounts = api.get_whatsapp_accounts()
                if accounts.get("success") and accounts.get("accounts"):
                    account_id = accounts["accounts"][0]["id"]
                    result = api.send_whatsapp(
                        account=account_id,
                        recipient=self.phone_number,
                        message=self.message_content,
                        reference_doctype=self.reference_doctype,
                        reference_name=self.reference_name
                    )
                else:
                    frappe.throw("No WhatsApp accounts available")
            
            # Update this record
            self.status = 'Sent'
            self.retry_count += 1
            self.error_message = None
            self.save()
            
            return {"success": True, "message": "Message resent successfully"}
            
        except Exception as e:
            self.retry_count += 1
            self.error_message = str(e)
            self.save()
            return {"success": False, "error": str(e)}

@frappe.whitelist()
def retry_message(name):
    """Retry sending a message"""
    doc = frappe.get_doc("FlashChat Message Log", name)
    return doc.retry_send()