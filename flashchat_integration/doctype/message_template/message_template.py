
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now, format_date, format_datetime
import re
import json

class MessageTemplate(Document):
    def validate(self):
        """Validate message template"""
        self.validate_template_variables()
        self.set_created_by()
    
    def validate_template_variables(self):
        """Validate that all variables in template are supported"""
        if not self.template_content:
            return
        
        # Extract variables from template content
        variables = re.findall(r'\{([^}]+)\}', self.template_content)
        
        # Get available variables
        try:
            available_vars = json.loads(self.available_variables or '{}')
            available_var_names = list(available_vars.keys())
        except:
            available_var_names = []
        
        # Check for unsupported variables
        unsupported = [var for var in variables if var not in available_var_names]
        
        if unsupported:
            frappe.throw(
                f"Unsupported variables found: {', '.join(unsupported)}. "
                f"Available variables: {', '.join(available_var_names)}"
            )
    
    def set_created_by(self):
        """Set created by field"""
        if not self.created_by:
            self.created_by = frappe.session.user
    
    def render_template(self, context=None):
        """Render template with provided context"""
        if not context:
            context = {}
        
        content = self.template_content
        
        # Add default context values
        default_context = {
            'company_name': frappe.defaults.get_user_default('Company') or 'Your Company',
            'date': format_date(now(), 'dd/MM/yyyy'),
            'datetime': format_datetime(now(), 'dd/MM/yyyy HH:mm')
        }
        
        # Merge contexts
        render_context = {**default_context, **context}
        
        # Replace variables in template
        for key, value in render_context.items():
            if value is not None:
                content = content.replace(f'{{{key}}}', str(value))
        
        # Update usage statistics
        self.update_usage_stats()
        
        return content
    
    def update_usage_stats(self):
        """Update usage statistics"""
        frappe.db.set_value(
            'Message Template', 
            self.name, 
            {
                'usage_count': (self.usage_count or 0) + 1,
                'last_used': now()
            },
            update_modified=False
        )
    
    def get_preview(self, context=None):
        """Get template preview with sample data"""
        sample_context = {
            'customer_name': 'John Doe',
            'order_id': 'SO-2025-00001',
            'amount': '1,500.00',
            'company_name': 'ABC Company',
            'date': format_date(now(), 'dd/MM/yyyy'),
            'due_date': format_date(now(), 'dd/MM/yyyy'),
            'invoice_number': 'INV-2025-00001'
        }
        
        if context:
            sample_context.update(context)
        
        return self.render_template(sample_context)

@frappe.whitelist()
def get_template_preview(template_name, context=None):
    """Get template preview"""
    try:
        template = frappe.get_doc('Message Template', template_name)
        if context and isinstance(context, str):
            context = json.loads(context)
        return {
            'success': True,
            'preview': template.get_preview(context)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@frappe.whitelist()
def render_template(template_name, context):
    """Render template with context"""
    try:
        template = frappe.get_doc('Message Template', template_name)
        if isinstance(context, str):
            context = json.loads(context)
        return {
            'success': True,
            'rendered': template.render_template(context)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
