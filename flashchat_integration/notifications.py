# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _

def get_notification_config():
    """Get notification configuration for FlashChat"""
    return {
        "for_doctype": {
            "FlashChat Message Log": {
                "status": "Failed",
                "alert": _("FlashChat message failed to send")
            },
            "FlashChat Campaign": {
                "status": "Completed",
                "alert": _("FlashChat campaign completed")
            }
        }
    }