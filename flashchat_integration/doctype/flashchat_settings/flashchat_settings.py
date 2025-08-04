
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_url

class FlashChatSettings(Document):
    def validate(self):
        """Validate FlashChat settings"""
        self.validate_api_secret()
        self.set_webhook_url()
    
    def validate_api_secret(self):
        """Validate API secret is provided"""
        if not self.api_secret:
            frappe.throw("API Secret is required")
    
    def set_webhook_url(self):
        """Set webhook URL automatically"""
        if self.enable_webhooks:
            site_url = get_url()
            self.webhook_url = f"{site_url}/api/method/flashchat_integration.api.flashchat_webhook"
    
    def on_update(self):
        """Clear cache when settings are updated"""
        frappe.cache().delete_value("flashchat_settings")
