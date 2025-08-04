
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "flashchat_integration"
app_title = "FlashChat Integration"
app_publisher = "ERPFlow.dev"
app_description = "Complete SMS, WhatsApp, and OTP integration for ERPNext using FlashChat.xyz API with real-time messaging, automated notifications, and comprehensive tracking."
app_icon = "octicon octicon-comment"
app_color = "blue"
app_email = "mushleh.uddin.acca@gmail.com"
app_license = "mit"

# Required Apps
required_apps = ["frappe"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/flashchat_integration/css/flashchat.css"
app_include_js = "/assets/flashchat_integration/js/flashchat.js"

# include js, css files in header of web template
# web_include_css = "/assets/flashchat_integration/css/flashchat.css"
# web_include_js = "/assets/flashchat_integration/js/flashchat.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Contact": "public/js/contact_integration.js",
    "Customer": "public/js/contact_integration.js",
    "Lead": "public/js/contact_integration.js",
    "Sales Order": "public/js/contact_integration.js",
    "Delivery Note": "public/js/contact_integration.js",
    "Sales Invoice": "public/js/contact_integration.js",
    "Payment Entry": "public/js/contact_integration.js",
    "Quotation": "public/js/contact_integration.js",
    "FlashChat Workflow": "public/js/workflow.js",
    "FlashChat Campaign": "public/js/contact_integration.js"
}

doctype_list_js = {
    "Contact": "public/js/contact_integration.js",
    "Customer": "public/js/contact_integration.js",
    "Lead": "public/js/contact_integration.js",
    "FlashChat Message Log": "public/js/contact_integration.js",
    "FlashChat Workflow": "public/js/workflow.js"
}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "flashchat_integration.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

before_install = "flashchat_integration.install.before_install"
after_install = "flashchat_integration.install.after_install"
after_migrate = "flashchat_integration.install.after_migrate"

# Uninstallation
# --------------

before_uninstall = "flashchat_integration.install.before_uninstall"
after_uninstall = "flashchat_integration.install.after_uninstall"

# Desk Notifications
# -------------------
# See frappe.core.notifications.get_notification_config

