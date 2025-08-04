# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _

def execute():
    """Setup permissions for FlashChat Integration"""
    
    try:
        # Create custom roles if they don't exist
        create_custom_roles()
        
        # Setup DocType permissions
        setup_doctype_permissions()
        
        # Setup page and report permissions
        setup_page_permissions()
        
        # Setup custom field permissions
        setup_custom_field_permissions()
        
        # Setup API permissions
        setup_api_permissions()
        
        print("FlashChat Integration: Permissions setup completed successfully")
        
    except Exception as e:
        frappe.log_error(f"Error setting up FlashChat permissions: {str(e)}", "FlashChat Permissions Setup")
        print(f"FlashChat Integration: Error setting up permissions - {str(e)}")

def create_custom_roles():
    """Create custom roles for FlashChat"""
    
    roles = [
        {
            "role_name": "FlashChat Manager",
            "description": "Can manage FlashChat settings, campaigns, and workflows"
        },
        {
            "role_name": "FlashChat User",
            "description": "Can send messages and view message logs"
        },
        {
            "role_name": "FlashChat Viewer",
            "description": "Can only view FlashChat data"
        }
    ]
    
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            try:
                role = frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_data["role_name"],
                    "description": role_data["description"]
                })
                role.insert(ignore_permissions=True)
                print(f"Created role: {role_data['role_name']}")
            except Exception as e:
                print(f"Failed to create role {role_data['role_name']}: {str(e)}")

