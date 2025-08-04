
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import now, add_to_date, get_datetime, getdate
from datetime import datetime, timedelta
import json

class FlashChatWorkflowEngine:
    """Advanced workflow engine for FlashChat automation"""
    
    def __init__(self):
        self.settings = frappe.get_single("FlashChat Settings")
    
    def process_scheduled_workflows(self):
        """Process all scheduled workflows"""
        try:
            # Get scheduled workflows
            scheduled_jobs = frappe.get_all(
                "Scheduled Job Log",
                filters={
                    "status": "Scheduled",
                    "method": "flashchat_integration.workflow_engine.execute_scheduled_workflow"
                },
                fields=["name", "scheduled_time", "kwargs"]
            )
            
            current_time = get_datetime()
            
            for job in scheduled_jobs:
                if get_datetime(job.scheduled_time) <= current_time:
                    self.execute_scheduled_job(job)
                    
        except Exception as e:
            frappe.log_error(f"Scheduled workflow processing failed: {str(e)}", "FlashChat Workflow Engine")
    
    def create_dynamic_workflow(self, config):
        """Create workflow dynamically from configuration"""
        workflow = frappe.get_doc({
            "doctype": "FlashChat Workflow",
            "workflow_name": config.get("name"),
            "workflow_type": config.get("type", "Event Based"),
            "trigger_doctype": config.get("doctype"),
            "trigger_event": config.get("event"),
            "message_type": config.get("message_type", "SMS"),
            "recipient_field": config.get("recipient_field"),
            "custom_message": config.get("message"),
            "conditions": config.get("conditions"),
            "is_active": config.get("active", 1),
            "delay_duration": config.get("delay", 0),
            "delay_unit": config.get("delay_unit", "Minutes")
        })
        
        workflow.insert()
        return workflow
    
    def execute_conditional_workflow(self, doctype, filters, message_config):
        """Execute workflow for documents matching conditions"""
        try:
            # Get documents matching filters
            documents = frappe.get_all(doctype, filters=filters, fields=["name"])
            
            results = []
            for doc_data in documents:
                doc = frappe.get_doc(doctype, doc_data.name)
                result = self.send_targeted_message(doc, message_config)
                results.append({
                    "document": doc.name,
                    "success": result.get("success", False),
                    "message": result.get("message", "")
                })
            
            return results
            
        except Exception as e:
            frappe.log_error(f"Conditional workflow execution failed: {str(e)}", "FlashChat Workflow Engine")
            return []
    
    def send_targeted_message(self, doc, message_config):
        """Send targeted message to document contact"""
        try:
            from flashchat_integration.api import FlashChatAPI
            
            # Get recipient
            recipient_field = message_config.get("recipient_field", "mobile_no")
            recipient = getattr(doc, recipient_field, None)
            
            if not recipient:
                return {"success": False, "message": "No recipient found"}
            
            # Prepare message
            message = message_config.get("message", "")
            context = self.build_message_context(doc)
            
            for key, value in context.items():
                if value is not None:
                    message = message.replace(f'{{{key}}}', str(value))
            
            # Send message
            api = FlashChatAPI()
            message_type = message_config.get("message_type", "SMS")
            
            if message_type == "SMS":
                result = api.send_sms(
                    phone=recipient,
                    message=message,
                    reference_doctype=doc.doctype,
                    reference_name=doc.name
                )
            elif message_type == "WhatsApp":
                accounts = api.get_whatsapp_accounts()
                if accounts.get("success") and accounts.get("accounts"):
                    account_id = accounts["accounts"][0]["id"]
                    result = api.send_whatsapp(
                        account=account_id,
                        recipient=recipient,
                        message=message,
                        reference_doctype=doc.doctype,
                        reference_name=doc.name
                    )
                else:
                    return {"success": False, "message": "No WhatsApp accounts"}
            
            return result
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def build_message_context(self, doc):
        """Build message context from document"""
        context = {}
        
        # Add all document fields
        for field in doc.meta.get_valid_columns():
            value = getattr(doc, field.fieldname, None)
            if value is not None:
                context[field.fieldname] = value
        
        # Add computed fields
        context.update({
            "company_name": frappe.defaults.get_user_default("Company") or "Your Company",
            "current_date": frappe.utils.format_date(now()),
            "current_time": frappe.utils.format_datetime(now()),
            "doc_url": frappe.utils.get_url_to_form(doc.doctype, doc.name)
        })
        
        return context
    
    def create_drip_campaign(self, contacts, messages, intervals):
        """Create drip campaign with multiple messages"""
        try:
            campaign = frappe.get_doc({
                "doctype": "FlashChat Campaign",
                "campaign_name": f"Drip Campaign {now()}",
                "message_type": "SMS",
                "status": "Processing"
            })
            campaign.insert()
            
            # Schedule messages
            for i, (message, interval) in enumerate(zip(messages, intervals)):
                send_time = add_to_date(now(), **interval)
                
                for contact in contacts:
                    frappe.enqueue(
                        "flashchat_integration.workflow_engine.send_drip_message",
                        queue="long",
                        at_time=send_time,
                        contact=contact,
                        message=message,
                        campaign_id=campaign.name
                    )
            
            return campaign
            
        except Exception as e:
            frappe.log_error(f"Drip campaign creation failed: {str(e)}", "FlashChat Workflow Engine")
            return None
    
    def setup_anniversary_reminders(self):
        """Setup automated anniversary/birthday reminders"""
        try:
            # Get contacts with anniversary dates
            contacts = frappe.get_all(
                "Contact",
                filters={
                    "mobile_no": ["!=", ""],
                    "birth_date": ["!=", ""]
                },
                fields=["name", "mobile_no", "birth_date", "first_name"]
            )
            
            for contact in contacts:
                if contact.birth_date:
                    # Calculate next birthday
                    today = getdate()
                    birth_date = getdate(contact.birth_date)
                    
                    next_birthday = birth_date.replace(year=today.year)
                    if next_birthday < today:
                        next_birthday = next_birthday.replace(year=today.year + 1)
                    
                    # Schedule birthday message
                    message = f"🎉 Happy Birthday {contact.first_name}! Wishing you a wonderful day filled with happiness and joy. Best wishes from {frappe.defaults.get_user_default('Company')}!"
                    
                    frappe.enqueue(
                        "flashchat_integration.workflow_engine.send_anniversary_message",
                        queue="long",
                        at_time=next_birthday,
                        contact_name=contact.name,
                        phone=contact.mobile_no,
                        message=message
                    )
            
        except Exception as e:
            frappe.log_error(f"Anniversary reminder setup failed: {str(e)}", "FlashChat Workflow Engine")