notification_config = "flashchat_integration.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    # Global workflow hooks for all doctypes
    "*": {
        "after_insert": "flashchat_integration.doctype.flashchat_workflow.flashchat_workflow.execute_workflow_hooks",
        "after_save": "flashchat_integration.doctype.flashchat_workflow.flashchat_workflow.execute_workflow_hooks",
        "on_submit": "flashchat_integration.doctype.flashchat_workflow.flashchat_workflow.execute_workflow_hooks",
        "on_cancel": "flashchat_integration.doctype.flashchat_workflow.flashchat_workflow.execute_workflow_hooks",
        "on_update": "flashchat_integration.doctype.flashchat_workflow.flashchat_workflow.execute_workflow_hooks",
        "before_submit": "flashchat_integration.doctype.flashchat_workflow.flashchat_workflow.execute_workflow_hooks",
        "before_cancel": "flashchat_integration.doctype.flashchat_workflow.flashchat_workflow.execute_workflow_hooks",
        "on_trash": "flashchat_integration.doctype.flashchat_workflow.flashchat_workflow.execute_workflow_hooks"
    },
    
    # Contact specific events
    "Contact": {
        "after_insert": [
            "flashchat_integration.utils.sync_contact_to_flashchat",
            "flashchat_integration.utils.auto_create_flashchat_contact"
        ],
        "on_update": [
            "flashchat_integration.utils.sync_contact_to_flashchat",
            "flashchat_integration.utils.update_flashchat_contact"
        ],
        "validate": "flashchat_integration.utils.validate_contact_phone",
        "on_trash": "flashchat_integration.utils.cleanup_contact_data"
    },
    
    # Customer specific events
    "Customer": {
        "after_insert": [
            "flashchat_integration.utils.sync_customer_to_flashchat",
            "flashchat_integration.utils.create_customer_preferences"
        ],
        "on_update": "flashchat_integration.utils.sync_customer_to_flashchat",
        "validate": "flashchat_integration.utils.validate_customer_phone"
    },
    
    # Lead specific events
    "Lead": {
        "after_insert": [
            "flashchat_integration.utils.sync_lead_to_flashchat",
            "flashchat_integration.utils.auto_lead_followup"
        ],
        "on_update": "flashchat_integration.utils.sync_lead_to_flashchat",
        "validate": "flashchat_integration.utils.validate_lead_phone"
    },
    
    # Sales Order events
    "Sales Order": {
        "on_submit": [
            "flashchat_integration.utils.send_order_confirmation",
            "flashchat_integration.utils.create_delivery_reminders"
        ],
        "on_cancel": "flashchat_integration.utils.send_order_cancellation",
        "on_update": "flashchat_integration.utils.check_order_status_change"
    },
    
    # Delivery Note events
    "Delivery Note": {
        "on_submit": [
            "flashchat_integration.utils.send_delivery_notification",
            "flashchat_integration.utils.update_order_status"
        ],
        "on_cancel": "flashchat_integration.utils.handle_delivery_cancellation"
    },
    
    # Sales Invoice events
    "Sales Invoice": {
        "on_submit": [
            "flashchat_integration.utils.send_invoice_notification",
            "flashchat_integration.utils.schedule_payment_reminders"
        ],
        "on_cancel": "flashchat_integration.utils.cancel_payment_reminders",
        "on_update": "flashchat_integration.utils.check_payment_status"
    },
    
    # Payment Entry events
    "Payment Entry": {
        "on_submit": [
            "flashchat_integration.utils.send_payment_confirmation",
            "flashchat_integration.utils.update_invoice_status"
        ],
        "on_cancel": "flashchat_integration.utils.handle_payment_cancellation"
    },
    
    # Quotation events
    "Quotation": {
        "on_submit": [
            "flashchat_integration.utils.send_quotation_notification",
            "flashchat_integration.utils.schedule_quotation_followup"
        ],
        "on_update": "flashchat_integration.utils.check_quotation_status"
    },
    
    # Event/Appointment events
    "Event": {
        "after_insert": "flashchat_integration.utils.schedule_appointment_reminders",
        "on_update": "flashchat_integration.utils.update_appointment_reminders"
    },
    
    # User events for OTP and authentication
    "User": {
        "validate": "flashchat_integration.utils.validate_user_mobile",
        "after_insert": "flashchat_integration.utils.send_welcome_message"
    },
    
    # FlashChat specific doctypes
    "FlashChat Settings": {
        "on_update": [
            "flashchat_integration.utils.validate_api_connection",
            "flashchat_integration.utils.clear_cache"
        ]
    },
    
    "FlashChat Workflow": {
        "validate": "flashchat_integration.utils.validate_workflow_config",
        "on_update": "flashchat_integration.utils.update_workflow_hooks"
    },
    
    "FlashChat Campaign": {
        "on_submit": "flashchat_integration.utils.start_campaign_execution",
        "on_cancel": "flashchat_integration.utils.stop_campaign_execution"
    },
    
    "Message Template": {
        "validate": "flashchat_integration.utils.validate_template_syntax",
        "on_update": "flashchat_integration.utils.update_template_cache"
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    # Every 15 minutes
    "cron": {
        "*/15 * * * *": [
            "flashchat_integration.utils.process_pending_messages",
            "flashchat_integration.utils.sync_message_status"
        ],
        "*/30 * * * *": [
            "flashchat_integration.utils.check_rate_limits",
            "flashchat_integration.utils.process_scheduled_workflows"
        ]
    },
    
    # Hourly tasks
    "hourly": [
        "flashchat_integration.utils.sync_message_status",
        "flashchat_integration.utils.process_pending_campaigns",
        "flashchat_integration.utils.send_scheduled_reminders",
        "flashchat_integration.utils.process_drip_campaigns",
        "flashchat_integration.utils.check_webhook_health"
    ],
    
    # Longer hourly tasks
    "hourly_long": [
        "flashchat_integration.utils.sync_all_contacts",
        "flashchat_integration.utils.process_bulk_operations",
        "flashchat_integration.utils.generate_delivery_reports"
    ],
    
    # Daily tasks
    "daily": [
        "flashchat_integration.utils.cleanup_old_logs",
        "flashchat_integration.utils.cleanup_workflow_logs",
        "flashchat_integration.utils.send_daily_summary",
        "flashchat_integration.utils.check_overdue_invoices",
        "flashchat_integration.utils.process_anniversary_reminders",
        "flashchat_integration.utils.update_contact_preferences",
        "flashchat_integration.utils.validate_phone_numbers",
        "flashchat_integration.utils.archive_old_campaigns"
    ],
    
    # Daily long-running tasks
    "daily_long": [
        "flashchat_integration.utils.full_contact_sync",
        "flashchat_integration.utils.generate_analytics_data",
        "flashchat_integration.utils.backup_message_data"
    ],
    
    # Weekly tasks
    "weekly": [
        "flashchat_integration.utils.generate_weekly_report",
        "flashchat_integration.utils.generate_workflow_analytics",
        "flashchat_integration.utils.cleanup_duplicate_contacts",
        "flashchat_integration.utils.optimize_workflow_performance",
        "flashchat_integration.utils.validate_api_credentials"
    ],
    
    # Monthly tasks
    "monthly": [
        "flashchat_integration.utils.generate_monthly_analytics",
        "flashchat_integration.utils.archive_old_data",
        "flashchat_integration.utils.update_contact_segments",
        "flashchat_integration.utils.review_workflow_performance"
    ]
}

