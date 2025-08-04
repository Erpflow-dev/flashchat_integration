## 13. flashchat_integration/boot.py

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

def boot_session(bootinfo):
    """Add FlashChat settings to boot info"""
    if frappe.session.user != "Guest":
        try:
            settings = frappe.get_single("FlashChat Settings")
            bootinfo.flashchat_settings = {
                "base_url": settings.base_url,
                "enable_sms": settings.enable_sms,
                "enable_whatsapp": settings.enable_whatsapp,
                "enable_otp": settings.enable_otp,
                "auto_sync_contacts": settings.auto_sync_contacts
            }
        except:
            bootinfo.flashchat_settings = {}