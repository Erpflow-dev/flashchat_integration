# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now, add_to_date, cint
import json

class FlashChatWorkflow(Document):
    def validate(self):
        """Validate workflow configuration"""
        self.validate_conditions()
        self.validate_message_config()
        self.validate_recipient_field()
    
    def validate_conditions(self):
        """Validate Python conditions"""
        if self.conditions:
            try:
                # Test compile the conditions
                compile(self.conditions, '<string>', 'eval')
            except SyntaxError as e:
                frappe.throw(f"Invalid Python syntax in conditions: {str(e)}")
    
    def validate_message_config(self):
        """Validate message configuration"""
        if not self.message_template and not self.custom_message:
            frappe.throw("Either Message Template or Custom Message is required")
    
    def validate_recipient_field(self):
        """Validate recipient field exists in trigger doctype"""
        if self.trigger_doctype and self.recipient_field:
            try:
                meta = frappe.get_meta(self.trigger_doctype)
                if not meta.get_field(self.recipient_field):
                    frappe.throw(f"Field '{self.recipient_field}' not found in {self.trigger_doctype}")
            except:
                pass  # DocType might not exist yet
    
    def execute_workflow(self, doc, method=None):
        """Execute workflow for a document"""
        try:
            # Check if workflow is active
            if not self.is_active:
                return
            
            # Check if trigger event matches
            if self.workflow_type == "Event Based" and method != self.trigger_event:
                return
            
            # Check conditions
            if not self.check_conditions(doc):
                return
            
            # Check rate limits
            if self.rate_limit_check and not self.check_rate_limits():
                self.log_execution(doc, False, "Rate limit exceeded")
                return
            
            # Check working hours
            if self.working_hours_only and not self.is_working_hours():
                self.log_execution(doc, False, "Outside working hours")
                return
            
            # Get recipients
            recipients = self.get_recipients(doc)
            if not recipients:
                self.log_execution(doc, False, "No recipients found")
                return
            
            # Check Do Not Disturb
            if self.respect_dnd:
                recipients = self.filter_dnd_recipients(recipients)
            
            if not recipients:
                self.log_execution(doc, False, "All recipients have DND enabled")
                return
            
            # Prepare message
            message = self.prepare_message(doc)
            
            # Execute with delay if specified
            if self.delay_duration > 0:
                self.schedule_execution(doc, recipients, message)
            else:
                self.send_messages(doc, recipients, message)
            
        except Exception as e:
            self.log_execution(doc, False, str(e))
            frappe.log_error(f"Workflow execution failed: {str(e)}", "FlashChat Workflow")
    
    def check_conditions(self, doc):
        """Check if workflow conditions are met"""
        if not self.conditions:
            return True
        
        try:
            # Create safe execution context
            context = {
                'doc': doc,
                'frappe': frappe,
                'now': now(),
                'cint': cint,
                'flt': float
            }
            
            # Execute conditions
            result = eval(self.conditions, {"__builtins__": {}}, context)
            return bool(result)
            
        except Exception as e:
            frappe.log_error(f"Condition evaluation failed: {str(e)}", "FlashChat Workflow")
            return False
    
    def check_rate_limits(self):
        """Check if rate limits allow sending"""
        try:
            from flashchat_integration.api import FlashChatAPI
            api = FlashChatAPI()
            return api._check_rate_limit(self.message_type)
        except:
            return True  # Allow if check fails
    
    def is_working_hours(self):
        """Check if current time is within working hours"""
        # TODO: Implement working hours check
        # For now, return True
        return True
    
    def get_recipients(self, doc):
        """Get recipient phone numbers from document"""
        recipients = []
        
        # Get primary recipient
        recipient = getattr(doc, self.recipient_field, None)
        
        if recipient:
            if self.send_to_multiple and ',' in recipient:
                # Multiple recipients separated by comma
                recipients.extend([r.strip() for r in recipient.split(',') if r.strip()])
            else:
                recipients.append(recipient)
        
        # Use fallback if no recipients found
        if not recipients and self.fallback_recipient:
            recipients.append(self.fallback_recipient)
        
        # Validate phone numbers
        valid_recipients = []
        for phone in recipients:
            if phone and (phone.startswith('+') or phone.isdigit()):
                valid_recipients.append(phone)
        
        return valid_recipients
    
    def filter_dnd_recipients(self, recipients):
        """Filter out recipients with Do Not Disturb enabled"""
        # TODO: Implement DND check against contact preferences
        return recipients
    
    def prepare_message(self, doc):
        """Prepare message content"""
        if self.message_template:
            # Use message template
            template = frappe.get_doc("Message Template", self.message_template)
            context = self.build_message_context(doc)
            return template.render_template(context)
        else:
            # Use custom message
            message = self.custom_message
            
            # Replace field placeholders
            context = self.build_message_context(doc)
            for key, value in context.items():
                if value is not None:
                    message = message.replace(f'{{{key}}}', str(value))
            
            return message
    
    def build_message_context(self, doc):
        """Build context for message rendering"""
        context = {}
        
        # Add all document fields
        for field in doc.meta.get_valid_columns():
            value = getattr(doc, field.fieldname, None)
            if value is not None:
                context[field.fieldname] = value
        
        # Add common fields
        context.update({
            'customer_name': getattr(doc, 'customer_name', '') or getattr(doc, 'name', ''),
            'company_name': frappe.defaults.get_user_default('Company') or 'Your Company',
            'date': frappe.utils.format_date(now(), 'dd/MM/yyyy'),
            'time': frappe.utils.format_datetime(now(), 'HH:mm')
        })
        
        return context
    
    def schedule_execution(self, doc, recipients, message):
        """Schedule delayed execution"""
        execute_at = now()
        
        if self.delay_unit == "Minutes":
            execute_at = add_to_date(execute_at, minutes=self.delay_duration)
        elif self.delay_unit == "Hours":
            execute_at = add_to_date(execute_at, hours=self.delay_duration)
        elif self.delay_unit == "Days":
            execute_at = add_to_date(execute_at, days=self.delay_duration)
        
        # Schedule background job
        frappe.enqueue(
            "flashchat_integration.doctype.flashchat_workflow.flashchat_workflow.execute_scheduled_workflow",
            queue="long",
            timeout=300,
            at_time=execute_at,
            workflow_name=self.name,
            doc_name=doc.name,
            recipients=recipients,
            message=message
        )
        
        self.log_execution(doc, True, f"Scheduled for {execute_at}")
    
    def send_messages(self, doc, recipients, message):
        """Send messages to recipients"""
        from flashchat_integration.api import FlashChatAPI
        
        try:
            api = FlashChatAPI()
            success_count = 0
            total_count = len(recipients)
            
            for recipient in recipients:
                try:
                    if self.message_type == "SMS":
                        result = api.send_sms(
                            phone=recipient,
                            message=message,
                            reference_doctype=doc.doctype,
                            reference_name=doc.name
                        )
                    elif self.message_type == "WhatsApp":
                        # Get WhatsApp account
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
                            raise Exception("No WhatsApp accounts available")
                    elif self.message_type == "OTP":
                        result = api.send_otp(
                            phone=recipient,
                            reference_doctype=doc.doctype,
                            reference_name=doc.name
                        )
                    
                    if result.get("success"):
                        success_count += 1
                
                except Exception as e:
                    frappe.log_error(f"Failed to send to {recipient}: {str(e)}", "FlashChat Workflow")
            
            # Log execution result
            success = success_count > 0
            message_detail = f"Sent to {success_count}/{total_count} recipients"
            self.log_execution(doc, success, message_detail)
            
        except Exception as e:
            self.log_execution(doc, False, str(e))
            raise
    
    def log_execution(self, doc, success, details=""):
        """Log workflow execution"""
        # Update statistics
        self.execution_count = (self.execution_count or 0) + 1
        if success:
            self.success_count = (self.success_count or 0) + 1
        else:
            self.failure_count = (self.failure_count or 0) + 1
        
        self.last_executed = now()
        
        # Calculate success rate
        if self.execution_count > 0:
            self.average_success_rate = (self.success_count / self.execution_count) * 100
        
        # Save without triggering events
        frappe.db.set_value("FlashChat Workflow", self.name, {
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "last_executed": self.last_executed,
            "average_success_rate": self.average_success_rate
        }, update_modified=False)
        
        # Create detailed log if enabled
        if self.enable_logging:
            self.create_execution_log(doc, success, details)
    
    def create_execution_log(self, doc, success, details):
        """Create detailed execution log"""
        try:
            log = frappe.get_doc({
                "doctype": "FlashChat Workflow Log",
                "workflow": self.name,
                "trigger_document": doc.doctype,
                "trigger_name": doc.name,
                "execution_time": now(),
                "status": "Success" if success else "Failed",
                "details": details,
                "message_type": self.message_type
            })
            log.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Failed to create workflow log: {str(e)}", "FlashChat Workflow Log")