# Testing
# -------

before_tests = "flashchat_integration.tests.utils.before_tests"

# Overriding Methods
# ------------------------------

override_whitelisted_methods = {
    "frappe.core.doctype.communication.email.make": "flashchat_integration.utils.intercept_email_communication"
}

# Each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
    "Contact": "flashchat_integration.dashboard.get_contact_dashboard_data",
    "Customer": "flashchat_integration.dashboard.get_customer_dashboard_data",
    "Lead": "flashchat_integration.dashboard.get_lead_dashboard_data",
    "Sales Order": "flashchat_integration.dashboard.get_sales_order_dashboard_data"
}

# Exempt linked doctypes from being automatically cancelled
auto_cancel_exempted_doctypes = ["FlashChat Message Log", "FlashChat Workflow Log"]

# User Data Protection
# --------------------

user_data_fields = [
    {
        "doctype": "FlashChat Message Log",
        "filter_by": "phone_number",
        "redact_fields": ["message_content", "response_content"],
        "rename": None
    },
    {
        "doctype": "FlashChat Contact",
        "filter_by": "phone_number",
        "redact_fields": ["phone_number", "email", "address"],
        "rename": None
    },
    {
        "doctype": "FlashChat Workflow Log",
        "filter_by": "trigger_name",
        "redact_fields": ["details"],
        "rename": None
    }
]

# Authentication and authorization
# --------------------------------

auth_hooks = [
    "flashchat_integration.auth.validate_otp_login"
]

# Translation
# --------------------------------

# Make property setters available in the translation
translate_field_map = {
    "FlashChat Settings": ["base_url", "webhook_url"],
    "FlashChat Workflow": ["workflow_name", "custom_message"],
    "Message Template": ["template_name", "template_content"]
}

# Website Theme
# -------------

# Override link/website generator URL routing
website_route_rules = [
    {"from_route": "/flashchat/<path:app_path>", "to_route": "flashchat"},
    {"from_route": "/api/flashchat/<path:api_path>", "to_route": "flashchat_api"}
]

# Boot
# -----

# Boot session - after login
boot_session = "flashchat_integration.boot.boot_session"

# Jinja Environment
# -----------------

jinja = {
    "methods": [
        "flashchat_integration.utils.get_flashchat_settings",
        "flashchat_integration.utils.format_phone_number",
        "flashchat_integration.utils.get_message_templates",
        "flashchat_integration.utils.get_workflow_status"
    ],
    "filters": {
        "format_phone": "flashchat_integration.utils.format_phone_number",
        "render_template": "flashchat_integration.utils.render_message_template"
    }
}

# Error handlers
# ---------------

on_session_creation = [
    "flashchat_integration.utils.on_session_creation"
]

# Error logging
error_report_email = "mushleh.uddin.acca@gmail.com"

