# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now, add_to_date, cint, flt
import json

class FlashChatCampaign(Document):
    def validate(self):
        """Validate campaign"""
        self.validate_send_time()
        self.calculate_recipients()
    
    def validate_send_time(self):
        """Validate send time is in future"""
        if self.send_at and self.send_at < now():
            frappe.throw("Send time must be in the future")
    
    def calculate_recipients(self):
        """Calculate number of recipients"""
        if self.target_audience == "All Contacts":
            self.total_recipients = frappe.db.count("Contact", {"mobile_no": ["!=", ""]})
        elif self.target_audience == "Customers":
            filters = {"mobile_no": ["!=", ""]}
            if self.customer_group:
                filters["customer_group"] = self.customer_group
            if self.territory:
                filters["territory"] = self.territory
            self.total_recipients = frappe.db.count("Customer", filters)
        elif self.target_audience == "Leads":
            filters = {"mobile_no": ["!=", ""]}
            if self.lead_source:
                filters["source"] = self.lead_source
            if self.territory:
                filters["territory"] = self.territory
            self.total_recipients = frappe.db.count("Lead", filters)
        elif self.target_audience == "Custom Filter":
            # TODO: Implement custom filter logic
            self.total_recipients = 0
    
    def schedule_campaign(self):
        """Schedule campaign for sending"""
        if self.status != "Draft":
            frappe.throw("Only draft campaigns can be scheduled")
        
        if not self.send_at:
            frappe.throw("Send time is required")
        
        self.status = "Scheduled"
        self.save()
        frappe.msgprint("Campaign scheduled successfully")
    
    def start_campaign(self):
        """Start campaign immediately"""
        if self.status not in ["Draft", "Scheduled"]:
            frappe.throw("Campaign cannot be started")
        
        self.status = "Processing"
        self.save()
        
        # Process campaign in background
        frappe.enqueue(
            "flashchat_integration.flashchat_campaign.flashchat_campaign.process_campaign",
            queue="long",
            campaign_name=self.name
        )
        
        frappe.msgprint("Campaign started successfully")
    
    def cancel_campaign(self):
        """Cancel campaign"""
        if self.status in ["Completed", "Cancelled"]:
            frappe.throw("Campaign cannot be cancelled")
        
        self.status = "Cancelled"
        self.save()
        frappe.msgprint("Campaign cancelled successfully")

@frappe.whitelist()
def schedule_campaign(name):
    """Schedule a campaign"""
    doc = frappe.get_doc("FlashChat Campaign", name)
    doc.schedule_campaign()

@frappe.whitelist()
def start_campaign(name):
    """Start a campaign"""
    doc = frappe.get_doc("FlashChat Campaign", name)
    doc.start_campaign()

@frappe.whitelist()
def cancel_campaign(name):
    """Cancel a campaign"""
    doc = frappe.get_doc("FlashChat Campaign", name)
    doc.cancel_campaign()

def process_campaign(campaign_name):
    """Process campaign in background"""
    try:
        campaign = frappe.get_doc("FlashChat Campaign", campaign_name)
        
        if campaign.status != "Processing":
            return
        
        # Get recipients
        recipients = get_campaign_recipients(campaign)
        
        # Send messages
        from flashchat_integration.api import FlashChatAPI
        api = FlashChatAPI()
        
        sent_count = 0
        failed_count = 0
        
        for recipient in recipients:
            try:
                if campaign.message_type == "SMS":
                    result = api.send_sms(
                        phone=recipient["mobile_no"],
                        message=campaign.message_content,
                        reference_doctype="FlashChat Campaign",
                        reference_name=campaign.name
                    )
                elif campaign.message_type == "WhatsApp":
                    # Get WhatsApp account
                    accounts = api.get_whatsapp_accounts()
                    if accounts.get("success") and accounts.get("accounts"):
                        account_id = accounts["accounts"][0]["id"]
                        result = api.send_whatsapp(
                            account=account_id,
                            recipient=recipient["mobile_no"],
                            message=campaign.message_content,
                            reference_doctype="FlashChat Campaign",
                            reference_name=campaign.name
                        )
                    else:
                        raise Exception("No WhatsApp accounts available")
                
                if result.get("success"):
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                frappe.log_error(f"Campaign message failed: {str(e)}", "FlashChat Campaign")
        
        # Update campaign statistics
        campaign.messages_sent = sent_count
        campaign.messages_failed = failed_count
        campaign.status = "Completed"
        
        if campaign.total_recipients > 0:
            campaign.success_rate = (sent_count / campaign.total_recipients) * 100
        
        campaign.save()
        
    except Exception as e:
        # Update campaign status to failed
        campaign = frappe.get_doc("FlashChat Campaign", campaign_name)
        campaign.status = "Failed"
        campaign.save()
        
        frappe.log_error(f"Campaign processing failed: {str(e)}", "FlashChat Campaign Processing")

def get_campaign_recipients(campaign):
    """Get recipients for campaign"""
    recipients = []
    
    if campaign.target_audience == "All Contacts":
        recipients = frappe.get_all(
            "Contact",
            filters={"mobile_no": ["!=", ""]},
            fields=["name", "mobile_no", "first_name", "last_name"]
        )
    elif campaign.target_audience == "Customers":
        filters = {"mobile_no": ["!=", ""]}
        if campaign.customer_group:
            filters["customer_group"] = campaign.customer_group
        if campaign.territory:
            filters["territory"] = campaign.territory
        
        recipients = frappe.get_all(
            "Customer",
            filters=filters,
            fields=["name", "mobile_no", "customer_name"]
        )
    elif campaign.target_audience == "Leads":
        filters = {"mobile_no": ["!=", ""]}
        if campaign.lead_source:
            filters["source"] = campaign.lead_source
        if campaign.territory:
            filters["territory"] = campaign.territory
        
        recipients = frappe.get_all(
            "Lead",
            filters=filters,
            fields=["name", "mobile_no", "lead_name"]
        )
    elif campaign.target_audience == "Custom Filter":
        # TODO: Implement custom filter logic
        if campaign.contact_filters:
            try:
                custom_filters = json.loads(campaign.contact_filters)
                recipients = frappe.get_all(
                    "Contact",
                    filters=custom_filters,
                    fields=["name", "mobile_no", "first_name", "last_name"]
                )
            except:
                recipients = []
    
    return recipients
