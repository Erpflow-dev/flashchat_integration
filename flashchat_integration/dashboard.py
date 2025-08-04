
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _

def get_contact_dashboard_data(data):
    """Get dashboard data for Contact"""
    data['custom_cards'] = [
        {
            'label': _('FlashChat Messages'),
            'count': frappe.db.count('FlashChat Message Log', {
                'phone_number': data.get('mobile_no')
            }),
            'route': ['List', 'FlashChat Message Log', {'phone_number': data.get('mobile_no')}]
        }
    ]
    return data

def get_customer_dashboard_data(data):
    """Get dashboard data for Customer"""
    return get_contact_dashboard_data(data)

def get_lead_dashboard_data(data):
    """Get dashboard data for Lead"""
    return get_contact_dashboard_data(data)

def get_sales_order_dashboard_data(data):
    """Get dashboard data for Sales Order"""
    data['custom_cards'] = [
        {
            'label': _('Order Messages'),
            'count': frappe.db.count('FlashChat Message Log', {
                'reference_doctype': 'Sales Order',
                'reference_name': data.get('name')
            }),
            'route': ['List', 'FlashChat Message Log', {
                'reference_doctype': 'Sales Order',
                'reference_name': data.get('name')
            }]
        }
    ]
    return data