@frappe.whitelist()
def test_workflow(workflow_name, doc_name):
    """Test workflow execution"""
    try:
        workflow = frappe.get_doc("FlashChat Workflow", workflow_name)
        doc = frappe.get_doc(workflow.trigger_doctype, doc_name)
        
        # Execute workflow in test mode
        workflow.execute_workflow(doc, workflow.trigger_event)
        
        return {"success": True, "message": "Workflow executed successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_scheduled_workflow(workflow_name, doc_name, recipients, message):
    """Execute scheduled workflow"""
    try:
        workflow = frappe.get_doc("FlashChat Workflow", workflow_name)
        doc = frappe.get_doc(workflow.trigger_doctype, doc_name)
        
        workflow.send_messages(doc, recipients, message)
        
    except Exception as e:
        frappe.log_error(f"Scheduled workflow execution failed: {str(e)}", "FlashChat Scheduled Workflow")

def register_workflow_hooks():
    """Register workflow hooks for all active workflows"""
    workflows = frappe.get_all(
        "FlashChat Workflow",
        filters={"is_active": 1, "workflow_type": "Event Based"},
        fields=["name", "trigger_doctype", "trigger_event"]
    )
    
    # Group workflows by doctype and event
    hooks = {}
    for workflow in workflows:
        doctype = workflow.trigger_doctype
        event = workflow.trigger_event
        
        if doctype not in hooks:
            hooks[doctype] = {}
        if event not in hooks[doctype]:
            hooks[doctype][event] = []
        
        hooks[doctype][event].append(workflow.name)
    
    return hooks

def execute_workflow_hooks(doc, method):
    """Execute workflow hooks for document events"""
    # Get workflows for this doctype and event
    workflows = frappe.get_all(
        "FlashChat Workflow",
        filters={
            "is_active": 1,
            "workflow_type": "Event Based",
            "trigger_doctype": doc.doctype,
            "trigger_event": method
        },
        fields=["name"]
    )
    
    for workflow_data in workflows:
        try:
            workflow = frappe.get_doc("FlashChat Workflow", workflow_data.name)
            workflow.execute_workflow(doc, method)
        except Exception as e:
            frappe.log_error(f"Workflow execution failed: {str(e)}", "FlashChat Workflow Hook")


