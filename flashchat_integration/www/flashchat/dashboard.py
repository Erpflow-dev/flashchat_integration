
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _

def get_context(context):
    """Get context for FlashChat dashboard"""
    context.no_cache = 1
    
    # Check if user has permission
    if not frappe.has_permission("FlashChat Settings", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Get dashboard data
    context.dashboard_data = get_dashboard_data()
    
    return context

def get_dashboard_data():
    """Get dashboard statistics"""
    from flashchat_integration.utils import get_dashboard_data
    return get_dashboard_data()