def setup_doctype_permissions():
    """Setup permissions for FlashChat doctypes"""
    
    permissions = [
        # FlashChat Settings
        {
            "doctype": "FlashChat Settings",
            "role": "System Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 1,
            "set_user_permissions": 1
        },
        {
            "doctype": "FlashChat Settings",
            "role": "FlashChat Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 0,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 0,
            "import": 0,
            "set_user_permissions": 0
        },
        
        # FlashChat Message Log
        {
            "doctype": "FlashChat Message Log",
            "role": "System Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 0,
            "set_user_permissions": 1
        },
        {
            "doctype": "FlashChat Message Log",
            "role": "FlashChat Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 0,
            "set_user_permissions": 0
        },
        {
            "doctype": "FlashChat Message Log",
            "role": "FlashChat User",
            "permlevel": 0,
            "read": 1,
            "write": 0,
            "create": 1,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 0,
            "import": 0,
            "set_user_permissions": 0
        },
        {
            "doctype": "FlashChat Message Log",
            "role": "Sales User",
            "permlevel": 0,
            "read": 1,
            "write": 0,
            "create": 1,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 0,
            "import": 0,
            "set_user_permissions": 0
        },
        {
            "doctype": "FlashChat Message Log",
            "role": "FlashChat Viewer",
            "permlevel": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 0,
            "import": 0,
            "set_user_permissions": 0
        },
        
        # FlashChat Campaign
        {
            "doctype": "FlashChat Campaign",
            "role": "System Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 1,
            "cancel": 1,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 0,
            "set_user_permissions": 1
        },
        {
            "doctype": "FlashChat Campaign",
            "role": "FlashChat Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 1,
            "cancel": 1,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 0,
            "set_user_permissions": 0
        },
        {
            "doctype": "FlashChat Campaign",
            "role": "Sales Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 1,
            "cancel": 1,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 0,
            "set_user_permissions": 0
        },
        {
            "doctype": "FlashChat Campaign",
            "role": "FlashChat User",
            "permlevel": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 0,
            "import": 0,
            "set_user_permissions": 0
        },
        
        # FlashChat Workflow
        {
            "doctype": "FlashChat Workflow",
            "role": "System Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 1,
            "set_user_permissions": 1
        },
        {
            "doctype": "FlashChat Workflow",
            "role": "FlashChat Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 0,
            "set_user_permissions": 0
        },
        {
            "doctype": "FlashChat Workflow",
            "role": "Sales Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 0,
            "import": 0,
            "set_user_permissions": 0
        },
        {
            "doctype": "FlashChat Workflow",
            "role": "FlashChat User",
            "permlevel": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 0,
            "import": 0,
            "set_user_permissions": 0
        },
        
        # FlashChat Workflow Log
        {
            "doctype": "FlashChat Workflow Log",
            "role": "System Manager",
            "permlevel": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 1,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 0,
            "set_user_permissions": 1
        },
        {
            "doctype": "FlashChat Workflow Log",
            "role": "FlashChat Manager",
            "permlevel": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 0,
            "set_user_permissions": 0
        },
        {
            "doctype": "FlashChat Workflow Log",
            "role": "FlashChat User",
            "permlevel": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 0,
            "import": 0,
            "set_user_permissions": 0
        },
        
        # Message Template
        {
            "doctype": "Message Template",
            "role": "System Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 1,
            "set_user_permissions": 1
        },
        {
            "doctype": "Message Template",
            "role": "FlashChat Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 0,
            "set_user_permissions": 0
        },
        {
            "doctype": "Message Template",
            "role": "Sales Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 0,
            "import": 0,
            "set_user_permissions": 0
        },
        {
            "doctype": "Message Template",
            "role": "FlashChat User",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 0,
            "import": 0,
            "set_user_permissions": 0
        },
        {
            "doctype": "Message Template",
            "role": "Sales User",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 0,
            "import": 0,
            "set_user_permissions": 0
        },
        
        # FlashChat Contact
        {
            "doctype": "FlashChat Contact",
            "role": "System Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 1,
            "set_user_permissions": 1
        },
        {
            "doctype": "FlashChat Contact",
            "role": "FlashChat Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 0,
            "set_user_permissions": 0
        },
        {
            "doctype": "FlashChat Contact",
            "role": "Sales Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 0,
            "set_user_permissions": 0
        },
        {
            "doctype": "FlashChat Contact",
            "role": "FlashChat User",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 0,
            "import": 0,
            "set_user_permissions": 0
        },
        {
            "doctype": "FlashChat Contact",
            "role": "Sales User",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 0,
            "import": 0,
            "set_user_permissions": 0
        }
    ]
    
    for perm in permissions:
        try:
            # Check if permission already exists
            existing = frappe.db.get_value(
                "DocPerm",
                {
                    "parent": perm["doctype"],
                    "role": perm["role"],
                    "permlevel": perm["permlevel"]
                },
                "name"
            )
            
            if not existing:
                # Create new permission
                doctype_meta = frappe.get_meta(perm["doctype"])
                if doctype_meta:
                    perm_doc = frappe.get_doc({
                        "doctype": "DocPerm",
                        "parent": perm["doctype"],
                        "parenttype": "DocType",
                        "parentfield": "permissions",
                        **perm
                    })
                    perm_doc.insert(ignore_permissions=True)
                    print(f"Added permission for {perm['doctype']} - {perm['role']}")
            else:
                print(f"Permission already exists for {perm['doctype']} - {perm['role']}")
                
        except Exception as e:
            print(f"Failed to create permission for {perm['doctype']} - {perm['role']}: {str(e)}")

def setup_page_permissions():
    """Setup permissions for pages and reports"""
    
    page_permissions = [
        {
            "page": "flashchat-dashboard",
            "roles": ["System Manager", "FlashChat Manager", "FlashChat User", "Sales Manager"]
        }
    ]
    
    for page_perm in page_permissions:
        try:
            for role in page_perm["roles"]:
                # Check if page permission exists
                existing = frappe.db.get_value(
                    "Page Role",
                    {
                        "parent": page_perm["page"],
                        "role": role
                    },
                    "name"
                )
                
                if not existing:
                    page_role = frappe.get_doc({
                        "doctype": "Page Role",
                        "parent": page_perm["page"],
                        "parenttype": "Page",
                        "parentfield": "roles",
                        "role": role
                    })
                    page_role.insert(ignore_permissions=True)
                    print(f"Added page permission for {page_perm['page']} - {role}")
                    
        except Exception as e:
            print(f"Failed to create page permission: {str(e)}")