# API Rate Limiting
# -----------------

rate_limits = {
    "flashchat_integration.api.send_sms_api": (100, 3600),  # 100 per hour
    "flashchat_integration.api.send_whatsapp_api": (50, 3600),  # 50 per hour
    "flashchat_integration.api.send_otp_api": (20, 3600),  # 20 per hour
    "flashchat_integration.api.flashchat_webhook": (1000, 3600)  # 1000 per hour
}

# Email settings
# ---------------

email_append_to = ["FlashChat Message Log", "FlashChat Workflow Log"]

# Website settings
# ----------------

website_context = {
    "favicon": "/assets/flashchat_integration/images/flashchat-logo.png",
    "splash_image": "/assets/flashchat_integration/images/flashchat-logo.png"
}

# Global Search
# --------------

global_search_doctypes = {
    "FlashChat Message Log": {
        "search_field": "phone_number",
        "autocomplete_field": "message_content",
        "filters": [
            ["status", "=", "Delivered"]
        ]
    },
    "FlashChat Workflow": {
        "search_field": "workflow_name",
        "autocomplete_field": "workflow_name"
    },
    "Message Template": {
        "search_field": "template_name",
        "autocomplete_field": "template_content"
    }
}

# Standard portal pages for FlashChat
# ------------------------------------

standard_portal_menu_items = [
    {"title": "FlashChat Messages", "route": "/flashchat/messages", "reference_doctype": "FlashChat Message Log"},
    {"title": "Message Templates", "route": "/flashchat/templates", "reference_doctype": "Message Template"}
]

# Custom Fields
# -------------

fixtures = [
    "Custom Field",
    "Property Setter", 
    "Client Script",
    "Server Script",
    "Workflow",
    "Workflow State",
    "Workflow Action"
]

# Disable standard notifications for FlashChat doctypes
# ----------------------------------------------------

disable_email_notifications = [
    "FlashChat Message Log",
    "FlashChat Workflow Log"
]

# Custom Dashboards
# ------------------

dashboards = [
    {
        "module": "FlashChat Integration",
        "color": "blue",
        "icon": "octicon octicon-comment",
        "type": "module",
        "label": "FlashChat Integration"
    }
]

# Print Formats
# -------------

# Disable print for certain doctypes
print_settings = {
    "FlashChat Message Log": {"allow_print": 0},
    "FlashChat Workflow Log": {"allow_print": 0}
}

# Background Jobs
# ---------------

# Custom queues for FlashChat operations
background_jobs = {
    "flashchat_sms": {
        "queue": "short",
        "timeout": 300
    },
    "flashchat_whatsapp": {
        "queue": "short", 
        "timeout": 300
    },
    "flashchat_campaign": {
        "queue": "long",
        "timeout": 3600
    },
    "flashchat_workflow": {
        "queue": "default",
        "timeout": 600
    }
}

# Naming Series
# -------------

naming_series = {
    "FlashChat Message Log": "FCM-.YYYY.-.#####",
    "FlashChat Campaign": "FCC-.YYYY.-.#####", 
    "FlashChat Workflow Log": "FCW-.YYYY.-.#####",
    "FlashChat Contact": "FCON-.YYYY.-.#####"
}

# DocType Icons
# -------------

doctype_icons = {
    "FlashChat Settings": "fa fa-cog",
    "FlashChat Message Log": "fa fa-comment",
    "FlashChat Campaign": "fa fa-bullhorn",
    "FlashChat Workflow": "fa fa-flow-chart",
    "FlashChat Contact": "fa fa-address-book",
    "Message Template": "fa fa-file-text"
}

# Standard Doctypes with additional features
# ------------------------------------------

extend_bootinfo = [
    "flashchat_integration.boot.extend_bootinfo"
]

# System settings
# ---------------

# Cache settings
cache_drivers = {
    "flashchat_settings": "redis",
    "message_templates": "redis",
    "workflow_cache": "redis"
}

# Logging configuration
log_settings = {
    "loggers": {
        "flashchat_integration": {
            "level": "INFO",
            "propagate": True
        }
    }
}

# Development and Testing
# -----------------------

# Additional paths for development
develop_version = "1.0.0-dev"

