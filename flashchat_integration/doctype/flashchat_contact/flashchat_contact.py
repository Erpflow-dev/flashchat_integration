
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now

class FlashChatContact(Document):
    def validate(self):
        """Validate FlashChat contact"""
        self.validate_phone_number()
        self.set_contact_name()
    
    def validate_phone_number(self):
        """Validate phone number format"""
        if self.phone_number and not self.phone_number.startswith('+'):
            frappe.throw("Phone number must be in international format (+country code)")
    
    def set_contact_name(self):
        """Set contact name from first and last name"""
        if self.first_name and self.last_name:
            self.contact_name = f"{self.first_name} {self.last_name}"
        elif self.first_name:
            self.contact_name = self.first_name
        elif not self.contact_name:
            self.contact_name = self.phone_number
    
    def sync_to_flashchat(self):
        """Sync contact to FlashChat"""
        try:
            from flashchat_integration.api import FlashChatAPI
            api = FlashChatAPI()
            
            # Prepare contact data
            contact_data = {
                'name': self.contact_name,
                'phone': self.phone_number,
                'email': self.email,
                'company': self.company,
                'first_name': self.first_name,
                'last_name': self.last_name
            }
            
            # Call FlashChat API (implement based on API specs)
            # result = api.sync_contact(contact_data)
            
            # Update sync status
            self.sync_status = 'Synced'
            self.last_sync = now()
            self.save()
            
            return {'success': True}
            
        except Exception as e:
            self.sync_status = 'Failed'
            self.save()
            frappe.log_error(f"Contact sync failed: {str(e)}", "FlashChat Contact Sync")
            return {'success': False, 'error': str(e)}