def send_drip_message(contact, message, campaign_id):
    """Send individual drip campaign message"""
    try:
        from flashchat_integration.api import FlashChatAPI
        
        api = FlashChatAPI()
        result = api.send_sms(
            phone=contact["mobile_no"],
            message=message,
            reference_doctype="FlashChat Campaign",
            reference_name=campaign_id
        )
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Drip message sending failed: {str(e)}", "FlashChat Drip Campaign")

def send_anniversary_message(contact_name, phone, message):
    """Send anniversary/birthday message"""
    try:
        from flashchat_integration.api import FlashChatAPI
        
        api = FlashChatAPI()
        result = api.send_sms(
            phone=phone,
            message=message,
            reference_doctype="Contact",
            reference_name=contact_name
        )
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Anniversary message sending failed: {str(e)}", "FlashChat Anniversary")

@frappe.whitelist()
def create_custom_workflow(config):
    """API to create custom workflow"""
    try:
        if isinstance(config, str):
            config = json.loads(config)
        
        engine = FlashChatWorkflowEngine()
        workflow = engine.create_dynamic_workflow(config)
        
        return {"success": True, "workflow": workflow.name}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def execute_bulk_workflow(doctype, filters, message_config):
    """Execute workflow for multiple documents"""
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        if isinstance(message_config, str):
            message_config = json.loads(message_config)
        
        engine = FlashChatWorkflowEngine()
        results = engine.execute_conditional_workflow(doctype, filters, message_config)
        
        return {"success": True, "results": results}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def setup_drip_campaign(contacts, messages, intervals):
    """Setup drip campaign"""
    try:
        if isinstance(contacts, str):
            contacts = json.loads(contacts)
        if isinstance(messages, str):
            messages = json.loads(messages)
        if isinstance(intervals, str):
            intervals = json.loads(intervals)
        
        engine = FlashChatWorkflowEngine()
        campaign = engine.create_drip_campaign(contacts, messages, intervals)
        
        if campaign:
            return {"success": True, "campaign": campaign.name}
        else:
            return {"success": False, "error": "Failed to create campaign"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}