# Test configurations
test_runner = "flashchat_integration.tests.runner.run_tests"
test_dependencies = ["frappe"]

# Maintenance and Health Checks
# ------------------------------

# Health check endpoints
health_check_functions = [
    "flashchat_integration.utils.check_api_connectivity",
    "flashchat_integration.utils.check_webhook_status",
    "flashchat_integration.utils.check_message_queue_health"
]

# Data migration helpers
migration_helpers = [
    "flashchat_integration.migration.migrate_old_messages",
    "flashchat_integration.migration.update_phone_formats"
]

# Performance monitoring
performance_metrics = [
    "flashchat_integration.metrics.track_message_delivery_time",
    "flashchat_integration.metrics.track_workflow_execution_time",
    "flashchat_integration.metrics.track_api_response_times"
]

# Regional Settings
# -----------------

# Country-specific settings
regional_settings = {
    "SA": {
        "phone_format": "+966-XX-XXX-XXXX",
        "working_hours": {"start": "08:00", "end": "17:00"},
        "weekend": ["Friday", "Saturday"]
    },
    "AE": {
        "phone_format": "+971-XX-XXX-XXXX", 
        "working_hours": {"start": "09:00", "end": "18:00"},
        "weekend": ["Friday", "Saturday"]
    },
    "US": {
        "phone_format": "+1-XXX-XXX-XXXX",
        "working_hours": {"start": "09:00", "end": "17:00"},
        "weekend": ["Saturday", "Sunday"]
    }
}

# Integrations with other apps
# ----------------------------

# ERPNext integrations
erpnext_integrations = [
    "flashchat_integration.integrations.erpnext.setup_sales_hooks",
    "flashchat_integration.integrations.erpnext.setup_crm_hooks"
]

# Third-party integrations
third_party_integrations = {
    "zapier": "flashchat_integration.integrations.zapier.handler",
    "slack": "flashchat_integration.integrations.slack.handler",
    "microsoft_teams": "flashchat_integration.integrations.teams.handler"
}

# Export configurations
# ---------------------

# Data export formats
export_formats = {
    "FlashChat Message Log": ["CSV", "Excel", "JSON"],
    "FlashChat Workflow Log": ["CSV", "Excel"],
    "FlashChat Campaign": ["PDF", "Excel"]
}

# Version compatibility
# ---------------------

# Compatible ERPNext versions
compatible_versions = [">=13.0.0", "<15.0.0"]

# Required Frappe version
required_frappe_version = ">=13.0.0"

# Feature flags
# -------------

feature_flags = {
    "enable_whatsapp_business_api": True,
    "enable_advanced_workflows": True,
    "enable_ai_message_suggestions": False,
    "enable_voice_messages": False,
    "enable_chatbot_integration": False
}

# Security settings
# -----------------

# Content Security Policy
csp_config = {
    "connect-src": ["'self'", "https://flashchat.xyz", "wss://flashchat.xyz"],
    "img-src": ["'self'", "data:", "https://flashchat.xyz"]
}

# CORS settings for API endpoints
cors_settings = {
    "allow_origin": ["https://flashchat.xyz"],
    "allow_methods": ["GET", "POST", "PUT", "DELETE"],
    "allow_headers": ["Content-Type", "Authorization"]
}

# Cleanup and maintenance
# -----------------------

# Automatic cleanup settings
cleanup_settings = {
    "message_logs_retention_days": 365,
    "workflow_logs_retention_days": 90,
    "failed_messages_retention_days": 30,
    "campaign_data_retention_days": 180
}

# Final configuration validation
# ------------------------------

def validate_app_config():
    """Validate app configuration on startup"""
    # This function will be called during app initialization
    pass

# App startup hooks
# -----------------

after_app_install = [
    "flashchat_integration.install.setup_default_data",
    "flashchat_integration.install.create_custom_roles",
    "flashchat_integration.install.setup_default_workflows"
]

# This ensures all features are properly configured and ready to use
startup_checks = [
    "flashchat_integration.utils.verify_api_connectivity",
    "flashchat_integration.utils.check_required_settings",
    "flashchat_integration.utils.validate_phone_number_formats"
]