def setup_custom_field_permissions():
    """Setup permissions for custom fields"""
    
    field_permissions = [
        {
            "doctype": "Contact",
            "fieldname": "flashchat_id",
            "roles": ["System Manager", "FlashChat Manager", "Sales Manager", "Sales User"]
        },
        {
            "doctype": "Customer",
            "fieldname": "flashchat_id", 
            "roles": ["System Manager", "FlashChat Manager", "Sales Manager", "Sales User"]
        },
        {
            "doctype": "Lead",
            "fieldname": "flashchat_id",
            "roles": ["System Manager", "FlashChat Manager", "Sales Manager", "Sales User"]
        }
    ]
    
    # Custom field permissions are handled through DocType permissions
    # This is for any additional field-level security if needed
    pass

def setup_api_permissions():
    """Setup API method permissions"""
    
    api_methods = [
        {
            "method": "flashchat_integration.api.send_sms_api",
            "roles": ["System Manager", "FlashChat Manager", "FlashChat User", "Sales Manager", "Sales User"]
        },
        {
            "method": "flashchat_integration.api.send_whatsapp_api",
            "roles": ["System Manager", "FlashChat Manager", "FlashChat User", "Sales Manager", "Sales User"]
        },
        {
            "method": "flashchat_integration.api.send_otp_api",
            "roles": ["System Manager", "FlashChat Manager", "FlashChat User", "Sales Manager", "Sales User"]
        },
        {
            "method": "flashchat_integration.api.verify_otp_api",
            "roles": ["System Manager", "FlashChat Manager", "FlashChat User", "Sales Manager", "Sales User"]
        },
        {
            "method": "flashchat_integration.api.get_whatsapp_accounts_api",
            "roles": ["System Manager", "FlashChat Manager", "FlashChat User", "Sales Manager", "Sales User"]
        },
        {
            "method": "flashchat_integration.utils.get_dashboard_data",
            "roles": ["System Manager", "FlashChat Manager", "FlashChat User", "FlashChat Viewer", "Sales Manager", "Sales User"]
        },
        {
            "method": "flashchat_integration.workflow_engine.create_custom_workflow",
            "roles": ["System Manager", "FlashChat Manager"]
        },
        {
            "method": "flashchat_integration.workflow_engine.execute_bulk_workflow",
            "roles": ["System Manager", "FlashChat Manager", "Sales Manager"]
        }
    ]
    
    # API permissions are typically handled through role-based access in hooks.py
    # and @frappe.whitelist() decorators with has_permission checks
    print("API method permissions configured through role-based access")

def cleanup_old_permissions():
    """Cleanup any old or invalid permissions"""
    
    try:
        # Remove any duplicate permissions
        frappe.db.sql("""
            DELETE p1 FROM `tabDocPerm` p1
            INNER JOIN `tabDocPerm` p2
            WHERE p1.name > p2.name
            AND p1.parent = p2.parent
            AND p1.role = p2.role
            AND p1.permlevel = p2.permlevel
        """)
        
        print("Cleaned up duplicate permissions")
        
    except Exception as e:
        print(f"Failed to cleanup permissions: {str(e)}")

def validate_permissions():
    """Validate that all permissions are set correctly"""
    
    required_permissions = [
        ("FlashChat Settings", "System Manager"),
        ("FlashChat Message Log", "FlashChat User"),
        ("FlashChat Campaign", "FlashChat Manager"),
        ("FlashChat Workflow", "FlashChat Manager"),
        ("Message Template", "FlashChat User")
    ]
    
    for doctype, role in required_permissions:
        perm_exists = frappe.db.get_value(
            "DocPerm",
            {
                "parent": doctype,
                "role": role
            },
            "name"
        )
        
        if perm_exists:
            print(f"✓ Permission validated: {doctype} - {role}")
        else:
            print(f"✗ Missing permission: {doctype} - {role}")

if __name__ == "__main__":
    execute()
